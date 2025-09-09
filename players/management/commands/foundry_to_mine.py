from django.core.management.base import BaseCommand

import re
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # where this file lives
# --- CONFIG ---
jsons_dir = BASE_DIR.parent / "jsons"          # folder with your creature JSONs
index_file = BASE_DIR / "database_index.json"

# regex to catch "123 - Name.json"
pattern_ = re.compile(r"^\s*(-?\d+)_-_(.+?)\.json$", re.IGNORECASE)
pattern = re.compile(r"^(\d+)\s*-\s*(.+)\.json$", re.IGNORECASE)
def rename_files_and_update_index():
    # Step 1: Rename files
    rename_map = {}  # old -> new
    for file in jsons_dir.glob("*.json"):
        match = pattern_.match(file.name)
        if match:
            print(match)
            new_name = f"{match.group(2)}.json"
            new_path = file.with_name(new_name)

            # Avoid overwriting if file already exists
            if new_path.exists():
                print(f"⚠️ Skipping {file.name}, {new_name} already exists")
                continue

            file.rename(new_path)
            rename_map[file.name] = new_name
            print(f"✅ Renamed {file.name} → {new_name}")

    # Step 2: Update database_index.json
    if index_file.exists():
        with open(index_file, encoding="utf-8") as f:
            index_data = json.load(f)

        for entry in index_data:
            old_path = entry.get("path")
            if old_path:
                filename = Path(old_path).name
                if filename in rename_map:
                    entry["path"] = old_path.replace(filename, rename_map[filename])
                    print(f"🔄 Updated path for {entry['name']} → {entry['path']}")

        # Save updated index
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)

        print("💾 database_index.json updated")
class Command(BaseCommand):
    help = 'Create development data'

    def handle(self, *args, **kwargs):
        rename_files_and_update_index()


