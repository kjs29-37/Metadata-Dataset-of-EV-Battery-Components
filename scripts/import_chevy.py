

import json
import os
import sqlite3
from datetime import date

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(BASE_DIR, 'battery_data.db')
META_DIR = os.path.join(BASE_DIR, 'metadata')


META_FILES = [
    'cells.json',
    'bms.json',
    'busbars.json',
    'cables.json',
    'casings.json',
    'connectors.json',
    'hardware.json',
]

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def flatten_specs(entry):
    """Extract non-core fields as a JSON specs blob."""
    core_fields = {'id', 'component_type', 'manufacturer', 'model',
                   'image_path', 'source_url', 'license', 'notes', 'vehicle_models'}
    specs = {k: v for k, v in entry.items() if k not in core_fields}
    return json.dumps(specs)

def import_entry(conn, entry):
    comp_id      = entry.get('id')
    comp_type    = entry.get('component_type')
    manufacturer = entry.get('manufacturer', '')
    model        = entry.get('model', '')
    image_path   = entry.get('image_path', '')
    source_url   = entry.get('source_url', 'N/A')
    specs        = flatten_specs(entry)

   
    existing = conn.execute(
        "SELECT id FROM components WHERE id = ?", (comp_id,)
    ).fetchone()

    if existing:
        # UPDATE existing record
        conn.execute("""
            UPDATE components
            SET type=?, manufacturer=?, model=?, image_path=?, source_url=?, specs=?
            WHERE id=?
        """, (comp_type, manufacturer, model, image_path, source_url, specs, comp_id))
        print(f"  ↻ Updated : {comp_id}")
    else:
        # INSERT new record
        conn.execute("""
            INSERT INTO components (id, type, manufacturer, model, image_path, source_url, specs)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (comp_id, comp_type, manufacturer, model, image_path, source_url, specs))
        print(f"  ✓ Inserted: {comp_id}")

def main():
    conn = get_db()

   
    try:
        conn.execute("ALTER TABLE components ADD COLUMN source_url TEXT")
        print("Added source_url column.")
    except Exception:
        pass  # Already exists

    total_inserted = 0
    total_updated  = 0

    for fname in META_FILES:
        fpath = os.path.join(META_DIR, fname)
        if not os.path.exists(fpath):
            print(f"\n⚠️  Skipping (not found): {fname}")
            continue

        with open(fpath, 'r', encoding='utf-8') as f:
            entries = json.load(f)

        print(f"\n── {fname} ({len(entries)} entries) ──")
        for entry in entries:
            import_entry(conn, entry)

    conn.commit()
    conn.close()

   
    print("\n✅ Import complete. All metadata synced to battery_data.db")
    print("   Run your Flask app and check /browse to verify.\n")

if __name__ == '__main__':
    main()
