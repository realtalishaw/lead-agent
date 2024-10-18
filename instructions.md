# Project Overview

You are building a command-line tool called Lead Agent. Lead Agent is a research and analysis tool that allows users to add seed URLs, remove seed URLs, check the status of seed URLs, research and extract information from seed URLs, find similar websites to seed URLs, find contact information for websites and people, add the information they've collected to their CRM, export the information they've collected to a CSV file, send an email to the contact information they've collected, and send a follow up email to the contact information they've collected.

You will be using Python 3.12 and the following libraries:
- Exa AI API
- OpenAI API
- Groq API
- Serper API
- Beautiful Soup
- Requests
- CSV
- OS
- Time
- Crew AI
- Colorama
- Rich
- HubSpot API
- Apollo.io API

The information Lead Agent collects is as follows:
- Company Name
- Contact Name
- Contact Email
- Contact Phone
- Address
- Website
- Description
- Revenue
- Number of Employees
- Industry
- Similar Websites
- Why They Are a Lead
- Any Additional Information


# Core Functionalities

- **Add Seed URLs**: Users can add individual URLs or bulk add URLs from a text file.
- **Remove Seed URLs**: Users can remove specific URLs from the database.
- **Check Status**: Users can check the status of individual or all seed URLs. Along with the status of any leads.
- **Research and Extract Information**: Users can research and extract information from seed URLs.
- **Find Similar Websites**: Users can find similar websites to seed URLs.
- **Find Contact Information**: Users can find contact information for websites and people.
- **Add to CRM**: Users can add the information they've collected to their CRM.
- **Export to CSV**: Users can export the information they've collected to a CSV file.
- **Send Email**: Users can send an email to the contact information they've collected.
- **Follow Up Email**: Users can send a follow up email to the contact information they've collected.


# Documentation
## Exa AI API
from exa_py import Exa

exa = Exa(api_key="e0ab2023-359a-4588-a059-19ffc73e45f4")

result = exa.find_similar_and_contents(
  "https://www.supergiantgames.com",
  num_results=10,
  text=True,
  summary=True,
  exclude_domains=["supergiantgames.com"]
)



# Current File Structure