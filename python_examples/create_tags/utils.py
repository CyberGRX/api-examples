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
from glom import glom


def _cell_value(cell):
    return "{}".format(cell.value).strip() if cell and cell.value else ""


def columns_for_headers(row, header_map):
    mapping = {}
    
    for idx, col in enumerate(row):
        column = _cell_value(col)
        if column and header_map.get(column, None):
            mapping[idx] = header_map.get(column, None)

    return mapping

def process_companies(sheet, header_mapping):
    companies = []
    headers = {}
    for index, row in enumerate(sheet.iter_rows()):
        if not headers:
            headers = columns_for_headers(row, header_mapping)
            if headers and len(headers) != 2:
                print(headers)
                raise Exception("Need column headers for both company names and tags")
        else:
            company = OrderedDict()
            for column_index, col in enumerate(row):
                if column_index not in headers:
                    continue

                if col.value is not None:
                    try:
                        company[headers[column_index]] = bytearray(col.value, 'utf-8').decode("utf-8")
                    except:
                        company[headers[column_index]] = col.value

            if not company:
                continue

            company["tags"] = [str(tag).strip() for tag in company["tags"].split(",") if tag and str(tag).strip()]
            if not company["tags"]:
                print("Company did not have any tags: ", company)
            else:
                companies.append(company)


    return companies