import json
import requests
from pathlib import Path
import os
from django.core.management.base import BaseCommand

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # where this file lives
json_path = BASE_DIR /"database_index.json"
save_dir = BASE_DIR / "downloaded_jsons"

def transform_foundry_to_tracker(foundry_json):
    npc = {}
    sys = foundry_json["system"]

    # Core creature info
    npc.update({
        "initiative": 0,
        "initiativebonus": sys["perception"]["mod"],
        "comments": "",
        "conditions": [],
        "color": "#fff",
        "duplicateIndex": 0,
        "name": foundry_json["name"],
        "type": "Creature",
        "level": sys["details"]["level"]["value"],
        "traits": [sys["traits"]["size"]["value"].capitalize()] +
                [t.capitalize() for t in sys["traits"]["value"]],
        "source": sys["details"]["publication"]["title"],
    })

    # Perception
    npc["perception"] = {
        "value": sys["perception"]["mod"],
        "note": sys["perception"]["details"],
        "usedAttribute": "wisdom",
        "modifications": []
    }

    npc["senses"] = sys["perception"].get("senses", [])

    # Languages
    npc["languages"] = [lang.capitalize() for lang in sys["details"]["languages"]["value"]]

    # Skills
    npc["skills"] = [
        {
            "name": name,
            "modifier": data["base"],
            "note": [],
            "usedAttribute": attr,
            "modifications": []
        }
        for name, data in sys["skills"].items()
        for attr in [  # crude attribute mapping
            {"athletics":"strength","intimidation":"charisma","stealth":"dexterity","survival":"wisdom"}.get(name,"")]
    ]

    # Ability scores
    for abbr, fullname in {
        "str": "strength", "dex": "dexterity", "con": "constitution",
        "int": "intelligence", "wis": "wisdom", "cha": "charisma"
    }.items():
        npc[fullname] = {"value": sys["abilities"][abbr]["mod"]}

    # AC and Saves
    npc["ac"] = {"value": sys["attributes"]["ac"]["value"], "note": "", "usedAttribute": "dexterity", "modifications": []}
    npc["fortitude"] = {"value": sys["saves"]["fortitude"]["value"], "note": "", "usedAttribute": "constitution", "modifications": []}
    npc["reflex"] = {"value": sys["saves"]["reflex"]["value"], "note": "", "usedAttribute": "dexterity", "modifications": []}
    npc["will"] = {"value": sys["saves"]["will"]["value"], "note": "", "usedAttribute": "wisdom", "modifications": []}

    npc["hp"] = {
        "value": sys["attributes"]["hp"]["value"],
        "max": sys["attributes"]["hp"]["max"],
        "note": "",
        "modifications": []
    }

    # Speed
    npc["speed"] = f"{sys['attributes']['speed']['value']} ft,"

    # Equipment items
    npc["items"] = [
        {
            "name": item["name"],
            "quantity": item["system"].get("quantity", 1),
            "description": item["system"]["description"]["value"],
            "level": item["system"]["level"]["value"],
            "price": " ".join(f"{v} {k}" for k, v in item["system"]["price"]["value"].items()),
            "traits": item["system"]["traits"]["value"],
        }
        for item in foundry_json["items"]
        if item["type"] in ("weapon", "armor", "equipment")
    ]

    # Strikes (melee/ranged)
    npc["strikes"] = []
    for item in foundry_json["items"]:
        if item["type"] == "melee":
            strike = {
                "type": item["system"]["weaponType"]["value"],
                "name": item["name"],
                "bonus": item["system"]["bonus"]["value"],
                "traits": item["system"]["traits"]["value"],
                "damageRolls": [{"roll": d["damage"], "type": d["damageType"]}
                                for d in item["system"]["damageRolls"].values()],
                "critRolls": [{"roll": f"({d['damage']})*2", "type": d["damageType"]}
                            for d in item["system"]["damageRolls"].values()],
                "effects": item["system"]["attackEffects"]["value"],
                "usedAttributeToHit": "strength" if item["system"]["weaponType"]["value"]=="melee" else "dexterity",
                "usedAttributeDamage": "strength",
                "toHitModifications": [],
                "damageModifications": []
            }
            npc["strikes"].append(strike)

    # Abilities
    npc["defensiveAbilities"] = [
        {"name": item["name"], "actions": -1, "traits": item["system"]["traits"]["value"], "description": item["system"]["description"]["value"], "collapsed": False}
        for item in foundry_json["items"] if item["type"] == "action" and item["system"]["actionType"]["value"]=="reaction"
    ]

    npc["offensiveAbilities"] = [
        {"name": item["name"], "actions": None, "traits": item["system"]["traits"]["value"], "description": item["system"]["description"]["value"], "collapsed": False}
        for item in foundry_json["items"] if item["type"] == "action" and item["system"]["actionType"]["value"]=="passive"
    ]

    return npc



class Command(BaseCommand):
    help = 'Create development data'

    def handle(self, *args, **kwargs):
        with open("foundry_npc.json", encoding="utf-8") as f:
            foundry_data = json.load(f)

        tracker_json = transform_foundry_to_tracker(foundry_data)
        print(json.dumps(tracker_json, indent=2, ensure_ascii=False))

