#!/usr/bin/env python3
"""
update_vw_id4.py
Run from project root: python scripts/update_vw_id4.py
Updates all VW ID.4 entries with correct image paths and source URLs.
"""
import sqlite3, json, os
from datetime import date

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(BASE_DIR, 'battery_data.db')

VW_UPDATES = [
    {
        "id":         "vw_id4_bms_0001",
        "model":      "Volkswagen ID.4 / ID.3 Battery Management System (MEB Platform)",
        "image_path": "images/bms/ID4_bms.webp",
        "source_url": "https://www.edn.com/under-the-hood-vws-id-3-electric-vehicle/",
        "specs": json.dumps({
            "features": [
                "Cell voltage monitoring",
                "Thermal management control",
                "State of health (SOH) estimation",
                "CAN bus communication with vehicle ECU",
                "Shared across VW Group MEB vehicles"
            ],
            "vehicle_models": ["Volkswagen ID.4", "Volkswagen ID.3", "Audi Q4 e-tron"],
            "notes": "MEB platform Battery Management System as detailed in EDN teardown of the VW ID.3. Manages the 77kWh pack across 12 modules. Architecture is shared across VW Group MEB platform vehicles including the ID.4, ID.3, and Audi Q4 e-tron.",
            "date_added": date.today().isoformat()
        })
    },
    {
        "id":         "vw_id4_cell_0001",
        "model":      "Volkswagen ID.4 NMC Prismatic Cell (Samsung SDI)",
        "image_path": "images/cells/ID4_cell.png",
        "source_url": "https://www.youtube.com/watch?v=uP-lOsd4cVY",
        "specs": json.dumps({
            "chemistry":      "NMC (Nickel Manganese Cobalt)",
            "format":         "Prismatic",
            "voltage_V":      3.68,
            "capacity_mAh":   78000,
            "vehicle_models": ["Volkswagen ID.4 Pro", "Volkswagen ID.4 GTX"],
            "notes": "Samsung SDI prismatic NMC cells used in the MEB platform 77kWh battery pack. The pack contains 288 cells across 12 modules. Reference from EV teardown video showing cell-level disassembly.",
            "date_added": date.today().isoformat()
        })
    },
    {
        "id":         "vw_id4_busbar_0001",
        "model":      "Volkswagen ID.4 MEB Module Interconnect Busbar",
        "image_path": "images/busbars/ID4_busbar.png",
        "source_url": "https://www.youtube.com/watch?v=uP-lOsd4cVY",
        "specs": json.dumps({
            "material":        "Aluminium",
            "voltage_rating_V": 400,
            "current_rating_A": 250,
            "vehicle_models":  ["Volkswagen ID.4", "Volkswagen ID.3"],
            "notes": "Aluminium busbar connecting prismatic cell modules within the MEB 77kWh battery pack. Lightweight aluminium chosen over copper for weight reduction. Visible in teardown video showing module-level disassembly.",
            "date_added": date.today().isoformat()
        })
    },
    {
        "id":         "vw_id4_casing_0001",
        "model":      "Volkswagen ID.4 MEB Battery Pack Enclosure",
        "image_path": "images/casings/ID4_casing.png",
        "source_url": "https://www.youtube.com/watch?v=XpXuZYsyRcw",
        "specs": json.dumps({
            "material":        "Aluminium extrusion / Steel reinforcement",
            "vehicle_models":  ["Volkswagen ID.4", "Volkswagen ID.3"],
            "notes": "Flat underbody skateboard enclosure for the MEB 77kWh battery pack. Aluminium extrusion frame with steel crash reinforcements and integrated liquid cooling channels. The flat pack lowers the vehicle centre of gravity and enables the spacious interior of the ID.4.",
            "date_added": date.today().isoformat()
        })
    },
    {
        "id":         "vw_id4_connector_0001",
        "model":      "Volkswagen ID.4 MEB HV Connector & Service Disconnect",
        "image_path": "images/connectors/ID4_Connector.jpg",
        "source_url": "https://www.batterydesign.net/volkswagen-meb-battery-pack-id-family/",
        "specs": json.dumps({
            "connector_type":  "HV service disconnect / module connector",
            "voltage_rating_V": 400,
            "current_rating_A": 300,
            "vehicle_models":  ["Volkswagen ID.4", "Volkswagen ID.3", "Audi Q4 e-tron"],
            "notes": "High-voltage connector and service disconnect for the MEB battery pack as documented by Battery Design. Orange housing identifies HV circuit. Includes HVIL (High Voltage Interlock Loop) for safe servicing.",
            "date_added": date.today().isoformat()
        })
    },
    {
        "id":         "vw_id4_cable_0001",
        "model":      "Volkswagen ID.4 MEB High Voltage Orange Cable",
        "image_path": "images/cables/ID4_cable.jpg",
        "source_url": "https://www.ebay.co.uk/itm/188162241564",
        "specs": json.dumps({
            "conductor_material": "Stranded Copper",
            "insulation":         "Cross-linked Polyethylene (Orange)",
            "voltage_rating":     "400V DC",
            "vehicle_models":     ["Volkswagen ID.4", "Volkswagen ID.3"],
            "notes": "High-voltage orange interconnect cable for the MEB platform. Connects battery pack to power electronics module. Orange insulation is the industry-standard EV safety colour for HV systems, alerting first responders to high-voltage risk.",
            "date_added": date.today().isoformat()
        })
    },
    {
        "id":         "vw_id4_hardware_0001",
        "model":      "Volkswagen ID.4 MEB Battery Pack Mounting Bolts & Brackets",
        "image_path": "images/hardware/ID4_bolts.webp",
        "source_url": "https://www.batterydesign.net/volkswagen-meb-battery-pack-id-family/",
        "specs": json.dumps({
            "part_type":       "nut/bolt/bracket",
            "material":        "High-strength Steel",
            "vehicle_models":  ["Volkswagen ID.4", "Volkswagen ID.3"],
            "notes": "Structural mounting hardware securing the MEB skateboard battery pack to the vehicle chassis underbody. Documented in Battery Design's MEB pack analysis. High-strength steel fasteners distribute pack weight evenly across reinforced chassis mounting points.",
            "date_added": date.today().isoformat()
        })
    },
]

def main():
    conn = sqlite3.connect(DB_PATH)

    updated = 0
    for entry in VW_UPDATES:
        exists = conn.execute(
            "SELECT id FROM components WHERE id = ?", (entry['id'],)
        ).fetchone()

        if exists:
            conn.execute("""
                UPDATE components
                SET model=?, image_path=?, source_url=?, specs=?
                WHERE id=?
            """, (entry['model'], entry['image_path'],
                  entry['source_url'], entry['specs'], entry['id']))
            print(f"  ✓ Updated: {entry['id']}")
            updated += 1
        else:
            print(f"  ⚠ Not found: {entry['id']} — check your DB")

    conn.commit()
    conn.close()
    print(f"\n✅ Done — {updated} VW ID.4 entries updated.")
    print("   Restart Flask and check /vehicle/volkswagen to verify.")

if __name__ == '__main__':
    main()
