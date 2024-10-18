import sqlite3
import argparse
import atexit
from exa_py import Exa
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Exa AI API
exa = None

def initialize_exa():
    global exa
    api_key = os.getenv("EXA_API_KEY")
    if api_key:
        exa = Exa(api_key=api_key)

# Create and connect to the SQLite database
conn = sqlite3.connect('leads.db')
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS seed_urls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL UNIQUE,
        status TEXT DEFAULT 'not-started'
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL UNIQUE,
        source_url TEXT,
        status TEXT DEFAULT 'new'
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS errors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL,
        error_message TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

conn.commit()

# Functions for managing seed URLs
def add_seed_url(url):
    cursor.execute('INSERT INTO seed_urls (url) VALUES (?)', (url,))
    conn.commit()
    print(f"Added seed URL: {url}")

def remove_seed_url(url):
    cursor.execute('DELETE FROM seed_urls WHERE url = ?', (url,))
    conn.commit()
    print(f"Removed seed URL: {url}")

def check_status(url=None):
    if url:
        cursor.execute('SELECT * FROM seed_urls WHERE url = ?', (url,))
        row = cursor.fetchone()
        if row:
            print(f"ID: {row[0]}, URL: {row[1]}, Status: {row[2]}")
        else:
            print(f"No seed URL found for: {url}")
    else:
        cursor.execute('SELECT * FROM seed_urls')
        rows = cursor.fetchall()
        if not rows:
            print("No seed URLs found.")
            return
        for row in rows:
            print(f"ID: {row[0]}, URL: {row[1]}, Status: {row[2]}")

def bulk_add_urls(file_path):
    with open(file_path, 'r') as file:
        urls = file.read().splitlines()
    
    for url in urls:
        add_seed_url(url.strip())
    
    print(f"Added {len(urls)} URLs from {file_path}")

def find_similar_websites(url=None):
    if exa is None:
        print("Exa API is not initialized. Please set up your API key.")
        return

    if url:
        urls = [url]
    else:
        cursor.execute('SELECT url FROM seed_urls WHERE status = "not-started"')
        urls = [row[0] for row in cursor.fetchall()]

    for seed_url in urls:
        try:
            cursor.execute('UPDATE seed_urls SET status = "processing" WHERE url = ?', (seed_url,))
            conn.commit()

            result = exa.find_similar_and_contents(
                seed_url,
                num_results=10,
                text=True,
                summary=True,
                exclude_domains=[seed_url.split("//")[-1].split("/")[0]]
            )

            for similar_site in result:
                cursor.execute('INSERT OR IGNORE INTO leads (url, source_url) VALUES (?, ?)', 
                               (similar_site['url'], seed_url))

            cursor.execute('UPDATE seed_urls SET status = "completed" WHERE url = ?', (seed_url,))
            conn.commit()
            print(f"Found and added similar websites for: {seed_url}")

        except Exception as e:
            cursor.execute('UPDATE seed_urls SET status = "failed" WHERE url = ?', (seed_url,))
            cursor.execute('INSERT INTO errors (url, error_message) VALUES (?, ?)', (seed_url, str(e)))
            conn.commit()
            print(f"Error processing {seed_url}: {str(e)}")

def view_leads():
    cursor.execute('SELECT * FROM leads')
    leads = cursor.fetchall()
    if not leads:
        print("No leads found.")
    else:
        for lead in leads:
            print(f"ID: {lead[0]}, URL: {lead[1]}, Source: {lead[2]}, Status: {lead[3]}")

def delete_lead(lead_id):
    cursor.execute('DELETE FROM leads WHERE id = ?', (lead_id,))
    conn.commit()
    print(f"Deleted lead with ID: {lead_id}")

def view_errors():
    cursor.execute('SELECT * FROM errors')
    errors = cursor.fetchall()
    if not errors:
        print("No errors found.")
    else:
        for error in errors:
            print(f"ID: {error[0]}, URL: {error[1]}, Error: {error[2]}, Timestamp: {error[3]}")

# CLI argument parsing
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Lead Agent CLI for Seed URL Management",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--add',
        type=str,
        metavar='URL',
        help="Add a single seed URL to the database"
    )
    parser.add_argument(
        '--remove',
        type=str,
        metavar='URL',
        help="Remove a specific seed URL from the database"
    )
    parser.add_argument(
        '--status',
        nargs='?',
        const='all',
        metavar='URL',
        help="Check the status of seed URLs:\n"
             "  - Use without arguments to check all URLs\n"
             "  - Provide a specific URL to check its status"
    )
    parser.add_argument(
        '--bulk-add',
        type=str,
        metavar='FILE',
        help="Bulk add URLs from a text file (one URL per line)"
    )
    parser.add_argument(
        '--find-similar',
        type=str,
        nargs='?',
        const='all',
        metavar='URL',
        help="Find similar websites for seed URLs:\n"
             "  - Use without arguments to find similar websites for all not-started URLs\n"
             "  - Provide a specific URL to find similar websites for that URL"
    )
    parser.add_argument(
        '--view-leads',
        action='store_true',
        help="View all leads"
    )
    parser.add_argument(
        '--delete-lead',
        type=int,
        metavar='ID',
        help="Delete a lead by ID"
    )
    parser.add_argument(
        '--view-errors',
        action='store_true',
        help="View all errors"
    )
    args = parser.parse_args()

    if args.add:
        add_seed_url(args.add)
    elif args.remove:
        remove_seed_url(args.remove)
    elif args.status:
        if args.status == 'all':
            check_status()
        else:
            check_status(args.status)
    elif args.bulk_add:
        bulk_add_urls(args.bulk_add)
    elif args.find_similar:
        if args.find_similar == 'all':
            find_similar_websites()
        else:
            find_similar_websites(args.find_similar)
    elif args.view_leads:
        view_leads()
    elif args.delete_lead:
        delete_lead(args.delete_lead)
    elif args.view_errors:
        view_errors()
    else:
        parser.print_help()

# Ensure the database connection is closed when the module is unloaded
@atexit.register
def close_connection():
    conn.close()
