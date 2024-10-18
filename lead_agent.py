import sqlite3
import argparse

# Create and connect to the SQLite database
conn = sqlite3.connect('leads.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS seed_urls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL,
        status TEXT DEFAULT 'not-started'
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
    else:
        parser.print_help()

# Close the database connection
conn.close()
