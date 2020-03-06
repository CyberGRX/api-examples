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
from uuid import uuid4
import requests
import stringcase
from openpyxl import Workbook, load_workbook
from tqdm import tqdm
from utils import (
    split,
    normalize_vendor,
    lookup_sheet_id,
    skip_falsy,
    insert_http,
    validate_answer,
    date_or_none,
    email_metadata,
    required,
    valid_assessment_order,
    as_string,
)
from glom import glom, Coalesce, Literal, OMIT

import click

HEADER_MAPPING = {
    "Vendor Name": "name",

    # Third Party Contact Info
    "Vendor Contact Name": "third_party_contact_name",
    "Vendor Contact First Name": "third_party_contact_first_name",
    "Vendor Contact Last Name": "third_party_contact_last_name",
    "Vendor Contact Email": "third_party_contact_email",
    "Vendor Contact Phone": "third_party_contact_phone",

    # Assessment Order Info
    "Order Assessment Tier": "assessment_order",
}

# Better change of mapping to column headers
HEADER_MAPPING.update({k.lower().strip(): v for k, v in HEADER_MAPPING.items()})
HEADER_MAPPING.update({k.upper().strip(): v for k, v in HEADER_MAPPING.items()})
HEADER_MAPPING.update({re.sub(r"[^0-9a-zA-Z ]+", '', k): v for k, v in HEADER_MAPPING.items()})
HEADER_MAPPING.update({k.replace(" ", "_"): v for k, v in HEADER_MAPPING.items()})
HEADER_MAPPING.update({k.replace(" ", ""): v for k, v in HEADER_MAPPING.items()})

COMPANY_SCHEMA = {
    "name": "name",

    "subscription_status": Literal(None),
    
    "address":{
        "city": Literal("Denver"),
        "country": Literal("USA"),
    },

    # Map the assessment order column to a valid order request, skip this field if it is not present or invalid
    "order_info": Coalesce(("assessment_order", valid_assessment_order), default=OMIT),

    "third_party_contact": (
        {
            # Prefer the first and last name from the spread sheet, fallback to using the email address
            "first_name": (
                Coalesce(
                    ("third_party_contact_first_name", required),
                    ("third_party_contact_name", split(False), required),
                    ("third_party_contact_email", email_metadata("first_name")),
                    default=OMIT,
                ),
                skip_falsy,
            ),
            "last_name": (
                Coalesce(
                    ("third_party_contact_last_name", required),
                    ("third_party_contact_name", split(True), required),
                    ("third_party_contact_email", email_metadata("last_name")),
                    default=OMIT,
                ),
                skip_falsy,
            ),
            "email": Coalesce(("third_party_contact_email", skip_falsy), default=OMIT),
            "phone": Coalesce(("third_party_contact_phone", as_string, skip_falsy), default=OMIT),
        },
        skip_falsy,
    ),
}

def url_cleanup(v):
    if not v:
        return f"https://{uuid4()}.net"

    return f"https://{v}" if "http" not in v else v

GRX_COMPANY_SCHEMA = {
    "id": "id",
    "name": "name",
    "url": ("primary_url", url_cleanup),
    "subscription_status": Coalesce("subscription.status", default=None),
}
