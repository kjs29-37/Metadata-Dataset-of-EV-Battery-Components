import json, sys, os
from jsonschema import validate, Draft202012Validator

ROOT = os.path.dirname(os.path.dirname(__file__))
SCHEMA = os.path.join(ROOT, "schema", "dataset_schema.json")
META_DIR = os.path.join(ROOT, "metadata")

def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def validate_file(fname, schema):
    data = load(os.path.join(META_DIR, fname))
    ids = set()
    errors = []
    for i, item in enumerate(data):
        for e in Draft202012Validator(schema).iter_errors(item):
            errors.append(f"{fname}[{i}] -> {e.message}")
        _id = item.get("id")
        if _id in ids:
            errors.append(f"{fname}[{i}] -> duplicate id: {_id}")
        ids.add(_id)
        ipath = os.path.join(ROOT, item.get("image_path",""))
        if not os.path.exists(ipath):
            errors.append(f"{fname}[{i}] -> missing image: {item.get('image_path')}")
    return errors

def main():
    schema = load(SCHEMA)
    all_files = ["cells.json", "connectors.json", "bms.json"]
    all_errors = []
    for f in all_files:
        if not os.path.exists(os.path.join(META_DIR, f)):
            print(f"skip: {f} not found"); continue
        all_errors += validate_file(f, schema)
    if all_errors:
        print("❌ Validation failed:")
        for e in all_errors:
            print(" -", e)
        sys.exit(1)
    print("✅ All metadata valid and images found.")

if __name__ == "__main__":
    main()
