#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build one offline interactive document; standard library only."""
import argparse
import json
from pathlib import Path


def safe_json(value):
    return json.dumps(value, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')


def build(data_path, output, world_path=None, attachment_path=None):
    skill = Path(__file__).resolve().parents[1]
    data_path, output = Path(data_path), Path(output)
    data = json.loads(data_path.read_text(encoding='utf-8'))
    import importlib.util
    spec = importlib.util.spec_from_file_location('city_validator', skill / 'scripts/validate_city.py')
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    result = validator.validate(data)
    if not result['passed']:
        raise ValueError('Invalid city data: ' + '; '.join(result['errors'][:8]))
    world = Path(world_path) if world_path else data_path.parent / 'worldbuilding.md'
    attachment = Path(attachment_path) if attachment_path else skill / 'references/gdc-user-summary.md'
    template = (skill / 'assets/atlas-template.html').read_text(encoding='utf-8')
    # Replace every token in a single pass: source text must not re-expand tokens.
    import re
    values = {'__CITY_DATA__': safe_json(data), '__WORLD_TEXT__': safe_json(world.read_text(encoding='utf-8') if world.exists() else 'Worldbuilding source not supplied.'), '__ATTACHMENT_TEXT__': safe_json(attachment.read_text(encoding='utf-8') if attachment.exists() else 'Attachment source not supplied.')}
    result = re.sub(r'__CITY_DATA__|__WORLD_TEXT__|__ATTACHMENT_TEXT__', lambda m: values[m.group()], template)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(result, encoding='utf-8')
    return len(result.encode('utf-8'))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('city_json')
    p.add_argument('--out', required=True)
    p.add_argument('--world')
    p.add_argument('--attachment')
    args = p.parse_args()
    size = build(args.city_json, args.out, args.world, args.attachment)
    print('Built %s (%d bytes), all document assets inline.' % (args.out, size))


if __name__ == '__main__':
    main()
