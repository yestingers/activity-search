#!/usr/bin/env python3
"""
System Initialization Script
Sets up all databases and verifies system components
"""

import os
import sqlite3
from datetime import datetime

def init_system():
    """
    Initialize the complete Activity Search system
    """
    print("Setting up Activity Search System...")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Initialize all databases
    print("\n1/4 Setting up search results database...")
    setup_search_database()

    print("\n2/4 Setting up report-ready results database...")
    setup_report_ready_database()

    print("\n3/4 Setting up historical reports database...")
    setup_historical_database()

    print("\n4/4 Verifying system components...")
    verify_components()

    print(f"\nSystem initialization completed successfully!")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nSystem is now ready to run drone activity searches.")


def setup_search_database():
    """
    Set up the main search results database
    """
    db_path = "search_results.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table for universal search results (search result库1)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS universal_search_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            content TEXT,
            source_engine TEXT,
            search_category TEXT,
            search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            relevance_score REAL DEFAULT 0.0
        )
    ''')

    # Create table for targeted fetch results (search result库2)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS targeted_fetch_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            content TEXT,
            source_site TEXT,
            fetch_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            relevance_score REAL DEFAULT 0.0
        )
    ''')

    conn.commit()
    conn.close()

    print(f"   Created database: {db_path}")
    print("   - universal_search_results table for SearxNG results")
    print("   - targeted_fetch_results table for targeted fetch results")


def setup_report_ready_database():
    """
    Set up the report-ready results database
    """
    db_path = "report_ready_results.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS report_ready_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            content TEXT,
            source_type TEXT,  -- 'universal' or 'targeted'
            source_details TEXT,
            relevance_score REAL,
            value_score REAL,
            category TEXT,
            added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

    print(f"   Created database: {db_path}")
    print("   - report_ready_results table for processed results")


def setup_historical_database():
    """
    Set up the historical reports database
    """
    db_path = "historical_reports.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historical_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            report_content TEXT NOT NULL,
            report_summary TEXT,
            recipient TEXT DEFAULT '3bd6edc5c6f1-im-bot',
            delivery_status TEXT DEFAULT 'pending'
        )
    ''')

    conn.commit()
    conn.close()

    print(f"   Created database: {db_path}")
    print("   - historical_reports table for archiving")


def verify_components():
    """
    Verify that all system components exist
    """
    # Check skill directories
    skill_dirs = [
        "skills/search-engine",
        "skills/result-processor",
        "skills/report-generator"
    ]

    for skill_dir in skill_dirs:
        if os.path.isdir(skill_dir):
            print(f"   OK Skill directory exists: {skill_dir}")
        else:
            print(f"   ERROR Missing skill directory: {skill_dir}")

    # Check skill files
    skill_files = [
        "skills/search-engine.skill",
        "skills/result-processor.skill",
        "skills/report-generator.skill",
        "skills/search-engine/implementation.py",
        "skills/result-processor/implementation.py",
        "skills/report-generator/implementation.py"
    ]

    for skill_file in skill_files:
        if os.path.isfile(skill_file):
            print(f"   OK Skill file exists: {skill_file}")
        else:
            print(f"   ERROR Missing skill file: {skill_file}")

    # Check cron job
    cron_file = "cron-jobs/drone-activity-tracker.json"
    if os.path.isfile(cron_file):
        print(f"   OK Cron job configuration exists: {cron_file}")
    else:
        print(f"   ERROR Missing cron job configuration: {cron_file}")

    # Check main script
    main_script = "run_activity_search.py"
    if os.path.isfile(main_script):
        print(f"   OK Main script exists: {main_script}")
    else:
        print(f"   ERROR Missing main script: {main_script}")


def main():
    """
    Main function to run system initialization
    """
    try:
        init_system()
        return 0
    except Exception as e:
        print(f"\nERROR during system initialization: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)