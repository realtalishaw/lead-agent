import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import json
import sqlite3
from groq import Groq
import logging

# Set up logging
logging.basicConfig(filename='lead_agent.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Initialize API clients
groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
APOLLO_API_KEY = os.getenv('APOLLO_API_KEY')

def scrape_website(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extract text from paragraphs, headings, and other relevant tags
        text = ' '.join([tag.get_text() for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])])
        return text
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return ""

def extract_info_with_groq(text):
    prompt = f"""
    Extract the following information from the given text. If the information is not available, write "Not found":
    
    - Company Name
    - Description
    - Industry
    - Number of Employees
    - Revenue
    - Address
    
    Text: {text}
    
    Provide the answer in JSON format.
    """
    
    try:
        completion = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,
            max_tokens=1000,
            top_p=1,
            stream=False,
            stop=None
        )
        
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        logging.error(f"Error in Groq API call: {str(e)}")
        return {"error": str(e)}

def find_contacts_with_apollo(company_name):
    url = "https://api.apollo.io/v1/mixed_people/search"
    
    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "X-Api-Key": APOLLO_API_KEY
    }
    
    data = {
        "q_organization_name": company_name,
        "page": 1,
        "per_page": 5
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        search_response = response.json()
        
        contacts = []
        for person in search_response.get('people', []):
            contact = {
                'name': f"{person.get('first_name', '')} {person.get('last_name', '')}",
                'email': person.get('email', 'Not found'),
                'phone': person.get('phone_number', 'Not found'),
                'title': person.get('title', 'Not found')
            }
            contacts.append(contact)
        
        return contacts
    except Exception as e:
        print(f"Error finding contacts for {company_name}: {str(e)}")
        return []

def get_leads_from_db():
    conn = sqlite3.connect('leads.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, company_name, website FROM leads WHERE status = "new"')
    leads = cursor.fetchall()
    conn.close()
    
    logging.info(f"Retrieved {len(leads)} leads from the database")
    if not leads:
        logging.warning("No leads with 'new' status found in the database")
    else:
        for lead in leads:
            logging.info(f"Lead found: ID={lead[0]}, Company={lead[1]}, Website={lead[2]}")
    
    return leads

def update_lead_in_db(lead_id, info):
    conn = sqlite3.connect('leads.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE leads
        SET status = ?, additional_info = ?
        WHERE id = ?
    ''', ('researched', json.dumps(info), lead_id))
    conn.commit()
    conn.close()

def conduct_research():
    logging.info("Starting research process")
    check_leads_table()  # Add this line
    leads = get_leads_from_db()
    logging.info(f"Found {len(leads)} leads to research")
    
    for lead_id, company_name, website in leads:
        logging.info(f"Researching: {company_name}")
        print(f"Researching: {company_name}")
        
        try:
            # Scrape website
            scraped_text = scrape_website(website)
            logging.info(f"Scraped {len(scraped_text)} characters from {website}")
            
            # Extract info with Groq
            extracted_info = extract_info_with_groq(scraped_text)
            logging.info(f"Extracted info using Groq: {json.dumps(extracted_info)}")
            
            # Find contacts with Apollo
            contacts = find_contacts_with_apollo(company_name)
            logging.info(f"Found {len(contacts)} contacts using Apollo")
            
            # Combine all information
            full_info = {
                **extracted_info,
                'website': website,
                'contacts': contacts
            }
            
            # Update the lead in the database
            update_lead_in_db(lead_id, full_info)
            
            logging.info(f"Research completed for {company_name}")
            print(f"Research completed for {company_name}")
            print(json.dumps(full_info, indent=2))
            print("\n" + "="*50 + "\n")
        
        except Exception as e:
            logging.error(f"Error researching {company_name}: {str(e)}")
            print(f"Error researching {company_name}: {str(e)}")
            update_lead_in_db(lead_id, {"error": str(e)})
    
    logging.info("Research process completed")

def initialize_research_tools():
    logging.info("Initializing research tools")
    if not os.getenv('APOLLO_API_KEY'):
        logging.error("APOLLO_API_KEY not found in environment variables")
        raise ValueError("APOLLO_API_KEY not found in environment variables")
    if not os.getenv('GROQ_API_KEY'):
        logging.error("GROQ_API_KEY not found in environment variables")
        raise ValueError("GROQ_API_KEY not found in environment variables")
    logging.info("Research tools initialized successfully")

def check_leads_table():
    conn = sqlite3.connect('leads.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, company_name, website, status FROM leads')
    all_leads = cursor.fetchall()
    conn.close()
    
    logging.info(f"Total leads in the database: {len(all_leads)}")
    for lead in all_leads:
        logging.info(f"Lead: ID={lead[0]}, Company={lead[1]}, Website={lead[2]}, Status={lead[3]}")
    
    return all_leads

if __name__ == "__main__":
    initialize_research_tools()
    conduct_research()
