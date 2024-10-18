import os
import argparse
import getpass
import logging
import sqlite3  # Add this import
from dotenv import load_dotenv, set_key
from lead_agent import (
    add_seed_url, remove_seed_url, check_status, bulk_add_urls,
    find_similar_websites, view_leads, delete_lead, view_errors, initialize_exa, get_seed_urls
)
from research_crew import conduct_research, initialize_research_tools, check_leads_table

# Set up logging
logging.basicConfig(filename='lead_agent.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def print_welcome():
    print("Welcome to Lead Agent!")
    print("This tool helps you manage seed URLs and find similar websites for lead generation.")
    print("Use the commands below to interact with the program.")
    print("\nAvailable commands:")
    print("  add <URL>           - Add a single seed URL")
    print("  remove <URL>        - Remove a specific seed URL")
    print("  status [URL]        - Check status of all URLs or a specific URL")
    print("  bulk-add <FILE>     - Bulk add URLs from a text file")
    print("  find-similar        - Find similar websites for seed URLs")
    print("  view-leads          - View all leads")
    print("  delete-lead <ID>    - Delete a specific lead")
    print("  view-errors         - View all errors")
    print("  help                - Show this help message")
    print("  exit                - Exit the program")
    print("  research-leads      - Conduct research on leads")
    print("  add-test-lead        - Add a test lead to the database")
    print("  check-leads         - Check the leads table")

def setup():
    print("Welcome to Lead Agent Setup!")
    print("Let's get you set up with the necessary API keys.")
    
    exa_api_key = getpass.getpass("Please enter your Exa AI API key: ").strip()
    groq_api_key = getpass.getpass("Please enter your Groq API key: ").strip()
    apollo_api_key = getpass.getpass("Please enter your Apollo API key: ").strip()
    
    # Save the API keys to .env file
    env_file = '.env'
    set_key(env_file, 'EXA_API_KEY', exa_api_key)
    set_key(env_file, 'GROQ_API_KEY', groq_api_key)
    set_key(env_file, 'APOLLO_API_KEY', apollo_api_key)
    
    print("\nSetup complete! Your API keys have been saved.")
    print("You can now start using Lead Agent.")

def select_seed_url():
    seed_urls = get_seed_urls()
    if not seed_urls:
        print("No seed URLs found. Please add some first.")
        return None

    print("Select a seed URL:")
    print("0. All seed URLs")
    for i, url in enumerate(seed_urls, 1):
        print(f"{i}. {url}")

    while True:
        try:
            choice = int(input("Enter the number of your choice: "))
            if choice == 0:
                return seed_urls
            elif 1 <= choice <= len(seed_urls):
                return [seed_urls[choice - 1]]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def add_test_lead():
    conn = sqlite3.connect('leads.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO leads (company_name, website, status)
        VALUES (?, ?, ?)
    ''', ('Test Company', 'https://www.atouchofclassbridal.com/', 'new'))
    conn.commit()
    conn.close()
    print("Test lead added to the database")

def main():
    # Check if .env file exists and contains all required API keys
    required_keys = ['EXA_API_KEY', 'GROQ_API_KEY', 'APOLLO_API_KEY']
    if not os.path.exists('.env') or not all(key in os.environ for key in required_keys):
        setup()
    
    load_dotenv()  # Reload environment variables
    initialize_exa()  # Initialize Exa API client
    initialize_research_tools()  # Initialize research tools
    
    print_welcome()

    while True:
        command = input("\nEnter a command: ").strip().split()

        if not command:
            continue

        action = command[0].lower()

        if action == 'exit':
            print("Thank you for using Lead Agent. Goodbye!")
            break
        elif action == 'help':
            print_welcome()
        elif action == 'add' and len(command) == 2:
            add_seed_url(command[1])
        elif action == 'remove' and len(command) == 2:
            remove_seed_url(command[1])
        elif action == 'status':
            if len(command) == 1:
                check_status()
            elif len(command) == 2:
                check_status(command[1])
            else:
                print("Invalid usage. Use 'status' or 'status <URL>'")
        elif action == 'bulk-add' and len(command) == 2:
            bulk_add_urls(command[1])
        elif action == 'find-similar':
            urls = select_seed_url()
            if urls:
                for url in urls:
                    find_similar_websites(url)
        elif action == 'view-leads':
            view_leads()
        elif action == 'delete-lead' and len(command) == 2:
            try:
                delete_lead(int(command[1]))
            except ValueError:
                print("Invalid lead ID. Please provide a valid integer.")
        elif action == 'view-errors':
            view_errors()
        elif action == 'research-leads':
            print("Starting research process...")
            conduct_research()
            print("Research process completed.")
        elif action == 'add-test-lead':
            add_test_lead()
        elif action == 'check-leads':
            all_leads = check_leads_table()
            for lead in all_leads:
                print(f"ID: {lead[0]}, Company: {lead[1]}, Website: {lead[2]}, Status: {lead[3]}")
        else:
            print("Invalid command. Type 'help' for usage information.")

if __name__ == "__main__":
    main()
