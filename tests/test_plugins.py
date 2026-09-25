import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('lock_plugins', ROOT / 'tools/lock_plugins.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PluginResolutionTests(unittest.TestCase):
    def test_transitive_dependencies_and_cycles(self):
        catalog = {
            'a': {'version': '1', 'requiredCore': '2.1', 'dependencies': [{'name': 'b', 'optional': False}, {'name': 'missing', 'optional': True}]},
            'b': {'version': '2', 'requiredCore': '2.1', 'dependencies': [{'name': 'a', 'optional': False}]},
        }
        self.assertEqual(module.resolve(catalog, ['a'], '2.2'), {'a': '1', 'b': '2'})

    def test_incompatible_core_is_rejected(self):
        with self.assertRaises(ValueError):
            module.resolve({'a': {'version': '1', 'requiredCore': '3.0', 'dependencies': []}}, ['a'], '2.568.3')

    def test_lock_has_all_roots_and_no_floating_versions(self):
        lines = (ROOT / 'controller/plugins.lock').read_text().splitlines()
        locked = dict(line.split(':') for line in lines)
        self.assertEqual(len(lines), len(locked))
        self.assertTrue(set((ROOT / 'controller/plugins.txt').read_text().splitlines()) <= locked.keys())
        self.assertTrue(all(version and version != 'latest' for version in locked.values()))
