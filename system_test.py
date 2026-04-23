"""
Quick System Integrity Test
Verifies that all system components are correctly set up
"""

import sys
import os
import sqlite3

def test_system_integrity():
    """
    Test system integrity without using problematic Unicode characters
    """
    print("Testing Activity Search System Integrity")
    print("="*40)

    # Test 1: Check if skill files exist
    print("1. Checking skill files...")
    skill_files = [
        "skills/search-engine.skill",
        "skills/result-processor.skill",
        "skills/report-generator.skill",
        "skills/search-engine/implementation.py",
        "skills/result-processor/implementation.py",
        "skills/report-generator/implementation.py"
    ]

    all_skills_exist = True
    for skill_file in skill_files:
        if os.path.isfile(skill_file):
            print(f"   OK: {skill_file}")
        else:
            print(f"   MISSING: {skill_file}")
            all_skills_exist = False

    if all_skills_exist:
        print("   All skill files exist")
    else:
        print("   Some skill files are missing")
        return False

    # Test 2: Check if databases exist
    print("\n2. Checking databases...")
    db_files = ["search_results.db", "report_ready_results.db", "historical_reports.db"]

    all_dbs_exist = True
    for db_file in db_files:
        if os.path.isfile(db_file):
            print(f"   OK: {db_file}")
        else:
            print(f"   MISSING: {db_file}")
            all_dbs_exist = False

    if all_dbs_exist:
        print("   All databases exist")
    else:
        print("   Some databases are missing")
        return False

    # Test 3: Check database schemas
    print("\n3. Checking database schemas...")
    try:
        # Check search_results.db
        conn = sqlite3.connect("search_results.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]

        if 'universal_search_results' in table_names and 'targeted_fetch_results' in table_names:
            print("   OK: search_results.db has correct tables")
        else:
            print(f"   ERROR: search_results.db missing tables. Found: {table_names}")
            return False
        conn.close()

        # Check report_ready_results.db
        conn = sqlite3.connect("report_ready_results.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]

        if 'report_ready_results' in table_names:
            print("   OK: report_ready_results.db has correct tables")
        else:
            print(f"   ERROR: report_ready_results.db missing tables. Found: {table_names}")
            return False
        conn.close()

        # Check historical_reports.db
        conn = sqlite3.connect("historical_reports.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]

        if 'historical_reports' in table_names:
            print("   OK: historical_reports.db has correct tables")
        else:
            print(f"   ERROR: historical_reports.db missing tables. Found: {table_names}")
            return False
        conn.close()

    except Exception as e:
        print(f"   ERROR: Database schema check failed: {e}")
        return False

    # Test 4: Check cron job configuration
    print("\n4. Checking cron job configuration...")
    if os.path.isfile("cron-jobs/drone-activity-tracker.json"):
        print("   OK: Cron job configuration exists")
    else:
        print("   ERROR: Cron job configuration missing")
        return False

    # Test 5: Check main execution script
    print("\n5. Checking main script...")
    if os.path.isfile("run_activity_search.py"):
        print("   OK: Main execution script exists")
    else:
        print("   ERROR: Main execution script missing")
        return False

    print("\n" + "="*40)
    print("System integrity check PASSED!")
    print("All components are correctly set up.")
    print("="*40)
    return True

if __name__ == "__main__":
    success = test_system_integrity()
    if success:
        print("\nSystem is ready for drone activity tracking!")
        exit(0)
    else:
        print("\nSystem integrity check FAILED!")
        exit(1)