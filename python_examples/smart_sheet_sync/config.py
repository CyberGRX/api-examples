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
)
from glom import glom, Coalesce, OMIT

import click

HEADER_MAPPING = {
    "Vendor Name": "company_name",
    "Vendor URL": "company_url",

    # Address metadata (need at least a city to create a company)
    "Vendor HQ City": "address_city",
    "Vendor HQ Country": "address_country",

    # Internal Metadata
    "Vendor Owner": "internal_vendor_owner",
    "Description": "internal_description",
    "Location": "internal_location",

    # Third Party Contact Info
    "Vendor Contact Name": "third_party_contact_name",
    "Vendor Contact Email": "third_party_contact_email",
    "Vendor Contact Phone": "third_party_contact_phone",

    # Assessment Order Info
    "Order Assessment Tier": "assessment_order",

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

    # GRX Metadata tracking from smart-sheets
    "Ingest Date": "ingest_date",
    "GRX Vendor Name": "grx_vendor_name",
}

COMPANY_SCHEMA = {
    "name": "company_name",

    # Prefer the company domain from the spread sheet, fallback to using the email address's domain
    "url": (
        Coalesce(("company_url", required), ("third_party_contact_email", email_metadata("domain"))),
        required,
        insert_http,
    ),
    "custom_id": "custom_id",
    "ingest_date": (Coalesce("ingest_date", default=None), date_or_none),

    "address": {
        "city": "address_city", 
        "country": "address_country",
    },

    # Map the assessment order column to a valid order request, skip this field if it is not present or invalid
    "order_info": Coalesce(("assessment_order", valid_assessment_order), default=OMIT),

    "third_party_contact": (
        {
            # Prefer the first and last name from the spread sheet, fallback to using the email address
            "first_name": (
                Coalesce(
                    ("third_party_contact_name", split(False), required),
                    ("third_party_contact_email", email_metadata("first_name")),
                    default=OMIT,
                ),
                skip_falsy,
            ),
            "last_name": (
                Coalesce(
                    ("third_party_contact_name", split(True), required),
                    ("third_party_contact_email", email_metadata("last_name")),
                    default=OMIT,
                ),
                skip_falsy,
            ),
            "email": Coalesce(("third_party_contact_email", skip_falsy), default=OMIT),
            "phone": Coalesce(("third_party_contact_phone", skip_falsy), default=OMIT),
        },
        skip_falsy,
    ),

    # If the row has answers, configure the scoping profile payload
    "third_party_scoping": (
        {
            "digital_identities": Coalesce(("profile_digital_identities", validate_answer), default=OMIT),
            "people": Coalesce(("profile_people", validate_answer), default=OMIT),
            "data": Coalesce(("profile_data", validate_answer), default=OMIT),
            "applications": Coalesce(("profile_applications", validate_answer), default=OMIT),
            "devices": Coalesce(("profile_devices", validate_answer), default=OMIT),
            "networks": Coalesce(("profile_networks", validate_answer), default=OMIT),
            "facilities": Coalesce(("profile_facilities", validate_answer), default=OMIT),
            "business_process": Coalesce(("profile_business_process", validate_answer), default=OMIT),
        },
        skip_falsy,
    ),

    "custom_metadata": (
        {
            "internal": (
                {
                    "owner": ("internal_vendor_owner", skip_falsy),
                    "description": ("internal_description", skip_falsy),
                    "location": ("internal_description", skip_falsy),
                },
                skip_falsy,
            ),
            "cyber_classification": (
                {
                    "critical_or_support": ("meta_is_critical_or_support", skip_falsy),
                    "rto": ("meta_rto", skip_falsy),
                    "data_sensitivity": ("meta_data_sensitivity", skip_falsy),
                    "compliance": ("meta_compliance", skip_falsy),
                    "tech_risk": ("meta_tech_risk", skip_falsy),
                    "influence": ("meta_influence", skip_falsy),
                },
                skip_falsy,
            ),
        },
        skip_falsy,
    ),
}

GRX_COMPANY_SCHEMA = {
    "id": "id",
    "name": "name",
    "custom_id": "custom_id",
    "is_profile_complete": "subscription.is_profile_complete",
    "impact": "inherent_risk.impact_label",
    "likelihood": "inherent_risk.likelihood_label",
}

BULK_IMPORT_COLUMNS = [
    ["Third Party Legal or DBA Name", "company_name", "blue"],
    ["Website Name URL", "company_url", "blue"],
    ["Third Party HQ City", "address_city"],
    ["Third Party HQ Country", "address_country"],
]
