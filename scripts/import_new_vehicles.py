#!/usr/bin/env python3
"""
import_new_vehicles.py
Run from project root: python scripts/import_new_vehicles.py
Adds placeholder entries for VW ID.4, Renault Zoe, Hyundai Ioniq 5, Ford Mustang Mach-E
Images are None (placeholder) — add images later by updating image_path in DB or re-running import.
"""
import sqlite3, json, os
from datetime import date

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(BASE_DIR, 'battery_data.db')

def specs(**kwargs):
    return json.dumps({**kwargs, "date_added": date.today().isoformat()})

ENTRIES = [
    # VW ID.4
    {"id":"vw_id4_cell_0001",      "type":"cells",      "manufacturer":"Volkswagen AG",           "model":"ID.4 NMC Prismatic Cell (Samsung SDI)",          "source_url":"https://www.volkswagen-newsroom.com/en/stories/the-id-4-battery-6880",  "specs":specs(chemistry="NMC",format="Prismatic",voltage_V=3.68,capacity_mAh=78000,vehicle_models=["VW ID.4 Pro","VW ID.4 GTX"],notes="Samsung SDI prismatic cells in the 77kWh MEB pack. 288 cells total across 12 modules.")},
    {"id":"vw_id4_bms_0001",       "type":"bms",        "manufacturer":"Volkswagen AG",           "model":"ID.4 MEB Battery Management System",              "source_url":"https://www.volkswagen-newsroom.com/en/stories/the-id-4-battery-6880",  "specs":specs(features=["Cell voltage monitoring","Thermal management","SOH estimation","CAN bus"],vehicle_models=["VW ID.4","VW ID.3","Audi Q4 e-tron"],notes="MEB platform BMS shared across VW Group MEB vehicles.")},
    {"id":"vw_id4_connector_0001", "type":"connectors", "manufacturer":"Volkswagen AG",           "model":"ID.4 HV Service Disconnect Connector",            "source_url":"https://www.volkswagen-newsroom.com/en/stories/the-id-4-battery-6880",  "specs":specs(connector_type="HV service disconnect",voltage_rating_V=400,current_rating_A=300,vehicle_models=["VW ID.4"],notes="Orange housing with HVIL interlock for safe servicing of MEB pack.")},
    {"id":"vw_id4_cable_0001",     "type":"cables",     "manufacturer":"Volkswagen AG",           "model":"ID.4 HV Orange Interconnect Cable",               "source_url":"https://www.volkswagen-newsroom.com/en/stories/the-id-4-battery-6880",  "specs":specs(conductor_material="Stranded Copper",insulation="Orange XLPE",voltage_rating="400V DC",vehicle_models=["VW ID.4"],notes="Standard MEB HV cable connecting battery to e-motor inverter.")},
    {"id":"vw_id4_busbar_0001",    "type":"busbars",    "manufacturer":"Volkswagen AG",           "model":"ID.4 MEB Module Interconnect Busbar",             "source_url":"https://www.volkswagen-newsroom.com/en/stories/the-id-4-battery-6880",  "specs":specs(material="Aluminium",voltage_rating_V=400,current_rating_A=250,vehicle_models=["VW ID.4"],notes="Aluminium busbar connecting prismatic modules in MEB 77kWh pack.")},
    {"id":"vw_id4_casing_0001",    "type":"casings",    "manufacturer":"Volkswagen AG",           "model":"ID.4 MEB Battery Pack Enclosure",                 "source_url":"https://www.volkswagen-newsroom.com/en/stories/the-id-4-battery-6880",  "specs":specs(material="Aluminium / Steel",vehicle_models=["VW ID.4"],notes="Flat underbody skateboard enclosure. Aluminium extrusion frame with integrated liquid cooling channels.")},
    {"id":"vw_id4_hardware_0001",  "type":"hardware",   "manufacturer":"Volkswagen AG",           "model":"ID.4 Battery Pack Mounting Bolts",                "source_url":"https://www.volkswagen-newsroom.com/en/stories/the-id-4-battery-6880",  "specs":specs(part_type="nut/bolt/bracket",material="High-strength Steel",vehicle_models=["VW ID.4"],notes="Structural mounting fasteners securing MEB pack to vehicle chassis underbody.")},

    # Renault Zoe
    {"id":"renault_zoe_cell_0001",      "type":"cells",      "manufacturer":"Renault / LG Energy Solution","model":"Zoe Z.E. 50 NMC Pouch Cell",              "source_url":"https://www.renault.co.uk/electric-vehicles/zoe/range-and-battery.html","specs":specs(chemistry="NMC",format="Pouch",voltage_V=3.65,capacity_mAh=55000,vehicle_models=["Renault Zoe Z.E. 50"],notes="LG Energy Solution pouch cells in the 52kWh Z.E. 50 pack. 192 cells in 4 modules.")},
    {"id":"renault_zoe_bms_0001",       "type":"bms",        "manufacturer":"Renault",                    "model":"Zoe Z.E. 50 Battery Management System",    "source_url":"https://www.renault.co.uk/electric-vehicles/zoe/range-and-battery.html","specs":specs(features=["Cell balancing","SOC/SOH monitoring","Thermal management","CAN bus"],vehicle_models=["Renault Zoe Z.E. 50","Renault Zoe Z.E. 40"],notes="Renault proprietary BMS for Z.E. platform managing the 52kWh pack.")},
    {"id":"renault_zoe_connector_0001", "type":"connectors", "manufacturer":"Renault",                    "model":"Zoe Z.E. 50 HV Battery Connector",         "source_url":"https://www.renault.co.uk/electric-vehicles/zoe/range-and-battery.html","specs":specs(connector_type="HV battery connector",voltage_rating_V=400,vehicle_models=["Renault Zoe Z.E. 50"],notes="HV connector for the 52kWh pack. Orange housing identifies HV circuit.")},
    {"id":"renault_zoe_cable_0001",     "type":"cables",     "manufacturer":"Renault",                    "model":"Zoe Z.E. 50 HV Cable",                     "source_url":"https://www.renault.co.uk/electric-vehicles/zoe/range-and-battery.html","specs":specs(conductor_material="Stranded Copper",insulation="Orange XLPE",voltage_rating="400V DC",vehicle_models=["Renault Zoe Z.E. 50"],notes="HV interconnect cable for the Renault Zoe battery system.")},
    {"id":"renault_zoe_busbar_0001",    "type":"busbars",    "manufacturer":"Renault",                    "model":"Zoe Z.E. 50 Module Busbar",                "source_url":"https://www.renault.co.uk/electric-vehicles/zoe/range-and-battery.html","specs":specs(material="Copper",vehicle_models=["Renault Zoe Z.E. 50"],notes="Copper busbar connecting pouch cell modules in the Zoe 52kWh pack.")},
    {"id":"renault_zoe_casing_0001",    "type":"casings",    "manufacturer":"Renault",                    "model":"Zoe Z.E. 50 Battery Pack Enclosure",       "source_url":"https://www.renault.co.uk/electric-vehicles/zoe/range-and-battery.html","specs":specs(material="Steel / Aluminium",vehicle_models=["Renault Zoe Z.E. 50"],notes="Floor-mounted skateboard enclosure for the 52kWh Z.E. 50 pack.")},
    {"id":"renault_zoe_hardware_0001",  "type":"hardware",   "manufacturer":"Renault",                    "model":"Zoe Z.E. 50 Battery Mounting Fasteners",   "source_url":"https://www.renault.co.uk/electric-vehicles/zoe/range-and-battery.html","specs":specs(part_type="nut/bolt/bracket",material="Steel",vehicle_models=["Renault Zoe Z.E. 50"],notes="Fasteners securing the Z.E. 50 pack to vehicle chassis.")},

    # Hyundai Ioniq 5
    {"id":"hyundai_ioniq5_cell_0001",      "type":"cells",      "manufacturer":"Hyundai / SK Innovation","model":"Ioniq 5 NMC Pouch Cell (SK Innovation)",     "source_url":"https://www.hyundai.co.uk/electric-cars/ioniq5",                         "specs":specs(chemistry="NMC",format="Pouch",voltage_V=3.7,capacity_mAh=78000,vehicle_models=["Hyundai Ioniq 5 Long Range","Kia EV6 Long Range"],notes="SK Innovation pouch cells in E-GMP 77.4kWh pack. 360 cells in 30 modules. Supports 800V ultra-fast charging.")},
    {"id":"hyundai_ioniq5_bms_0001",       "type":"bms",        "manufacturer":"Hyundai",                "model":"Ioniq 5 E-GMP Battery Management System",    "source_url":"https://www.hyundai.co.uk/electric-cars/ioniq5",                         "specs":specs(features=["800V architecture support","Ultra-fast charge management","V2L bidirectional control","Cell balancing","SOH monitoring"],vehicle_models=["Hyundai Ioniq 5","Kia EV6","Genesis GV60"],notes="E-GMP BMS managing 77.4kWh pack. Supports 800V charging and V2L power delivery.")},
    {"id":"hyundai_ioniq5_connector_0001", "type":"connectors", "manufacturer":"Hyundai",                "model":"Ioniq 5 800V HV Connector",                  "source_url":"https://www.hyundai.co.uk/electric-cars/ioniq5",                         "specs":specs(connector_type="800V HV connector",voltage_rating_V=800,current_rating_A=350,vehicle_models=["Hyundai Ioniq 5","Kia EV6"],notes="800V-rated HV connector unique to E-GMP. Enables 350kW ultra-fast charging.")},
    {"id":"hyundai_ioniq5_cable_0001",     "type":"cables",     "manufacturer":"Hyundai",                "model":"Ioniq 5 E-GMP 800V HV Cable",                "source_url":"https://www.hyundai.co.uk/electric-cars/ioniq5",                         "specs":specs(conductor_material="Stranded Copper",voltage_rating="800V DC",vehicle_models=["Hyundai Ioniq 5"],notes="800V-rated HV cable for E-GMP platform. Higher insulation rating than standard 400V EV cables.")},
    {"id":"hyundai_ioniq5_busbar_0001",    "type":"busbars",    "manufacturer":"Hyundai",                "model":"Ioniq 5 E-GMP Module Busbar",                "source_url":"https://www.hyundai.co.uk/electric-cars/ioniq5",                         "specs":specs(material="Aluminium",voltage_rating_V=800,vehicle_models=["Hyundai Ioniq 5"],notes="800V-rated aluminium busbar connecting E-GMP modules.")},
    {"id":"hyundai_ioniq5_casing_0001",    "type":"casings",    "manufacturer":"Hyundai",                "model":"Ioniq 5 E-GMP Battery Pack Enclosure",       "source_url":"https://www.hyundai.co.uk/electric-cars/ioniq5",                         "specs":specs(material="Aluminium",vehicle_models=["Hyundai Ioniq 5","Kia EV6"],notes="E-GMP underbody enclosure. Flat pack enables low floor height and spacious interior.")},
    {"id":"hyundai_ioniq5_hardware_0001",  "type":"hardware",   "manufacturer":"Hyundai",                "model":"Ioniq 5 Battery Pack Mounting Bolts",         "source_url":"https://www.hyundai.co.uk/electric-cars/ioniq5",                         "specs":specs(part_type="nut/bolt/bracket",material="High-strength Steel",vehicle_models=["Hyundai Ioniq 5"],notes="Structural mounting hardware for E-GMP pack.")},

    # Ford Mustang Mach-E
    {"id":"ford_mache_cell_0001",      "type":"cells",      "manufacturer":"Ford / SK Innovation","model":"Mach-E Extended Range Pouch Cell",              "source_url":"https://www.ford.co.uk/cars/all-electric/mustang-mach-e",                "specs":specs(chemistry="NMC",format="Pouch",voltage_V=3.7,capacity_mAh=63000,vehicle_models=["Ford Mustang Mach-E Extended Range","Ford Mustang Mach-E GT"],notes="SK Innovation pouch cells in the 98.7kWh extended range pack. 376 cells total.")},
    {"id":"ford_mache_bms_0001",       "type":"bms",        "manufacturer":"Ford",               "model":"Mach-E Battery Energy Control Module (BECM)",  "source_url":"https://www.ford.co.uk/cars/all-electric/mustang-mach-e",                "specs":specs(features=["SOC/SOH monitoring","Cell balancing","Thermal management","Ford SYNC integration"],vehicle_models=["Ford Mustang Mach-E","Ford F-150 Lightning"],notes="Ford BECM managing Mach-E extended range pack. Integrates with Ford SYNC.")},
    {"id":"ford_mache_connector_0001", "type":"connectors", "manufacturer":"Ford",               "model":"Mach-E HV Battery Service Disconnect",         "source_url":"https://www.ford.co.uk/cars/all-electric/mustang-mach-e",                "specs":specs(connector_type="HV service disconnect",voltage_rating_V=400,current_rating_A=300,vehicle_models=["Ford Mustang Mach-E"],notes="Manual service disconnect for the Mach-E HV pack. Orange housing, HVIL interlock.")},
    {"id":"ford_mache_cable_0001",     "type":"cables",     "manufacturer":"Ford",               "model":"Mach-E HV Orange Interconnect Cable",          "source_url":"https://www.ford.co.uk/cars/all-electric/mustang-mach-e",                "specs":specs(conductor_material="Stranded Copper",insulation="Orange XLPE",voltage_rating="400V DC",vehicle_models=["Ford Mustang Mach-E"],notes="HV cable connecting battery to inverter on the Mach-E.")},
    {"id":"ford_mache_busbar_0001",    "type":"busbars",    "manufacturer":"Ford",               "model":"Mach-E Battery Module Busbar",                 "source_url":"https://www.ford.co.uk/cars/all-electric/mustang-mach-e",                "specs":specs(material="Aluminium",voltage_rating_V=400,vehicle_models=["Ford Mustang Mach-E"],notes="Aluminium busbar connecting pouch cell modules in the Mach-E extended range pack.")},
    {"id":"ford_mache_casing_0001",    "type":"casings",    "manufacturer":"Ford",               "model":"Mach-E 98.7kWh Battery Pack Enclosure",        "source_url":"https://www.ford.co.uk/cars/all-electric/mustang-mach-e",                "specs":specs(material="Aluminium / Steel",vehicle_models=["Ford Mustang Mach-E Extended Range"],notes="Skateboard underbody enclosure for the 98.7kWh pack. Steel lower tray, aluminium upper cover.")},
    {"id":"ford_mache_hardware_0001",  "type":"hardware",   "manufacturer":"Ford",               "model":"Mach-E Battery Pack Mounting Hardware",        "source_url":"https://www.ford.co.uk/cars/all-electric/mustang-mach-e",                "specs":specs(part_type="nut/bolt/bracket",material="High-strength Steel",vehicle_models=["Ford Mustang Mach-E"],notes="Chassis mounting fasteners for the Mach-E extended range battery pack.")},
]

