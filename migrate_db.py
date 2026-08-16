#!/usr/bin/env python3
"""
reset_database.py — Clear ALL data from every table. Keep schema intact.

Place next to app.py / run.py, then run:
    python reset_database.py

What it does:
  • DELETEs every row from every table (tables stay, schema stays)
  • Resets auto-increment / identity counters back to 1
  • Temporarily disables foreign keys so order does not matter
  • Re-enables foreign keys after cleanup

WARNING: This is irreversible. Type the confirmation carefully.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# ---------------------------------------------------------------------------
# 1. Load the Flask app (tries common patterns)
# ---------------------------------------------------------------------------
app = None

for module, attr in [("app", "app"), ("run", "app"), ("wsgi", "app")]:
    if app is None:
        try:
            mod = __import__(module, fromlist=[attr])
            app = getattr(mod, attr)
            print("Loaded Flask app from " + module + ".py")
            break
        except Exception:
            pass

for module in ["app", "run", "wsgi"]:
    if app is None:
        try:
            mod = __import__(module, fromlist=["create_app"])
            app = mod.create_app()
            print("Created Flask app via " + module + ".create_app()")
            break
        except Exception:
            pass

if app is None:
    print("ERROR: Could not find a Flask app instance.")
    print("  Tried: from app import app")
    print("  Tried: from run import app")
    print("  Tried: from wsgi import app")
    print("  Tried: create_app() from app, run, wsgi")
    print("  Quick fix: edit this script and add your import.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 2. Imports (need app context for db.engine)
# ---------------------------------------------------------------------------
from database.db import db
from sqlalchemy import text, inspect


def reset_database():
    print("=" * 70)
    print("  DATABASE RESET — DATA ONLY")
    print("  Deletes rows | Keeps tables | Keeps schema | Start fresh")
    print("=" * 70)

    with app.app_context():
        engine = db.engine
        inspector = inspect(engine)
        dialect = engine.dialect.name
        all_tables = inspector.get_table_names()

        print("")
        print("Project root : " + PROJECT_ROOT)
        print("Dialect      : " + dialect)
        print("Tables found : " + str(len(all_tables)))
        for t in sorted(all_tables):
            print("    * " + t)

        confirm = input(
            "\nWARNING: This will PERMANENTLY DELETE every row from every table.\n"
            "    Tables, columns, indexes, and constraints will NOT be touched.\n"
            "    Type DELETE EVERYTHING to proceed: "
        )
        if confirm.strip() != "DELETE EVERYTHING":
            print("\nCancelled. No data was deleted.")
            return

        with engine.begin() as conn:

            if dialect == "sqlite":
                print("\nSQLite: disabling foreign keys...")
                conn.execute(text("PRAGMA foreign_keys = OFF"))

                for table in sorted(all_tables):
                    print("    DELETE FROM " + table + " ...", end=" ")
                    conn.execute(text('DELETE FROM "' + table + '"'))
                    print("OK")

                if "sqlite_sequence" in all_tables:
                    print("    Resetting sqlite_sequence ...", end=" ")
                    conn.execute(text("DELETE FROM sqlite_sequence"))
                    print("OK")

                print("Re-enabling foreign keys...")
                conn.execute(text("PRAGMA foreign_keys = ON"))

            elif dialect == "postgresql":
                print("\nPostgreSQL: truncating with CASCADE + RESTART IDENTITY...")
                for table in sorted(all_tables):
                    print("    TRUNCATE " + table + " ...", end=" ")
                    conn.execute(text('TRUNCATE TABLE "' + table + '" RESTART IDENTITY CASCADE'))
                    print("OK")

            elif dialect in ("mysql", "mariadb"):
                print("\nMySQL: disabling foreign key checks...")
                conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

                for table in sorted(all_tables):
                    print("    DELETE FROM " + table + " ...", end=" ")
                    conn.execute(text("DELETE FROM `" + table + "`"))
                    print("OK")

                for table in sorted(all_tables):
                    conn.execute(text("ALTER TABLE `" + table + "` AUTO_INCREMENT = 1"))

                print("Re-enabling foreign key checks...")
                conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

            else:
                print("\nGeneric (" + dialect + "): deleting rows...")
                for table in sorted(all_tables):
                    print("    DELETE FROM " + table + " ...", end=" ")
                    conn.execute(text('DELETE FROM "' + table + '"'))
                    print("OK")

        print("")
        print("=" * 70)
        print("  DONE — All rows cleared, tables and schema intact.")
        print("=" * 70)
        print("  You can now start fresh. Register a new company, users, etc.")
        print("=" * 70)


if __name__ == "__main__":
    reset_database()