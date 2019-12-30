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
from glom import glom, Coalesce

import click


@click.command()
@click.option('--company-header', prompt='Company Name', help='Header identifying the column that contains company names', required=True)
@click.option('--tag-header', prompt="Tags", help='Header identifying the column that contains tags', required=True)
@click.option('--sheet', prompt="Third Parties", help='What sheet are we processing in the excel file?', required=True)
@click.argument('filename')
def create_tags(company_header, tag_header, sheet, filename):
    api = os.environ.get('CYBERGRX_API', "https://api.cybergrx.com").rstrip("/")
    token = os.environ.get('CYBERGRX_API_TOKEN', None)
    if not token:
        raise Exception("The environment variable CYBERGRX_API_TOKEN must be set")

    wb = load_workbook(filename)
    companies = process_companies(wb[sheet], {company_header: "name", tag_header: "tags"})

    print("Detected " + str(len(companies)) + " companies with tags in " + filename)
    for company in tqdm(companies, total=len(companies), desc="Third Party Tagging"):
        uri = api + "/v1/third-parties?limit=1&name=" + company["name"]
        
        response = requests.get(uri, headers={'Authorization': token.strip()})
        result = json.loads(response.content.decode('utf-8'))

        third_party_id = glom(result, "items.0.id", default=None)
        if third_party_id:
            uri = api + "/v1/third-parties/" + third_party_id + "/tagging"
            requests.put(uri, headers={'Authorization': token.strip()}, json={"tags": company["tags"]})

if __name__ == '__main__':
    create_tags()
