#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the bundled JSON Schema subset and city planning invariants, offline."""
import argparse
import json
import math
import re
from pathlib import Path


def schema_errors(value, rule, schema, path='$'):
    errors = []
    if '$ref' in rule:
        target = schema
        for part in rule['$ref'][2:].split('/'):
            target = target[part]
        return schema_errors(value, target, schema, path)
    types = rule.get('type', [])
    types = [types] if isinstance(types, str) else types
    checks = {'object': lambda x: isinstance(x, dict), 'array': lambda x: isinstance(x, list), 'string': lambda x: isinstance(x, str), 'number': lambda x: isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x), 'integer': lambda x: isinstance(x, int) and not isinstance(x, bool), 'null': lambda x: x is None, 'boolean': lambda x: isinstance(x, bool)}
    if types and not any(checks[t](value) for t in types):
        return [path + ': invalid type, expected ' + str(types)]
    if 'const' in rule and value != rule['const']:
        errors.append(path + ': const mismatch')
    if 'enum' in rule and value not in rule['enum']:
        errors.append(path + ': enum mismatch')
    if isinstance(value, dict):
        props = rule.get('properties', {})
        for k in rule.get('required', []):
            if k not in value:
                errors.append(path + ': missing ' + k)
        for k, v in value.items():
            if k in props:
                errors += schema_errors(v, props[k], schema, path + '.' + k)
            elif rule.get('additionalProperties') is False:
                errors.append(path + ': unexpected ' + k)
    if isinstance(value, list):
        if len(value) < rule.get('minItems', 0) or len(value) > rule.get('maxItems', float('inf')):
            errors.append(path + ': array length out of bounds')
        if rule.get('uniqueItems') and len({json.dumps(x, sort_keys=True) for x in value}) != len(value):
            errors.append(path + ': duplicate array items')
        for i, v in enumerate(value):
            errors += schema_errors(v, rule.get('items', {}), schema, path + '[' + str(i) + ']')
    if isinstance(value, str) and 'pattern' in rule and re.search(rule['pattern'], value) is None:
        errors.append(path + ': string pattern mismatch')
    if isinstance(value, str) and len(value.strip()) < rule.get('minLength', 0):
        errors.append(path + ': empty or short string')
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if not math.isfinite(value) or value < rule.get('minimum', -float('inf')) or value > rule.get('maximum', float('inf')):
            errors.append(path + ': number out of bounds')
    return errors


