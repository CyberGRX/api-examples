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
import re
import json
import requests
import smartsheet
import stringcase
from openpyxl import Workbook, load_workbook
from tqdm import tqdm
from utils import split, normalize_vendor, lookup_sheet_id, skip_falsy, insert_http
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

    normalized = str(value).strip().lower()
    for key in VALID_ANSWERS.keys():
        if normalized.startswith(key):
            return VALID_ANSWERS[key]

    return OMIT

HEADER_MAPPING = {
    "Vendor Name": "company_name",
    "Vendor URL": "company_url",

    # Address metadata (need at least a city to create a company)
    "Vendor HQ City": "address_city",

    # Internal Metadata
    "Vendor Owner": "internal_vendor_owner",
    "Description": "internal_description",
    "Location": "internal_location",

    # Third Party Contact Info
    "Vendor Contact Name": "third_party_contact_name",
    "Vendor Contact Email": "third_party_contact_email",
    "Vendor Contact Phone": "third_party_contact_phone",

    # Cyber classification metadata
    "Critical/Support": "meta_is_critical_or_support",
    "RTO": "meta_rto",
    "Data Sensitivity": "meta_data_sensitivity",
    "Legal/Regulatory Compliance": "meta_compliance",
    "Technology Risk": "meta_tech_risk",
    "Influence": "meta_influence",

    # Profile questions
    "Digital Identities": "profile_digital_identities",
    "People": "profile_people",
    "Data": "profile_data",
    "Applications": "profile_applications",
    "Devices": "profile_devices",
    "Network Access": "profile_networks",
    "Facilities": "profile_facilities",
    "Business Process": "profile_business_process",

    # CyberGRX Risk Analysis
    "Impact": "impact",
    "Likelihood": "likelihood",
}

COMPANY_SCHEMA = {
    "name": "company_name",
    "url": ("company_url", insert_http),

    "address": {
        "city": "address_city",
    },

    "third_party_contact": {
        "first_name": Coalesce(("third_party_contact_name", split(0), skip_falsy), default=OMIT),
        "last_name": Coalesce(("third_party_contact_name", split(1), skip_falsy), default=OMIT),
        "email": Coalesce(("third_party_contact_email", skip_falsy), default=OMIT),
        "phone": Coalesce(("third_party_contact_phone", skip_falsy), default=OMIT),
    },

    "third_party_scoping": {
        "digital_identities": Coalesce(("profile_digital_identities", validate_answer), default=OMIT),
        "people": Coalesce(("profile_people", validate_answer), default=OMIT),
        "data": Coalesce(("profile_data", validate_answer), default=OMIT),
        "applications": Coalesce(("profile_applications", validate_answer), default=OMIT),
        "devices": Coalesce(("profile_devices", validate_answer), default=OMIT),
        "networks": Coalesce(("profile_networks", validate_answer), default=OMIT),
        "facilities": Coalesce(("profile_facilities", validate_answer), default=OMIT),
        "business_process": Coalesce(("profile_business_process", validate_answer), default=OMIT),
    },

    "custom_metadata": {
        "internal": {
            "owner": "internal_vendor_owner",
            "description": "internal_description",
            "location": "internal_description"
        },
        "cyber_classification": {
            "critical_or_support": "meta_is_critical_or_support",
            "rto": "meta_rto",
            "data_sensitivity": "meta_data_sensitivity",
            "compliance": "meta_compliance",
            "tech_risk": "meta_tech_risk",
            "influence": "meta_influence",
        }
    },
}

GRX_COMPANY_SCHEMA = {
    "id": "id", 
    "name": "name", 
    "custom_id": "custom_id",
    "is_profile_complete": "subscription.is_profile_complete",
    "impact": "inherent_risk.impact_label",
    "likelihood": "inherent_risk.likelihood_label",
}

def process_missing_vendors(missing_vendors, token, api):
    for missing in tqdm(missing_vendors, total=len(missing_vendors), desc="Create missing vendors"):
        uri = api + "/v1/third-parties?&name=" + missing["name"]
        response = requests.get(uri, headers={'Authorization': token.strip()})
        result = json.loads(response.content.decode('utf-8'))
        matches = glom(result, "items", default=[])

        if not matches:
            uri = api + "/v1/third-parties?&domain=" + missing["url"]
            response = requests.get(uri, headers={'Authorization': token.strip()})
            result = json.loads(response.content.decode('utf-8'))
            matches = glom(result, "items", default=[])

        if len(matches) > 1:
            print("Multiple GRX records matched "+ missing["name"])
            continue

        if len(matches) == 1:
            if glom(matches, "0.custom_id", default=None):
                print("Found a GRX record that had a different custom_id for " + missing["name"])
                continue

            # Found one company in CyberGRX that does not have a custom_id, link these records up
            uri = api + glom(matches, "0.uri") + "/custom-id"
            response = requests.put(uri, headers={'Authorization': token.strip()}, json={"custom_id": missing["custom_id"]})
            if response.status_code != 200:
                print("Error submitting custom_id for " + missing["name"])
                print(response.content)

            uri = api + glom(matches, "0.uri") + "/custom-metadata"
            response = requests.patch(uri, headers={'Authorization': token.strip(), "Content-Type": "application/merge-patch+json"}, json=missing["custom_metadata"])
            if response.status_code != 200:
                print("Error submitting custom_metadata for " + missing["name"])
                print(response.content)

            continue
            
        if not matches:       
            uri = api + "/v1/third-parties"
            response = requests.post(uri, headers={'Authorization': token.strip()}, json=missing)
            if response.status_code not in [200, 202]:
                print("Error submitting GRX vendor request for " + missing["name"])
                print(response.content)


