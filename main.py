import os
import argparse
from dotenv import load_dotenv, set_key
from lead_agent import (
    add_seed_url, remove_seed_url, check_status, bulk_add_urls,
    find_similar_websites, view_leads, delete_lead, view_errors, initialize_exa
)

def print_welcome():
    print("Welcome to Lead Agent!")
    print("This tool helps you manage seed URLs and find similar websites for lead generation.")
    print("Use the commands below to interact with the program.")
    print("\nAvailable commands:")
    print("  add <URL>           - Add a single seed URL")
    print("  remove <URL>        - Remove a specific seed URL")
    print("  status [URL]        - Check status of all URLs or a specific URL")
    print("  bulk-add <FILE>     - Bulk add URLs from a text file")
    print("  find-similar [URL]  - Find similar websites for all seed URLs or a specific URL")
    print("  view-leads          - View all leads")
    print("  delete-lead <ID>    - Delete a specific lead")
    print("  view-errors         - View all errors")
    print("  help                - Show this help message")
    print("  exit                - Exit the program")

def setup():
    print("Welcome to Lead Agent Setup!")
    print("Let's get you set up with the necessary API keys.")
    
    exa_api_key = input("Please enter your Exa AI API key: ").strip()
    
    # Save the API key to .env file
    env_file = '.env'
    set_key(env_file, 'EXA_API_KEY', exa_api_key)
    
    print("\nSetup complete! Your API key has been saved.")
    print("You can now start using Lead Agent.")

def main():
    # Check if .env file exists and contains EXA_API_KEY
    if not os.path.exists('.env') or 'EXA_API_KEY' not in os.environ:
        setup()
    
    load_dotenv()  # Reload environment variables
    initialize_exa()  # Initialize Exa API client
    
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
            if len(command) == 1:
                find_similar_websites()
            elif len(command) == 2:
                find_similar_websites(command[1])
            else:
                print("Invalid usage. Use 'find-similar' or 'find-similar <URL>'")
        elif action == 'view-leads':
            view_leads()
        elif action == 'delete-lead' and len(command) == 2:
            try:
                delete_lead(int(command[1]))
            except ValueError:
                print("Invalid lead ID. Please provide a valid integer.")
        elif action == 'view-errors':
            view_errors()
        else:
            print("Invalid command. Type 'help' for usage information.")

if __name__ == "__main__":
    main()
