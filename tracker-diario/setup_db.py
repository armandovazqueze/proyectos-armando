"""
setup_db.py — Diagnoses and initializes tracker.db safely.

- Prints the exact DB path being used by the project
- Shows existing tables
- Applies schema.sql using CREATE TABLE IF NOT EXISTS (safe, no data loss)
- Loads the activity catalog from seed.sql if the activities table is empty
- Verifies the result

Run from tracker-diario/:
    python setup_db.py
"""
import sqlite3
import sys
from pathlib import Path

# ── Resolve paths the same way app/db.py does ────────────────────────────────

ROOT     = Path(__file__).parent          # tracker-diario/
DB_PATH  = ROOT / "tracker.db"
SCHEMA   = ROOT / "database" / "schema.sql"
SEED     = ROOT / "database" / "seed.sql"

print(f"\n{'='*55}")
print(f"  tracker-diario DB setup")
print(f"{'='*55}")
print(f"\n  DB path   : {DB_PATH}")
print(f"  Schema    : {SCHEMA}")
print(f"  Seed      : {SEED}")


# ── Sanity check ──────────────────────────────────────────────────────────────

for f, label in [(SCHEMA, "schema.sql"), (SEED, "seed.sql")]:
    if not f.exists():
        print(f"\n  ERROR: {label} not found at {f}")
        sys.exit(1)

db_existed = DB_PATH.exists()
print(f"\n  tracker.db exists before setup: {db_existed}")


# ── Connect and inspect current state ────────────────────────────────────────

conn = sqlite3.connect(str(DB_PATH))
conn.execute("PRAGMA foreign_keys = ON")

def get_tables(conn):
    return [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()]

tables_before = get_tables(conn)
print(f"  Tables before  : {tables_before or '(none)'}")


# ── Apply schema (CREATE TABLE IF NOT EXISTS — safe, no data loss) ────────────

print("\n  Applying schema.sql ...")
conn.executescript(SCHEMA.read_text())
conn.commit()

tables_after = get_tables(conn)
print(f"  Tables after   : {tables_after}")

expected = {"activities", "daily_checkins", "checkin_activities"}
missing  = expected - set(tables_after)
if missing:
    print(f"\n  ERROR: These tables are still missing: {missing}")
    conn.close()
    sys.exit(1)
print("  Schema OK ✓")


# ── Load activity catalog if empty ────────────────────────────────────────────

act_count = conn.execute("SELECT COUNT(*) FROM activities").fetchone()[0]
print(f"\n  Activities in catalog: {act_count}")

if act_count == 0:
    print("  Loading activity catalog from seed.sql ...")
    conn.executescript(SEED.read_text())
    conn.commit()
    act_count = conn.execute("SELECT COUNT(*) FROM activities").fetchone()[0]
    print(f"  Activities after seed : {act_count}")
else:
    print("  Catalog already populated — seed skipped.")


# ── Final summary ─────────────────────────────────────────────────────────────

checkin_count = conn.execute("SELECT COUNT(*) FROM daily_checkins").fetchone()[0]

print(f"\n{'='*55}")
print(f"  DB path       : {DB_PATH}")
print(f"  Tables        : {', '.join(sorted(get_tables(conn)))}")
print(f"  Activities    : {act_count}")
print(f"  Check-ins     : {checkin_count}")
print(f"{'='*55}\n")

conn.close()
print("  Setup complete. You can now run:")
print("    python telegram_bot/bot.py")
print("    streamlit run dashboard/app.py\n")
