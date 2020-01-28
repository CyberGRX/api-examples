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
from datetime import datetime, timedelta
from openpyxl import Workbook, load_workbook
from tqdm import tqdm
from utils import (
    split,
    normalize_vendor,
    lookup_sheet_id,
    skip_falsy,
    insert_http,
    validate_answer,
    sheet_writer,
    row_to_vendor,
)
from config import HEADER_MAPPING, SMART_SHEET_UPDATE_COLUMNS, COMPANY_SCHEMA, GRX_COMPANY_SCHEMA, BULK_IMPORT_COLUMNS
from glom import glom, Coalesce, OMIT

import click


def process_newly_matched_vendor(missing, matches, token, api):
    if glom(matches, "0.custom_id", default=None):
        print("Found a GRX record that had a different custom_id for " + missing["name"])
        return

    # Found one company in CyberGRX that does not have a custom_id, link these records up
    uri = api + glom(matches, "0.uri") + "/custom-id"
    response = requests.put(uri, headers={"Authorization": token.strip()}, json={"custom_id": missing["custom_id"]})
    if response.status_code != 200:
        print("Error submitting custom_id for " + missing["name"])
        print(response.content)

    if "custom_metadata" in missing:
        # Apply custom metadata
        uri = api + glom(matches, "0.uri") + "/custom-metadata"
        response = requests.patch(
            uri,
            headers={"Authorization": token.strip(), "Content-Type": "application/merge-patch+json"},
            json=missing["custom_metadata"],
        )
        if response.status_code != 200:
            print("Error submitting custom_metadata for " + missing["name"])
            print(response.content)

    # Apply scoping profile
    if "third_party_scoping" in missing:
        third_party_id = glom(matches, "0.id")
        apply_scoping_profile(third_party_id, missing["name"], missing["third_party_scoping"], token, api)


def process_missing_vendors(missing_vendors, skip_rows_without_orders, token, api, sheet_id, smart):
    row_updates = []
    today = datetime.today()

    for missing in tqdm(missing_vendors, total=len(missing_vendors), desc="Create missing vendors"):
        uri = api + "/v1/third-parties?name=" + missing["name"]
        response = requests.get(uri, headers={"Authorization": token.strip()})
        if response.status_code not in [200]:
            print("Error looking up third party by name " + missing["name"])
            print(response.content)
            matches = []
        else:
            result = json.loads(response.content.decode("utf-8"))
            matches = glom(result, "items", default=[])

        if not matches:
            domain = missing["url"]
            if "://" in domain:
                domain = domain.split("://", 1)[1]

            uri = api + "/v1/third-parties?domain=" + domain
            response = requests.get(uri, headers={"Authorization": token.strip()})
            if response.status_code not in [200]:
                print("Error looking up third party by url " + missing["url"])
                print(response.content)
            else:
                result = json.loads(response.content.decode("utf-8"))
                matches = glom(result, "items", default=[])

        if len(matches) > 1:
            print("Multiple GRX records matched " + missing["name"])
            continue

        if len(matches) == 1:
            # Found a single match within the CyberGRX ecosystem that has not been linked back to SmartSheets
            process_newly_matched_vendor(missing, matches, token, api)
            continue

        if not matches:
            if skip_rows_without_orders and "order_info" not in missing:
                # This company does not have order info, do not ingest it in CyberGRX yet
                continue

            # This company must be added to the CyberGRX ecosystem
            ingest_date = missing.pop("ingest_date")
            if ingest_date and ingest_date + timedelta(days=7) >= today:
                # The record has been recently added to CyberGRX, skip it
                continue

            uri = api + "/v1/third-parties"
            response = requests.post(uri, headers={"Authorization": token.strip()}, json=missing)
            if response.status_code not in [200, 202]:
                print("Error submitting GRX vendor request for " + missing["name"])
                print(response.content)
            else:
                ingest_date_cell = smart.models.Cell()
                ingest_date_cell.column_id = HEADER_MAPPING["Ingest Date"]
                ingest_date_cell.value = today.strftime("%Y-%m-%d")

                row_update = smart.models.Row()
                row_update.id = int(missing["custom_id"])
                row_update.cells.append(ingest_date_cell)

                row_updates.append(row_update)

    if row_updates:
        # If we have submitted records to CyberGRX, track those updates in the smart sheet
        smart.Sheets.update_rows(sheet_id, row_updates)


