import sqlite3
import argparse
import atexit
from exa_py import Exa
import os
import logging
from dotenv import load_dotenv
import json

# Set up logging
logging.basicConfig(filename='lead_agent.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Initialize Exa AI API
exa = None

def initialize_exa():
    global exa
    api_key = os.getenv("EXA_API_KEY")
    if api_key:
        exa = Exa(api_key=api_key)
        logging.info("Exa API initialized successfully")
    else:
        logging.warning("Exa API key not found")

# Create and connect to the SQLite database
conn = sqlite3.connect('leads.db')
cursor = conn.cursor()

# Drop the existing leads table if it exists
cursor.execute('DROP TABLE IF EXISTS leads')

# Create the leads table with the correct structure
cursor.execute('''
    CREATE TABLE leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT,
        website TEXT NOT NULL UNIQUE,
        source_url TEXT,
        status TEXT DEFAULT 'new',
        additional_info TEXT,
        score REAL
    )
''')
conn.commit()

# Create tables if they don't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS seed_urls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL UNIQUE,
        status TEXT DEFAULT 'not-started'
    )
''')

# Modify the leads table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT,
        website TEXT NOT NULL UNIQUE,
        source_url TEXT,
        status TEXT DEFAULT 'new',
        additional_info TEXT,
        score REAL
    )
''')
conn.commit()

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
    logging.info(f"Added seed URL: {url}")
    print(f"Added seed URL: {url}")

def remove_seed_url(url):
    cursor.execute('DELETE FROM seed_urls WHERE url = ?', (url,))
    conn.commit()
    logging.info(f"Removed seed URL: {url}")
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
    
    logging.info(f"Added {len(urls)} URLs from {file_path}")
    print(f"Added {len(urls)} URLs from {file_path}")

def find_similar_websites(url):
    if exa is None:
        logging.error("Exa API is not initialized. Please set up your API key.")
        print("Exa API is not initialized. Please set up your API key.")
        return

    try:
        logging.info(f"Starting to find similar websites for: {url}")
        print(f"Starting to find similar websites for: {url}")

        cursor.execute('UPDATE seed_urls SET status = "processing" WHERE url = ?', (url,))
        conn.commit()

        result = exa.find_similar_and_contents(
            url,
            num_results=10,
            text=True,
            summary=True,
            exclude_domains=[url.split("//")[-1].split("/")[0]]
        )

        # Process and save the results
        if hasattr(result, 'results') and isinstance(result.results, list):
            for similar_site in result.results:
                cursor.execute('''
                    INSERT OR REPLACE INTO leads 
                    (company_name, website, source_url, status, additional_info, score) 
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    getattr(similar_site, 'title', ''),
                    similar_site.url,
                    url,
                    'new',
                    json.dumps({
                        'text': getattr(similar_site, 'text', ''),
                        'summary': getattr(similar_site, 'summary', '')
                    }),
                    getattr(similar_site, 'score', 0)
                ))
                logging.info(f"Added/Updated similar website: {similar_site.url}")
                print(f"Added/Updated similar website: {similar_site.url}")
            
            print(f"Added {len(result.results)} similar websites for {url}")
            logging.info(f"Added {len(result.results)} similar websites for {url}")
        else:
            logging.warning(f"No results found for {url}")
            print(f"No results found for {url}")

        cursor.execute('UPDATE seed_urls SET status = "completed" WHERE url = ?', (url,))
        conn.commit()
        logging.info(f"Completed finding similar websites for: {url}")
        print(f"Completed finding similar websites for: {url}")

    except Exception as e:
        cursor.execute('UPDATE seed_urls SET status = "failed" WHERE url = ?', (url,))
        cursor.execute('INSERT INTO errors (url, error_message) VALUES (?, ?)', (url, str(e)))
        conn.commit()
        logging.error(f"Error processing {url}: {str(e)}")
        print(f"Error processing {url}: {str(e)}")

def view_leads():
    cursor.execute('SELECT * FROM leads')
    leads = cursor.fetchall()
    if not leads:
        print("No leads found.")
    else:
        for lead in leads:
            print(f"ID: {lead[0]}")
            print(f"Company Name: {lead[1]}")
            print(f"Website: {lead[2]}")
            print(f"Source: {lead[3]}")
            print(f"Status: {lead[4]}")
            additional_info = json.loads(lead[5])
            print(f"Summary: {additional_info.get('summary', 'N/A')}")
            print(f"Score: {lead[6]}")
            print("---")

def delete_lead(lead_id):
    cursor.execute('DELETE FROM leads WHERE id = ?', (lead_id,))
    conn.commit()
    logging.info(f"Deleted lead with ID: {lead_id}")
    print(f"Deleted lead with ID: {lead_id}")

def view_errors():
    cursor.execute('SELECT * FROM errors')
    errors = cursor.fetchall()
    if not errors:
        print("No errors found.")
    else:
        for error in errors:
            print(f"ID: {error[0]}, URL: {error[1]}, Error: {error[2]}, Timestamp: {error[3]}")

def get_seed_urls():
    cursor.execute('SELECT url FROM seed_urls')
    return [row[0] for row in cursor.fetchall()]

# Ensure the database connection is closed when the module is unloaded
@atexit.register
def close_connection():
    conn.close()
    logging.info("Database connection closed")