def process_profile_updates(matched_vendors, token, api):
    for vendor in tqdm(matched_vendors, total=len(matched_vendors), desc="Submit profile questions"):
        third_party_id = vendor["grx"]["id"]
        uri = api + "/v1/third-parties/" + third_party_id + "/scoping"
        response = requests.put(uri, headers={'Authorization': token.strip()}, json=vendor["third_party_scoping"])
        if response.status_code != 200:
            print("Error submitting scoping profile answers for " + vendor["name"])
            print(response.content)


def process_matched_vendors(matched_vendors, token, sheet_id, api, smart):
    row_updates = []
    for vendor in tqdm(matched_vendors, total=len(matched_vendors), desc="Compute risk updates"):
        impact = smart.models.Cell()
        impact.column_id = HEADER_MAPPING["Impact"]
        impact.value = vendor["grx"]["impact"]

        likelihood = smart.models.Cell()
        likelihood.column_id = HEADER_MAPPING["Likelihood"]
        likelihood.value = vendor["grx"]["likelihood"]

        row_update = smart.models.Row()
        row_update.id = int(vendor["custom_id"])
        row_update.cells.append(impact)
        row_update.cells.append(likelihood)

        row_updates.append(row_update)
        
    print(row_updates)
    smart.Sheets.update_rows(sheet_id, row_updates)



@click.command()
@click.option('--sheet-name', help="Name of the sheet we are using", required=False)
@click.option('--sheet-id', help="ID of the sheet we are using", required=False)
@click.argument('filename', required=False, default="profile-answers.xlsx")
def sync_smart_sheet(sheet_name, sheet_id, filename):
    api = os.environ.get('CYBERGRX_API', "https://api.cybergrx.com").rstrip("/")
    token = os.environ.get('CYBERGRX_API_TOKEN', None)
    if not token:
        raise Exception("The environment variable CYBERGRX_API_TOKEN must be set")

    if not os.environ.get("SMARTSHEET_ACCESS_TOKEN", None):
        raise Exception("The environment variable SMARTSHEET_ACCESS_TOKEN must be set")

    if not sheet_id and not sheet_name:
        raise Exception("Either --sheet-name or --sheet-id must be provided")

    smart = smartsheet.Smartsheet()
    smart.errors_as_exceptions(True)

    # If sheet_id was not provided, lookup the ID using the sheet name
    if not sheet_id:
        sheet_id = lookup_sheet_id(smart, sheet_name)

    # Load the entire sheet
    sheet = smart.Sheets.get_sheet(sheet_id)
    print("Loaded " + str(len(sheet.rows)) + " rows from sheet: " + sheet.name)

    # Build column map for later reference - translates column names to smart sheet column ids
    for column in sheet.columns:
        if column.title in HEADER_MAPPING:
            HEADER_MAPPING[column.id] = HEADER_MAPPING[column.title]
            HEADER_MAPPING[column.title] = column.id
        else:
            snake_header = stringcase.snakecase(re.sub(r"[^0-9a-zA-Z]+", '', column.title))
            HEADER_MAPPING[column.id] = snake_header
            HEADER_MAPPING[snake_header] = column.id

    # Load all vendors from smart sheet                
    smart_sheet_vendors = [normalize_vendor(vendor, HEADER_MAPPING, COMPANY_SCHEMA) for vendor in sheet.rows]

    # Load all third parties skipping residual risk 
    uri = api + "/bulk-v1/third-parties?skip_residual_risk=true"
    print("Fetching third parties from " + uri + " this can take some time.")
    response = requests.get(uri, headers={'Authorization': token.strip()})
    grx_vendors = glom(json.loads(response.content.decode('utf-8')), ([GRX_COMPANY_SCHEMA]))
    grx_custom_ids = set([v["custom_id"] for v in grx_vendors if v["custom_id"]])

    # See which vendors in smart sheets do not have a corresponding custom_id in CyberGRX
    missing_vendors = [vendor for vendor in smart_sheet_vendors if vendor["custom_id"] not in grx_custom_ids]
    if missing_vendors:
        print("There are vendors in smart sheet that need to be migrated to CyberGRX")
        process_missing_vendors(missing_vendors, token, api)

    grx_vendor_map = {vendor["custom_id"]: vendor for vendor in grx_vendors}
    matched_vendors = [vendor for vendor in smart_sheet_vendors if vendor["custom_id"] in grx_custom_ids]
    for vendor in matched_vendors:
        vendor["grx"] = grx_vendor_map[vendor["custom_id"]]

    # Vendors that do not haave a complete profile, need to be updated
    vendors_with_profile = [vendor for vendor in matched_vendors if not vendor["grx"]["is_profile_complete"]]
    if vendors_with_profile:
        print("There are vendors with profile questions that need to be answered in CyberGRX")
        process_profile_updates(vendors_with_profile, token, api)

    # For vendors that have matches, sync their risk back to smart sheets
    if matched_vendors:
        print("There are vendors that need to sync risk profiles back to smart sheets")
        process_matched_vendors(matched_vendors, token, sheet_id, api, smart)

if __name__ == '__main__':
    sync_smart_sheet()
