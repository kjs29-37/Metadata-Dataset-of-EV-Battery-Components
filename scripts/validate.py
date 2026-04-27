#!/usr/bin/env python3
"""
validate.py — Run from project root: python3 scripts/validate.py
Validates all JSON metadata files against dataset_schema.json
"""
import json, os, sys

ROOT        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_PATH = os.path.join(ROOT, 'schema', 'dataset_schema.json')
META_DIR    = os.path.join(ROOT, 'metadata')

VALID_TYPES = ['cells','bms','connectors','cables','busbars','casings','hardware']

def validate_file(filepath):
    errors = []
    filename = os.path.basename(filepath)
    with open(filepath, encoding='utf-8') as f:
        try:
            entries = json.load(f)
        except json.JSONDecodeError as e:
            return [f"{filename} -> JSON parse error: {e}"]

    if not isinstance(entries, list):
        entries = [entries]

    for i, item in enumerate(entries):
        ref = f"{filename}[{i}]"
        for field in ['id', 'component_type', 'manufacturer']:
            if not item.get(field):
                errors.append(f"{ref} -> missing required field: '{field}'")
        ct = item.get('component_type','')
        if ct and ct not in VALID_TYPES:
            errors.append(f"{ref} -> invalid component_type: '{ct}'")
        image_path = item.get('image_path')
        if image_path and isinstance(image_path, str):
            full = os.path.join(ROOT, 'static', image_path)
            if not os.path.exists(full):
                errors.append(f"{ref} -> missing image: {image_path}")
    return errors

def main():
    print("CellBase Dataset Validator")
    print("=" * 50)
    meta_files = sorted([f for f in os.listdir(META_DIR) if f.endswith('.json')])
    all_errors = []
    total = 0
    for filename in meta_files:
        filepath = os.path.join(META_DIR, filename)
        with open(filepath, encoding='utf-8') as f:
            try:
                entries = json.load(f)
                total += len(entries) if isinstance(entries, list) else 1
            except:
                pass
        all_errors += validate_file(filepath)
    print(f"✓ Validated {total} entries across {len(meta_files)} files")
    print("=" * 50)
    if not all_errors:
        print(f"✅ All validations PASSED — 0 errors")
        print(f"   {total} entries are schema-compliant")
    else:
        print(f"❌ {len(all_errors)} error(s) found:")
        for e in all_errors:
            print(f"   - {e}")
    print("=" * 50)

if __name__ == '__main__':
    main()