def point_in(p, polygon):
    x, y = p
    inside = False
    for a, b in zip(polygon, polygon[1:] + polygon[:1]):
        cross = (b[0]-a[0])*(y-a[1])-(b[1]-a[1])*(x-a[0])
        if abs(cross) < 1e-7 and min(a[0], b[0])-1e-7 <= x <= max(a[0], b[0])+1e-7 and min(a[1], b[1])-1e-7 <= y <= max(a[1], b[1])+1e-7:
            return True
        if (a[1] > y) != (b[1] > y) and x < (b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:
            inside = not inside
    return inside


def active(item, era):
    return item['since'] <= era and (item.get('retired') is None or item['retired'] > era)


def route(data, start, end, era, mode='walk', permit=False, closed=''):
    import heapq
    nodes = {n['id']: n for n in data['nodes'] if active(n, era)}
    if start not in nodes or end not in nodes:
        return None
    graph = {n: [] for n in nodes}
    speed = 8 if mode == 'bike' else 4.5
    for r in data['roads']:
        if active(r, era) and mode in r['modes'] and r['id'] != closed and (not r['permit'] or permit):
            if r['fromNodeId'] in graph and r['toNodeId'] in graph:
                t = r['lengthM']/speed+r['delaySeconds']
                graph[r['fromNodeId']].append((r['toNodeId'], t, r['id']))
                graph[r['toNodeId']].append((r['fromNodeId'], t, r['id']))
    todo, best = [(0, start, [])], {start: 0}
    while todo:
        seconds, u, roads = heapq.heappop(todo)
        if seconds > best[u]:
            continue
        if u == end:
            return {'seconds': seconds, 'roadIds': roads}
        for v, cost, rid in graph[u]:
            score = seconds + cost
            if score < best.get(v, float('inf')):
                best[v] = score
                heapq.heappush(todo, (score, v, roads+[rid]))
    return None


def validate(data, schema_path=None):
    schema_path = schema_path or Path(__file__).resolve().parents[1]/'references/city.schema.json'
    schema = json.loads(Path(schema_path).read_text(encoding='utf-8'))
    errors = schema_errors(data, schema, schema)
    if errors:
        return {'passed': False, 'errors': errors, 'warnings': [], 'checks': 0}
    warnings, checks = [], 1
    keys = ['sources', 'claims', 'eras', 'factions', 'events', 'districts', 'buildings', 'pois', 'nodes', 'roads', 'transit', 'experiments']
    idx = {k: {x['id']: x for x in data[k]} for k in keys}
    all_ids = [x['id'] for k in keys for x in data[k]]
    if len(set(all_ids)) != len(all_ids):
        errors.append('IDs must be globally unique')
    for key in keys:
        if len(idx[key]) != len(data[key]):
            errors.append('duplicate ID in ' + key)
    refs = {'claimIds':'claims','sourceIds':'sources','referenceIds':'sources','eventIds':'events','dependsOn':'events','premises':'claims','districtIds':'districts','affectedDistrictIds':'districts','factionId':'factions','districtId':'districts','primaryRoadId':'roads','roadIds':'roads','nodeIds':'nodes','nodeId':'nodes','fromNodeId':'nodes','toNodeId':'nodes'}
    for key in keys:
        for item in data[key]:
            for field, target in refs.items():
                if field in item:
                    values = item[field] if isinstance(item[field], list) else [item[field]]
                    for value in values:
                        if value not in idx[target]:
                            errors.append('%s.%s: unknown %s' % (item['id'], field, value))
            checks += 1
    if errors:
        return {'passed': False, 'errors': errors, 'warnings': warnings, 'checks': checks}
    eras = data['eras']
    if [e['index'] for e in eras] != list(range(len(eras))) or any(b['year'] <= a['year'] for a, b in zip(eras, eras[1:])):
        errors.append('eras must have consecutive indexes and increasing years')
    def acyclic(key, field):
        visiting, done = set(), set()
        def visit(id):
            if id in visiting:
                errors.append(key + ': dependency cycle at ' + id)
                return
            if id in done:
                return
            visiting.add(id)
            for dep in idx[key][id].get(field, []):
                visit(dep)
            visiting.remove(id)
            done.add(id)
        for id in idx[key]:
            visit(id)
    acyclic('events', 'dependsOn')
    acyclic('claims', 'premises')
    for c in data['claims']:
        if c['kind'] == 'inference' and (not c['premises'] or not c['reasoning'].strip()):
            errors.append(c['id'] + ': inference requires premises and reasoning')
        if c['kind'] == 'measurement' and not c.get('measurementEvidence'):
            errors.append(c['id'] + ': measurement requires raw evidence location')
    for ev in data['events']:
        for dep in ev['dependsOn']:
            if idx['events'][dep]['era'] >= ev['era']:
                errors.append(ev['id'] + ': upstream event is not earlier')
    nera = len(eras)
    for key in ['events','districts','pois','nodes','roads','transit','buildings']:
        for x in data[key]:
            epoch = x.get('since', x.get('era'))
            if epoch >= nera:
                errors.append(x['id'] + ': era out of range')
    for r in data['roads']:
        a, b = idx['nodes'][r['fromNodeId']], idx['nodes'][r['toNodeId']]
        if a['since'] > r['since'] or b['since'] > r['since']:
            errors.append(r['id'] + ': road predates endpoint')
        if r['retired'] is not None and (r['retired'] <= r['since'] or r['retired'] >= nera):
            errors.append(r['id'] + ': invalid retirement')
        if math.dist(r['points'][0], [a['x'],a['y']]) > .01 or math.dist(r['points'][-1], [b['x'],b['y']]) > .01:
            errors.append(r['id'] + ': geometry endpoints do not match nodes')
        calc = sum(math.dist(x,y) for x,y in zip(r['points'],r['points'][1:]))*data['coordinateSystem']['metersPerUnit']
        if abs(calc-r['lengthM']) > .11:
            errors.append(r['id'] + ': length does not match scaled polyline')
    for key in ['pois','buildings']:
        for x in data[key]:
            d = idx['districts'][x['districtId']]
            if x['since'] < d['since']:
                errors.append(x['id'] + ': object predates district')
            if key == 'pois':
                node = idx['nodes'][x['nodeId']]
                if x['since'] < node['since'] or not point_in([node['x'],node['y']],d['polygon']):
                    errors.append(x['id'] + ': POI node is not available or outside district')
    polygon_area = 0
    for d in data['districts']:
        polygon = d['polygon']
        area = abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(polygon,polygon[1:]+polygon[:1])))/2
        polygon_area += area
        if area <= 0 or not point_in(d['labelPoint'],polygon):
            errors.append(d['id'] + ': degenerate polygon or label outside')
        if abs(d['densityPerKm2']-d['population']/d['areaKm2']) > 1:
            errors.append(d['id'] + ': population density inconsistent')
    area_km2=polygon_area*data['coordinateSystem']['metersPerUnit']**2/1e6
    if abs(data['brief']['playableAreaKm2']-area_km2) > .001:
        errors.append('playable area inconsistent with polygons and scale')
    if sum(d['population'] for d in data['districts']) != data['brief']['population']:
        errors.append('city population does not equal district total')
    if abs(sum(d['areaKm2'] for d in data['districts'])-data['brief']['settingAreaKm2']) > .01:
        errors.append('setting area does not equal district total')
    for n in data['nodes']:
        if n['x'] > data['coordinateSystem']['width'] or n['y'] > data['coordinateSystem']['height']:
            errors.append(n['id'] + ': outside coordinate bounds')
    for e in eras:
        current = [n['id'] for n in data['nodes'] if active(n,e['index'])]
        if current:
            for target in current[1:]:
                if route(data,current[0],target,e['index']) is None:
                    errors.append('%s: walking graph disconnected at %s' % (e['id'],target))
        for n in current:
            degree = sum(n in (r['fromNodeId'],r['toNodeId']) for r in data['roads'] if active(r,e['index']))
            if degree > 4:
                warnings.append('%s/%s: degree %d exceeds demo traffic budget; engine validation required' % (e['id'],n,degree))
    for ex in data['experiments']:
        if ex['status'] == 'passed' and not ex['observations']:
            errors.append(ex['id'] + ': passed experiment has no observations')
    if data['review']['productionGate'] == 'approved':
        if any(g['status'] not in ['passed','accepted_risk'] for g in data['review']['gates']):
            errors.append('production approval contains unresolved gates')
        if any(e['status'] == 'not_run' for e in data['experiments']):
            errors.append('production approved while experiments are not run')
    checks += 10 + len(data['roads']) + len(data['pois']) + len(data['districts'])
    warnings.append('Engine, player-view, vertical traversal, traffic AI and platform tests are not verified by this validator.')
    return {'passed': not errors, 'errors': errors, 'warnings': sorted(set(warnings)), 'checks': checks, 'counts': {k:len(data[k]) for k in keys}, 'playableAreaKm2Calculated':round(area_km2,6)}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('city_json')
    p.add_argument('--report')
    args=p.parse_args()
    try:
        result=validate(json.loads(Path(args.city_json).read_text(encoding='utf-8')))
    except (ValueError, KeyError, TypeError) as exc:
        result={'passed':False,'errors':[str(exc)]}
    result['cityFile']=str(args.city_json)
    text=json.dumps(result,ensure_ascii=False,indent=2)
    if args.report:
        Path(args.report).write_text(text+'\n',encoding='utf-8')
    print(text)
    raise SystemExit(0 if result['passed'] else 1)


if __name__=='__main__':
    main()
