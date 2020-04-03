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
from config import HEADER_MAPPING, COMPANY_SCHEMA, GRX_COMPANY_SCHEMA

import click


@click.command()
@click.option(
    "--sheet", help="What sheet are we processing in the excel file?", required=False, default="Third Parties"
)
@click.argument("filename", required=False, default="assessment-orders.xlsx")
def submit_orders(sheet, filename):
    api = os.environ.get("CYBERGRX_API", "https://api.cybergrx.com").rstrip("/")
    token = os.environ.get("CYBERGRX_API_TOKEN", None)
    if not token:
        raise Exception("The environment variable CYBERGRX_API_TOKEN must be set")

    wb = load_workbook(filename)
    work_sheet = wb[sheet] if sheet in wb else wb.active
    companies = process_companies(work_sheet, HEADER_MAPPING, COMPANY_SCHEMA)

    print("Detected " + str(len(companies)) + " companies with potential orders in " + filename)
    print("")
    print("Finding all third parties in the ecosystem for order placement")
    for company in tqdm(companies, total=len(companies), desc="Find Third Parties"):
        company_name = company.get("name")
        uri = api + "/v1/third-parties?limit=1&name=" + company_name

        response = requests.get(uri, headers={"Authorization": token.strip()})
        if response.status_code is not 200:
            print(f"There was no match for {company_name} in the ecosystem")
            continue

        try:
            result = glom(json.loads(response.content.decode("utf-8")), "items", default=None)
        except:
            result = None

        if not result:
            # print(f"There was no match for {company_name} in the ecosystem")
            continue

        if len(result) is not 1:
            # print(f"There was more than 1 result for {company_name}")
            # print(result)
            continue

        company.update(glom(result[0], GRX_COMPANY_SCHEMA))

    companies_without_lookups = [c for c in companies if "url" not in c]
    if companies_without_lookups:
        print(f"\nThere were {len(companies_without_lookups)} companies that were not found or duplicated, they were:")
        for company in companies_without_lookups:
            print(f"    {company['name']}")

    companies_without_orders = [c for c in companies if "url" in c and c["subscription_status"] in [None, "New"]]
    companies_with_orders = [c for c in companies if "url" in c and c["subscription_status"] not in [None, "New"]]
    if len(companies_without_orders) != len(companies_with_orders):
        print(f"\nThere were {len(companies_with_orders)} that already had orders, here are the names:")
        for company in companies_with_orders:
            print(f"    {company['name']}")

    if not companies_without_orders:
        print("\nThere were no companies that need an order placed")
        return

    print(f"\nPlacing {len(companies_without_orders)} assessment orders")
    for company in tqdm(companies_without_orders, total=len(companies_without_orders), desc="Order Assessments"):
        company_name = company.get("name")

        uri = api + "/v1/third-parties"
        response = requests.post(uri, headers={"Authorization": token.strip()}, json=company)
        if response.status_code is 202:
            print(
                f"The order was placed for {company_name} but it is in the curation queue, must have had multiple companies with same name"
            )
            continue

        if response.status_code is not 200:
            print(f"There was an error processing the order for {company_name}")
            print(response.status_code)
            print(response.text)


if __name__ == "__main__":
    submit_orders()
