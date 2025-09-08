import json
import requests
from pathlib import Path
import os
from django.core.management.base import BaseCommand
from players.models import StatBlock

BASE_DIR = Path(__file__).resolve().parent.parent.parent
json_path = BASE_DIR / "database_index.json"
save_dir = BASE_DIR / "downloaded_jsons"


class Command(BaseCommand):
    help = 'Create development data'

    def handle(self, *args, **kwargs):
        os.makedirs(save_dir, exist_ok=True)
        with open(json_path, encoding="utf-8") as f:
            creatures = json.load(f)
        to_create = []
        for creature in creatures:
            url = f"https://pathfinderdashboard.com/{creature['path']}"
            try:
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                data = resp.json()

                to_create.append(
                    StatBlock(
                        name=creature["name"],
                        path=creature["path"],
                        data=data
                    )
                )
                print(f"✅ Saved {creature['name']}")
            except Exception as e:
                print(f"❌ Error {creature['name']}")
                to_create.append(
                    StatBlock(
                        name=creature["name"],
                        path=creature["path"],
                        data=None
                    )
                )

        StatBlock.objects.bulk_create(to_create, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f"Inserted {len(to_create)} stat blocks."))
