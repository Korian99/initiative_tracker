import json
import requests
from pathlib import Path
import os
from django.core.management.base import BaseCommand

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # where this file lives
json_path = BASE_DIR /"database_index.json"
save_dir = BASE_DIR / "downloaded_jsons"


class Command(BaseCommand):
    help = 'Create development data'

    def handle(self, *args, **kwargs):
        os.makedirs(save_dir, exist_ok=True)
        with open(json_path, encoding="utf-8") as f:
            creatures = json.load(f)
        non_created = created = []
        
        for creature in creatures:
            url = f"https://pathfinderdashboard.com/{creature['path']}"
            try:
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                new_path = creature['path'].replace('assets/database/',"")
                filename = new_path.replace(' ', '_')
                filepath = os.path.join(save_dir, filename)

                with open(filepath, "w", encoding="utf-8") as out_file:
                    json.dump(data, out_file, ensure_ascii=False, indent=2)

                print(f"✅ Saved {filename}")

                created.append(creature['path'])
            except Exception as e:
                print(f"❌ Error fetching {url}: {e}")
                non_created.append(creature['path'])

        filepath = os.path.join(save_dir, 'non_created.json')
        with open(filepath, "w", encoding="utf-8") as out_file:
            json.dump(non_created, out_file, ensure_ascii=False, indent=2)
        filepath = os.path.join(save_dir, 'created.json')
        with open(filepath, "w", encoding="utf-8") as out_file:
            json.dump(created, out_file, ensure_ascii=False, indent=2)