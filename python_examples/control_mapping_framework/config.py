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
from openpyxl import Workbook, load_workbook
from tqdm import tqdm
from glom import glom, Coalesce, OMIT, Literal
from pytz import UTC
import datetime

YESTERDAY = (datetime.datetime.utcnow().replace(tzinfo=UTC) - datetime.timedelta(days = 1)).isoformat()

CONTROL_SCORES = "Answers"
COMPANY_TAGS = "Company Tags"
GAPS_TABLE = "Control Gaps (Findings)"

TP_COLUMNS = [
    ["Company Name", "name", "blue"],
    ["Company URL", "primary_url", "blue"],
    ["Impact", "impact_label", "orange"],
    ["Impact Value", "impact_score", "orange"],
    ["Likelihood", "likelihood_label", "orange"],
    ["Likelihood Value", "likelihood_score", "orange"],
    ["Industry", "industry"],
]

TP_MAPPING = {
    "likelihood_label": Coalesce("inherent_risk.likelihood_label", default=None),
    "likelihood_score": Coalesce("inherent_risk.likelihood_score", default=None),
    "impact_label": Coalesce("inherent_risk.impact_label", default=None),
    "impact_score": Coalesce("inherent_risk.impact_score", default=None),
}

GAPS_COLUMNS = [
    ["Company Name", "company_name", "blue"],
    ["Control Name", "name", "orange"],
    ["Control Number", "number", "orange"],
    ["Level", "impact_level", "orange"],
    ["Remedy", "remedy", "orange"],
]

SCORE_COLUMNS = [
    ["Control", "number_name", "blue"],
    ["Question Type", "question_type", "blue"],
    ["Answer State", "answer_state", "orange"],
    ["Effectiveness Score", "effectiveness_score", "orange"],
    ["Coverage Score", "coverage_score", "orange"],
    ["Maturity Score", "maturity_score", "orange"],
    ["Comment", "comment"],
    ["Validated", "validation"],
]

SCORE_MAPPING = {
    "number_name": lambda v: f'{v["number"]} {v["name"]}',
    "answer_state": Coalesce("answer_state", default=None),
    "question_type": Coalesce("question_type", default=None),
    "effectiveness_score": Coalesce("effectiveness_score", default=None),
    "coverage_score": Coalesce("coverage_score", default=None),
    "maturity_score": Coalesce("maturity_score", default=None),
    "comment": Literal(None),
    "validation": Literal(None),
}

TAG_COLUMNS = [
    ["Company Name", "company_name", "blue"],
    ["Tag", "tag"],
]