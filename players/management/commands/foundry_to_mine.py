from django.core.management.base import BaseCommand

import re
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # where this file lives
# --- CONFIG ---
jsons_dir = BASE_DIR.parent / "jsons"          # folder with your creature JSONs
index_file = BASE_DIR / "database_index.json"

# regex to catch "123 - Name.json"
pattern = re.compile(r"^(\d+)\s*-\s*(.+)\.json$", re.IGNORECASE)
def rename_files_and_update_index():
    # Step 1: Rename files
    rename_map = {}  # old -> new
    if index_file.exists():
        with open(index_file, encoding="utf-8") as f:
            index_data = json.load(f)
        for entry in index_data:
            entry["path"] = entry["name"]+".json"
            print(f"🔄 Updated path for {entry['name']} → {entry['path']}")

        # Save updated index
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)

        print("💾 database_index.json updated")
class Command(BaseCommand):
    help = 'Create development data'

    def handle(self, *args, **kwargs):
        rename_files_and_update_index()