def main():
    conn = sqlite3.connect(DB_PATH)
    for col in ['source_url','model']:
        try: conn.execute(f"ALTER TABLE components ADD COLUMN {col} TEXT")
        except: pass

    inserted = updated = 0
    for e in ENTRIES:
        exists = conn.execute("SELECT id FROM components WHERE id=?", (e['id'],)).fetchone()
        if exists:
            conn.execute("UPDATE components SET type=?,manufacturer=?,model=?,image_path=?,source_url=?,specs=? WHERE id=?",
                         (e['type'],e['manufacturer'],e['model'],None,e['source_url'],e['specs'],e['id']))
            print(f"  ↻ Updated : {e['id']}")
            updated += 1
        else:
            conn.execute("INSERT INTO components (id,type,manufacturer,model,image_path,source_url,specs) VALUES (?,?,?,?,?,?,?)",
                         (e['id'],e['type'],e['manufacturer'],e['model'],None,e['source_url'],e['specs']))
            print(f"  ✓ Inserted: {e['id']}")
            inserted += 1

    conn.commit()
    conn.close()
    print(f"\n✅ Done — {inserted} inserted, {updated} updated.")
    print(f"   Your dataset now has entries for 7 vehicle platforms.")
    print(f"   Cards will show 'Image pending / Coming soon' until images are added.")

if __name__ == '__main__':
    main()