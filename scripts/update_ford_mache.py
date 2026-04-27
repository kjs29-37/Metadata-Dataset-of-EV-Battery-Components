#!/usr/bin/env python3
"""
update_ford_mache.py
Run from project root: python scripts/update_ford_mache.py
Updates all Ford Mustang Mach-E entries with correct image paths and source URLs.
"""
import sqlite3, json, os
from datetime import date

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(BASE_DIR, 'battery_data.db')

MACHE_UPDATES = [
    {
        "id":         "ford_mache_bms_0001",
        "model":      "Ford Mustang Mach-E Battery Energy Control Module (BECM)",
        "image_path": "images/bms/Mach-e_bms.png",
        "source_url": "https://www.youtube.com/watch?v=3_iRpKx9VmI",
        "specs": json.dumps({
            "features": [
                "State of charge (SOC) estimation",
                "State of health (SOH) monitoring",
                "Cell voltage and temperature monitoring",
                "Thermal management control",
                "Ford SYNC integration",
                "CAN bus communication with vehicle ECU"
            ],
            "vehicle_models": ["Ford Mustang Mach-E Extended Range", "Ford Mustang Mach-E GT", "Ford F-150 Lightning"],
            "notes": "Ford Battery Energy Control Module (BECM) managing the Mach-E extended range 98.7kWh pack. Integrates with Ford SYNC and BlueCruise driver assistance systems. Reference from teardown video showing BECM removal and inspection.",
            "date_added": date.today().isoformat()
        })
    },
    {
        "id":         "ford_mache_cell_0001",
        "model":      "Ford Mustang Mach-E Extended Range NMC Pouch Cell (SK Innovation)",
        "image_path": "images/cells/Mach-e_cell.png",
        "source_url": "https://www.youtube.com/watch?v=4vRjo0gaG1g",
        "specs": json.dumps({
            "chemistry":      "NMC (Nickel Manganese Cobalt)",
            "format":         "Pouch",
            "voltage_V":      3.7,
            "capacity_mAh":   63000,
            "vehicle_models": ["Ford Mustang Mach-E Extended Range", "Ford Mustang Mach-E GT"],
            "notes": "SK Innovation NMC pouch cells used in the Mach-E 98.7kWh extended range battery pack. 376 cells total. Reference from battery cell teardown video showing pouch cell construction and dimensions.",
            "date_added": date.today().isoformat()
        })
    },
    {
        "id":         "ford_mache_busbar_0001",
        "model":      "Ford Mustang Mach-E Battery Module Interconnect Busbar",
        "image_path": "images/busbars/Mach-e_busbar.png",
        "source_url": "https://www.youtube.com/watch?v=3_iRpKx9VmI",
        "specs": json.dumps({
            "material":         "Aluminium",
            "voltage_rating_V": 400,
            "current_rating_A": 300,
            "vehicle_models":   ["Ford Mustang Mach-E Extended Range"],
            "notes": "Aluminium busbar connecting pouch cell modules within the Mach-E 98.7kWh extended range pack. Reference from teardown video showing module-level interconnection during disassembly.",
            "date_added": date.today().isoformat()
        })
    },
    {
        "id":         "ford_mache_casing_0001",
        "model":      "Ford Mustang Mach-E 98.7kWh Battery Pack Enclosure",
        "image_path": "images/casings/Mach-e_casing.png",
        "source_url": "https://www.youtube.com/watch?v=8zkLNp8HOCU",
        "specs": json.dumps({
            "material":       "Steel (lower tray) / Aluminium (upper cover)",
            "vehicle_models": ["Ford Mustang Mach-E Extended Range", "Ford Mustang Mach-E GT"],
            "notes": "Skateboard underbody enclosure for the Mach-E 98.7kWh extended range pack. Steel lower tray provides structural rigidity and crash protection; aluminium upper cover seals the pack. Flat form factor lowers the centre of gravity. Reference from full pack removal teardown video.",
            "date_added": date.today().isoformat()
        })
    },
    {
        "id":         "ford_mache_connector_0001",
        "model":      "Ford Mustang Mach-E HV Battery Service Disconnect Connector",
        "image_path": "images/connectors/Mach-e_connector.png",
        "source_url": "https://www.youtube.com/watch?v=eVi0MQFy9K8",
        "specs": json.dumps({
            "connector_type":   "HV service disconnect / interlock",
            "voltage_rating_V": 400,
            "current_rating_A": 300,
            "vehicle_models":   ["Ford Mustang Mach-E", "Ford F-150 Lightning"],
            "notes": "Manual service disconnect connector on the Mach-E HV battery pack. Removing this connector breaks the HV circuit for safe service. Includes a High Voltage Interlock Loop (HVIL) that signals the BECM when disconnected, preventing accidental energisation. Reference from connector inspection teardown video.",
            "date_added": date.today().isoformat()
        })
    },
    {
        "id":         "ford_mache_cable_0001",
        "model":      "Ford Mustang Mach-E HV Orange Interconnect Cable",
        "image_path": "images/cables/Mach-e_cable.png",
        "source_url": "https://www.youtube.com/watch?v=c2DmFRBspe4",
        "specs": json.dumps({
            "conductor_material": "Stranded Copper",
            "insulation":         "Cross-linked Polyethylene (Orange)",
            "voltage_rating":     "400V DC",
            "vehicle_models":     ["Ford Mustang Mach-E Extended Range"],
            "notes": "High-voltage orange interconnect cable connecting the Mach-E battery pack to the power electronics and inverter. Orange insulation is the industry-standard EV safety colour for HV systems. Reference from HV cable inspection teardown video.",
            "date_added": date.today().isoformat()
        })
    },
    {
        "id":         "ford_mache_hardware_0001",
        "model":      "Ford Mustang Mach-E Battery Pack Mounting Bolts & Brackets",
        "image_path": "images/hardware/Mach-e_hardware.png",
        "source_url": "https://www.youtube.com/watch?v=eVi0MQFy9K8",
        "specs": json.dumps({
            "part_type":      "nut/bolt/bracket",
            "material":       "High-strength Steel",
            "vehicle_models": ["Ford Mustang Mach-E Extended Range", "Ford Mustang Mach-E GT"],
            "notes": "High-strength steel mounting bolts and brackets securing the Mach-E skateboard battery pack to the vehicle chassis. Fasteners thread into reinforced underbody mounting points, distributing pack weight evenly and providing crash structure integration. Reference from hardware inspection teardown video.",
            "date_added": date.today().isoformat()
        })
    },
]

def main():
    conn = sqlite3.connect(DB_PATH)

    updated = 0
    for entry in MACHE_UPDATES:
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
    print(f"\n✅ Done — {updated} Ford Mach-E entries updated.")
    print("   Restart Flask and check /vehicle/ford to verify.")

if __name__ == '__main__':
    main()
