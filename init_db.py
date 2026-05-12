import sqlite3
import json
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'battery_data.db')
METADATA_DIR = os.path.join(BASE_DIR, 'metadata')

def init_db():
   
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

   
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS components (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            manufacturer TEXT,
            model TEXT,
            specs TEXT,  -- We will store flexible specs (voltage, etc) as JSON text
            image_path TEXT,
            source_url TEXT
        )
    ''')

   
    files = [
    'cells.json', 
    'bms.json', 
    'connectors.json', 
    'cables.json',      
    'busbars.json',     
    'casings.json',    
    'hardware.json'    
]
    
    print("--- Migrating Data to SQL ---")
    for filename in files:
        filepath = os.path.join(METADATA_DIR, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                
            for item in data:
              
                specs = json.dumps({k:v for k,v in item.items() if k not in ['id', 'component_type', 'manufacturer', 'model', 'image_path', 'source_url']})
                
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO components (id, type, manufacturer, model, specs, image_path, source_url)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        item.get('id'),
                        item.get('component_type'),
                        item.get('manufacturer'),
                        item.get('model'),
                        specs,
                        item.get('image_path'),
                        item.get('source_url')
                    ))
                    print(f"✔ Imported {item.get('id')}")
                except Exception as e:
                    print(f"❌ Error importing {item.get('id')}: {e}")
        else:
            print(f"⚠️ File not found: {filename}")

    conn.commit()
    conn.close()
    print("--- Database Ready ---")

if __name__ == '__main__':
    init_db()