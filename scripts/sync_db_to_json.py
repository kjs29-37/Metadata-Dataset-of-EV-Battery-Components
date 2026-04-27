#!/usr/bin/env python3
"""
sync_db_to_json.py
Run from project root: python3 scripts/sync_db_to_json.py
Exports all database entries back to metadata JSON files.
"""
import sqlite3, json, os
from datetime import date

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(BASE_DIR, 'battery_data.db')
META_DIR = os.path.join(BASE_DIR, 'metadata')

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    types = [r[0] for r in conn.execute(
        "SELECT DISTINCT type FROM components ORDER BY type"
    ).fetchall()]

    for comp_type in types:
        rows = conn.execute(
            "SELECT * FROM components WHERE type = ? ORDER BY id",
            (comp_type,)
        ).fetchall()

        entries = []
        for row in rows:
            try:
                specs = json.loads(row['specs'] or '{}')
            except:
                specs = {}

            notes = specs.pop('notes', '') or specs.pop('note', '')
            license_val = specs.pop('license', 'Educational reference')

            entry = {
                "id":             row['id'],
                "component_type": row['type'],
                "manufacturer":   row['manufacturer'] or '',
                "model":          row['model'] or '',
                "image_path":     row['image_path'] or '',
                "source_url":     row['source_url'] or '',
                "license":        license_val,
                "notes":          notes,
            }
            entry.update(specs)
            entries.append(entry)

        out_path = os.path.join(META_DIR, f"{comp_type}.json")
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)
        print(f"  ✓ {comp_type}.json — {len(entries)} entries")

    conn.close()
    print(f"\n✅ Done — {len(types)} metadata files synced from database.")

if __name__ == '__main__':
    main()
