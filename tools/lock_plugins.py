#!/usr/bin/env python3
"""Resolve all required plugin dependencies from an explicit update-center snapshot."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def resolve(catalog, roots, core):
    selected = set()
    pending = list(roots)
    version = lambda value: tuple(int(part) for part in value.split('.'))
    while pending:
        name = pending.pop()
        if name in selected:
            continue
        plugin = catalog[name]
        if version(plugin['requiredCore']) > version(core):
            raise ValueError(f'{name} requires Jenkins {plugin["requiredCore"]}, selected {core}')
        selected.add(name)
        pending.extend(dep['name'] for dep in plugin['dependencies'] if not dep['optional'])
    return {name: catalog[name]['version'] for name in sorted(selected)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot', type=Path)
    args = parser.parse_args()
    roots = (ROOT / 'controller/plugins.txt').read_text().splitlines()
    plugins = resolve(json.loads(args.snapshot.read_text())['plugins'], roots, '2.568.3')
    (ROOT / 'controller/plugins.lock').write_text(''.join(f'{name}:{version}\n' for name, version in plugins.items()))


if __name__ == '__main__':
    main()