def apply_scoping_profile(third_party_id, third_party_name, scoping_profile, token, api):
    if not scoping_profile:
        return

    uri = api + "/v1/third-parties/" + third_party_id + "/scoping"
    response = requests.put(uri, headers={"Authorization": token.strip()}, json=scoping_profile)
    if response.status_code != 200:
        print("Error submitting scoping profile answers for " + third_party_name)
        print(response.content)


def process_vendors_with_profile_updates(matched_vendors, token, api):
    for vendor in tqdm(matched_vendors, total=len(matched_vendors), desc="Submit profile questions"):
        if "third_party_scoping" in vendor:
            apply_scoping_profile(vendor["grx"]["id"], vendor["name"], vendor["third_party_scoping"], token, api)

def smart_sheet_cell_update(value, column_id, row_update, smart):
    if value is not None:
        cell = smart.models.Cell()
        cell.value = value
        cell.column_id = column_id
        row_update.cells.append(cell)



def process_matched_vendors(matched_vendors, token, sheet_id, api, smart):
    row_updates = []
    for vendor in tqdm(matched_vendors, total=len(matched_vendors), desc="Compute risk updates"):
        row_update = smart.models.Row()
        row_update.id = int(vendor["custom_id"])

        for k, v in SMART_SHEET_UPDATE_COLUMNS.items():
            if HEADER_MAPPING[k] != v["key"]:
                # This column is present in the sheet the mapping is set to a columnID
                smart_sheet_cell_update(glom(vendor, v["spec"]), HEADER_MAPPING[k], row_update, smart)

        row_updates.append(row_update)

    smart.Sheets.update_rows(sheet_id, row_updates)


@click.command()
@click.option("--sheet-name", help="Name of the sheet we are using", required=False)
@click.option("--sheet-id", help="ID of the sheet we are using", required=False)
@click.option(
    "--skip-rows-without-orders",
    help="Do not submit rows to CyberGRX that do not have a valid 'Order Assessment Tier'",
    is_flag=True,
)
def sync_smart_sheet(sheet_name, sheet_id, skip_rows_without_orders):
    api = os.environ.get("CYBERGRX_API", "https://api.cybergrx.com").rstrip("/")
    token = os.environ.get("CYBERGRX_API_TOKEN", None)
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
    print("Loaded " + str(len(sheet.rows)) + " vendors from sheet: " + sheet.name)

    # Build column map for later reference - translates column names to smart sheet column ids
    for column in sheet.columns:
        if column.title in HEADER_MAPPING:
            HEADER_MAPPING[column.id] = HEADER_MAPPING[column.title]
            HEADER_MAPPING[column.title] = column.id
        else:
            snake_header = stringcase.snakecase(re.sub(r"[^0-9a-zA-Z]+", "", column.title))
            HEADER_MAPPING[column.id] = snake_header
            HEADER_MAPPING[snake_header] = column.id

    # Load all vendors from smart sheet
    all_smart_sheet_vendors = [normalize_vendor(vendor, HEADER_MAPPING, COMPANY_SCHEMA) for vendor in sheet.rows]
    for v in all_smart_sheet_vendors:
        if "url" not in v or "address" not in v:
            print("Missing data in", v)
    smart_sheet_vendors = [v for v in all_smart_sheet_vendors if "url" in v and "address" in v]

    # Load all third parties skipping residual risk
    uri = api + "/bulk-v1/third-parties?skip_residual_risk=true"
    print("Fetching third parties from " + uri + " this can take some time.")
    response = requests.get(uri, headers={"Authorization": token.strip()})
    grx_vendors = glom(json.loads(response.content.decode("utf-8")), ([GRX_COMPANY_SCHEMA]))
    grx_custom_ids = set([v["custom_id"] for v in grx_vendors if v["custom_id"]])

    # See which vendors in smart sheets do not have a corresponding custom_id in CyberGRX
    missing_vendors = [vendor for vendor in smart_sheet_vendors if vendor["custom_id"] not in grx_custom_ids]
    if missing_vendors:
        print("There are vendors in smart sheet that need to be migrated to CyberGRX")
        process_missing_vendors(missing_vendors, skip_rows_without_orders, token, api, sheet_id, smart)

    # Associate smart sheet vendors with CyberGRX records
    grx_vendor_map = {vendor["custom_id"]: vendor for vendor in grx_vendors}
    matched_vendors = [vendor for vendor in smart_sheet_vendors if vendor["custom_id"] in grx_custom_ids]
    for vendor in matched_vendors:
        vendor["grx"] = grx_vendor_map[vendor["custom_id"]]

    # Vendors that do not haave a complete profile, need to be updated
    vendors_with_profile = [vendor for vendor in matched_vendors if not vendor["grx"]["is_profile_complete"]]
    if vendors_with_profile:
        print("There are vendors with profile questions that need to be answered in CyberGRX")
        process_vendors_with_profile_updates(vendors_with_profile, token, api)

    # For vendors that have matches, sync their risk back to smart sheets
    if matched_vendors:
        print("There are vendors that need to sync risk profiles back to smart sheets")
        process_matched_vendors(matched_vendors, token, sheet_id, api, smart)


