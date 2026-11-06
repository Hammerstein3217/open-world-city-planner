#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regression tests for meaningful city invariants. Standard library only."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('city_validator',ROOT/'skills/open-world-city-planner/scripts/validate_city.py')
V=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)
DATA=json.loads((ROOT/'demo/city.json').read_text(encoding='utf-8'))

class CityTests(unittest.TestCase):
    def broken(self, fn, expected):
        d=copy.deepcopy(DATA)
        fn(d)
        result=V.validate(d)
        self.assertFalse(result['passed'])
        self.assertTrue(any(expected in e for e in result['errors']),result['errors'])
    def test_sample(self):
        self.assertTrue(V.validate(DATA)['passed'])
    def test_dangling_claim(self):
        self.broken(lambda d:d['districts'][0]['claimIds'].append('MISSING'),'unknown MISSING')
    def test_future_cause(self):
        self.broken(lambda d:d['events'][0]['dependsOn'].append('E05'),'upstream event is not earlier')
    def test_inference_cycle(self):
        self.broken(lambda d:d['claims'][-1]['premises'].append('I03'),'dependency cycle')
    def test_empty_inference(self):
        self.broken(lambda d:d['claims'][-1].update(premises=[]),'inference requires')
    def test_fake_measurement(self):
        self.broken(lambda d:d['claims'][-1].update(kind='measurement'),'measurement requires')
    def test_early_road(self):
        self.broken(lambda d:d['roads'][1].update(since=0),'road predates endpoint')
    def test_length(self):
        self.broken(lambda d:d['roads'][0].update(lengthM=9999),'length does not match')
    def test_outside_poi(self):
        self.broken(lambda d:d['pois'][0].update(districtId='D06'),'POI node is not available or outside')
    def test_density(self):
        self.broken(lambda d:d['districts'][0].update(densityPerKm2=1),'density inconsistent')
    def test_false_experiment_pass(self):
        self.broken(lambda d:d['experiments'][0].update(status='passed'),'passed experiment has no observations')
    def test_false_production_pass(self):
        self.broken(lambda d:d['review'].update(productionGate='approved'),'production approval')
    def test_schema_missing(self):
        self.broken(lambda d:d['pois'][0].pop('cause'),'missing cause')
    def test_route_restricted_modes(self):
        self.assertIsNone(V.route(DATA,'N01','N09',4,'bike'))
        self.assertIsNotNone(V.route(DATA,'N01','N09',4,'walk'))
    def test_reroute_and_permission(self):
        a=V.route(DATA,'N02','N03',4)
        b=V.route(DATA,'N02','N03',4,closed='R02')
        self.assertIn('R02',a['roadIds'])
        self.assertNotIn('R02',b['roadIds'])
        self.assertGreater(b['seconds'],a['seconds'])
        without=V.route(DATA,'N08','N05',4)
        with_permit=V.route(DATA,'N08','N05',4,permit=True)
        self.assertNotIn('R08',without['roadIds'])
        self.assertIn('R08',with_permit['roadIds'])
        self.assertLess(with_permit['seconds'],without['seconds'])
    def test_era_and_zero_distance(self):
        self.assertIsNone(V.route(DATA,'N01','N09',0))
        self.assertEqual(V.route(DATA,'N01','N01',4)['seconds'],0)
        self.assertTrue(V.active(next(r for r in DATA['roads'] if r['id']=='R17'),1))
        self.assertFalse(V.active(next(r for r in DATA['roads'] if r['id']=='R17'),3))
    def test_safe_inline_payload(self):
        spec=importlib.util.spec_from_file_location('builder',ROOT/'skills/open-world-city-planner/scripts/build_demo.py')
        b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
        payload='</script><script>alert(1)</script>&\u2028'
        encoded=b.safe_json(payload)
        self.assertNotIn('</script>',encoded)
        self.assertEqual(json.loads(encoded),payload)

if __name__=='__main__':
    unittest.main(verbosity=2)
