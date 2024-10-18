import argparse
from lead_agent import add_seed_url, remove_seed_url, check_status, bulk_add_urls

def print_welcome():
    print("Welcome to Lead Agent!")
    print("This tool helps you manage seed URLs for lead generation.")
    print("Use the commands below to interact with the program.")
    print("\nAvailable commands:")
    print("  add <URL>           - Add a single seed URL")
    print("  remove <URL>        - Remove a specific seed URL")
    print("  status [URL]        - Check status of all URLs or a specific URL")
    print("  bulk-add <FILE>     - Bulk add URLs from a text file")
    print("  help                - Show this help message")
    print("  exit                - Exit the program")

def main():
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
        else:
            print("Invalid command. Type 'help' for usage information.")

if __name__ == "__main__":
    main()