@click.command()
@click.option("--sheet-name", help="Name of the sheet we are using", required=False)
@click.option("--sheet-id", help="ID of the sheet we are using", required=False)
@click.option(
    "--skip-rows-without-orders",
    help="Do not submit rows to CyberGRX that do not have a valid 'Order Assessment Tier'",
    is_flag=True,
)
def bulk_import_request(sheet_name, sheet_id, skip_rows_without_orders):
    api = os.environ.get("CYBERGRX_API", "https://api.cybergrx.com").rstrip("/")
    token = os.environ.get("CYBERGRX_API_TOKEN", None)
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
    print("Loaded " + str(len(sheet.rows)) + " vendors from sheet: " + sheet.name)

    # Build column map for later reference - translates column names to smart sheet column ids
    for column in sheet.columns:
        if column.title in HEADER_MAPPING:
            HEADER_MAPPING[column.id] = HEADER_MAPPING[column.title]
            HEADER_MAPPING[column.title] = column.id
        else:
            snake_header = stringcase.snakecase(re.sub(r"[^0-9a-zA-Z]+", "", column.title))
            HEADER_MAPPING[column.id] = snake_header
            HEADER_MAPPING[snake_header] = column.id

    # Load all vendors from smart sheet
    smart_sheet_vendors = [row_to_vendor(vendor, HEADER_MAPPING) for vendor in sheet.rows]

    # Load all third parties skipping residual risk
    uri = api + "/bulk-v1/third-parties?skip_residual_risk=true"
    print("Fetching third parties from " + uri + " this can take some time.")
    response = requests.get(uri, headers={"Authorization": token.strip()})
    grx_vendors = glom(json.loads(response.content.decode("utf-8")), ([GRX_COMPANY_SCHEMA]))
    grx_custom_ids = set([v["custom_id"] for v in grx_vendors if v["custom_id"]])

    # See which vendors in smart sheets do not have a corresponding custom_id in CyberGRX
    missing_vendors = [vendor for vendor in smart_sheet_vendors if vendor["custom_id"] not in grx_custom_ids]

    if skip_rows_without_orders:
        # User wants to skip vendors that do not have orders
        missing_vendors = [vendor for vendor in missing_vendors if "order_info" in glom(vendor, COMPANY_SCHEMA)]

    if not missing_vendors:
        print("There are no vendors that need to be migrated to CyberGRX")
        return

    wb = Workbook()
    wb["Sheet"].title = "Third Party Information"
    vendor_writer = sheet_writer(wb, "Third Party Information", BULK_IMPORT_COLUMNS)

    for vendor in tqdm(missing_vendors, total=len(missing_vendors), desc="Vendor"):
        vendor_writer(vendor)

    # Finalize each writer (fix width, ETC)
    vendor_writer.finalizer()
    wb.save("bulk-import-request.xlsx")


@click.group()
def cli():
    pass


cli.add_command(sync_smart_sheet)
cli.add_command(bulk_import_request)


if __name__ == "__main__":
    cli()
