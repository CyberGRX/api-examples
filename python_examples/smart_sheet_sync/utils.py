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
from collections import OrderedDict
from openpyxl import Workbook
from openpyxl.styles.fills import FILL_SOLID
from openpyxl.styles import Color, PatternFill, Font, Border, Side
from openpyxl.styles import colors
from openpyxl.cell import Cell
from tqdm import tqdm
from glom import glom, OMIT


VALID_ANSWERS = {
    "least": "Least",
    "minimal": "Minimal",
    "moderate": "Moderate",
    "significant": "Significant",
}


def skip_falsy(value): 
    return OMIT if not value else value


def insert_http(value): 
    if not value.startswith("http"):
        return "https://" + value

    return value


def normalize_vendor(vendor, column_mapping, spec):
    normalized = glom({column_mapping[cell.column_id]: cell.value for cell in vendor.cells}, spec)
    normalized["custom_id"] = str(vendor.id)
    return normalized


def lookup_sheet_id(smart, sheet_name):
    response = smart.Sheets.list_sheets(include_all=True)
    matched_sheets = [sheet for sheet in response.data if sheet.name.lower() == sheet_name.lower()]
    if len(matched_sheets) != 1:
        message = "Unable to lookup a unique sheet ID, multiple sheets matched '" + sheet_name + "' set --sheet-id instead"
        raise Exception(message)

    return matched_sheets[0].id


def split(index):
    def splitter(value):
        if not value:
            return OMIT
        
        try:
            return value.split(" ")[index]
        except:
            return OMIT

    return splitter


def validate_answer(value):
    if not value:
        return OMIT

    normalized = str(value).strip().lower()
    for key in VALID_ANSWERS.keys():
        if normalized.startswith(key):
            return VALID_ANSWERS[key]

    return OMIT