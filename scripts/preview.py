import json, os

ROOT = os.path.dirname(os.path.dirname(__file__))
META_DIR = os.path.join(ROOT, "metadata")

def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def list_entries():
    meta_files = ["cells.json", "connectors.json", "bms.json"]
    for file_name in meta_files:
        path = os.path.join(META_DIR, file_name)
        if not os.path.exists(path):
            print(f"⚠️  Missing metadata file: {file_name}")
            continue

        data = load_json(path)
        print(f"\n=== {file_name} ({len(data)} items) ===")
        if not data:
            print("  (no entries yet)")
            continue

        for item in data:
            comp_id = item.get("id", "N/A")
            manufacturer = item.get("manufacturer", "Unknown")
            model = item.get("model", "—")
            print(f" - {comp_id:15} | {manufacturer:20} | {model}")

if __name__ == "__main__":
    list_entries()
