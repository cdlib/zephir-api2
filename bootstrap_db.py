"""
Seed the database with sample data from a CSV file.

Usage:
    uv run python bootstrap_db.py [CSV_FILE]

CSV_FILE defaults to tests/sample_data.csv. Rows whose id already exists are
skipped (upsert-on-conflict is not performed, to preserve any live data).

Required environment variables (same as the app):
    DATABASE_URI  or  DB_USERNAME / DB_PASSWORD / DB_HOST / DB_DATABASE
"""

import csv
import sys

from app import create_app
from app.extensions import db
from app.models import ZephirFiledata

CSV_DEFAULT = "tests/sample_data.csv"


def seed(csv_path: str) -> None:
    app = create_app()
    with app.app_context():
        db.create_all()

        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            inserted = skipped = 0

            for row in reader:
                htid = row["id"]
                if db.session.get(ZephirFiledata, htid) is not None:
                    print(f"  skip  {htid} (already exists)")
                    skipped += 1
                    continue

                db.session.add(ZephirFiledata(
                    htid=htid,
                    metadata_xml=row["metadata"],
                    metadata_json=row.get("metadata_json"),
                ))
                print(f"  insert {htid}")
                inserted += 1

            db.session.commit()

        print(f"\nDone. {inserted} inserted, {skipped} skipped.")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else CSV_DEFAULT
    seed(path)
