#########################################################################
#    _________        ___.                   ______________________  ___
#    \_   ___ \___.__.\_ |__   ___________  /  _____/\______   \   \/  /
#    /    \  \<   |  | | __ \_/ __ \_  __ \/   \  ___ |       _/\     /
#    \     \___\___  | | \_\ \  ___/|  | \/\    \_\  \|    |   \/     \
#     \______  / ____| |___  /\___  >__|    \______  /|____|_  /___/\  \
#            \/\/          \/     \/               \/        \/      \_/
#
#

import os
import json
import requests
from openpyxl import Workbook, load_workbook
from tqdm import tqdm
from utils import process_companies
from glom import glom, Coalesce, OMIT

import click

VALID_ANSWERS = {
    "least": "Least",
    "minimal": "Minimal",
    "moderate": "Moderate",
    "significant": "Significant",
}

def validate_answer(value):
    if not value:
        return OMIT

    answer = VALID_ANSWERS.get(str(value).strip().lower(), None)
    return answer if answer else OMIT

HEADER_MAPPING = {
    "Company Name": "name",
    "Digital Identities": "digital_identities",
    "People": "people",
    "Data": "data",
    "Applications": "applications",
    "Devices": "devices",
    "Networks": "networks",
    "Facilities": "facilities",
    "Business Process": "business_process",
}

COMPANY_SCHEMA = {
    "name": "name",
    "digital_identities": Coalesce(("digital_identities", validate_answer), default=OMIT),
    "people": Coalesce(("people", validate_answer), default=OMIT),
    "data": Coalesce(("data", validate_answer), default=OMIT),
    "applications": Coalesce(("applications", validate_answer), default=OMIT),
    "devices": Coalesce(("devices", validate_answer), default=OMIT),
    "networks": Coalesce(("networks", validate_answer), default=OMIT),
    "facilities": Coalesce(("facilities", validate_answer), default=OMIT),
    "business_process": Coalesce(("business_process", validate_answer), default=OMIT),

}


@click.command()
@click.option('--sheet', help='What sheet are we processing in the excel file?', required=False, default="Third Parties")
@click.argument('filename', required=False, default="profile-answers.xlsx")
def create_tags(sheet, filename):
    api = os.environ.get('CYBERGRX_API', "https://api.cybergrx.com").rstrip("/")
    token = os.environ.get('CYBERGRX_API_TOKEN', None)
    if not token:
        raise Exception("The environment variable CYBERGRX_API_TOKEN must be set")

    wb = load_workbook(filename)
    companies = process_companies(wb[sheet], HEADER_MAPPING, COMPANY_SCHEMA)

    print("Detected " + str(len(companies)) + " companies with profile answers in " + filename)
    for company in tqdm(companies, total=len(companies), desc="Third Party Tagging"):
        company_name = company.pop("name")
        uri = api + "/v1/third-parties?limit=1&name=" + company_name
        
        response = requests.get(uri, headers={'Authorization': token.strip()})
        result = json.loads(response.content.decode('utf-8'))

        third_party_id = glom(result, "items.0.id", default=None)
        if third_party_id:
            uri = api + "/v1/third-parties/" + third_party_id + "/scoping"
            response = requests.put(uri, headers={'Authorization': token.strip()}, json=company)
            if response.status_code != 200:
                print("Error submitting scoping profile answers for " + company_name)
                print(response.content)

if __name__ == '__main__':
    create_tags()
