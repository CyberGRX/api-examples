#########################################################################
#    _________        ___.                   ______________________  ___
#    \_   ___ \___.__.\_ |__   ___________  /  _____/\______   \   \/  /
#    /    \  \<   |  | | __ \_/ __ \_  __ \/   \  ___ |       _/\     /
#    \     \___\___  | | \_\ \  ___/|  | \/\    \_\  \|    |   \/     \
#     \______  / ____| |___  /\___  >__|    \______  /|____|_  /___/\  \
#            \/\/          \/     \/               \/        \/      \_/
#
#

import datetime

from glom import Check, Coalesce, SKIP
from pytz import UTC

YESTERDAY = (datetime.datetime.utcnow().replace(tzinfo=UTC) - datetime.timedelta(days=1)).isoformat()

CONTROL_SCORES = "Answers"
COMPANY_TAGS = "Company Tags"
GAPS_TABLE = "Control Gaps (Findings)"
THIRD_PARTY_TABLE = "Vendor Metadata"
RESIDUAL_RISK_TABLE = "Residual Risk"

VALIDATION_LABELS = {
    "FullyValidated": "Fully Validated",
    "PartiallyValidated": "Partially Validated",
    "NotValidated": "Not Validated",
    # Map the remaining states into the Not Reviewed bucket
    "PendingReview": "Not Reviewed",
    "NotSelectedForValidation": "Not Reviewed",
    None: "Not Reviewed",
}


def validation_label(val):
    try:
        return VALIDATION_LABELS[val]
    except KeyError:
        return "Not Reviewed"


TP_COLUMNS = [
    ["Company Name", "name", "blue"],
    ["Company URL", "primary_url", "blue"],
    ["Likelihood", "likelihood_label", "orange"],
    ["Likelihood Value", "likelihood_score", "orange"],
    ["Impact", "impact_label", "orange"],
    ["Impact Value", "impact_score", "orange"],
    ["Assessment State", "assessment_status"],
    ["Assessment Progress", "assessment_progress"],
    ["Requested Completion Date", "assessment_requested_completion_date"],
    ["Assessment Completion Date", "assessment_completion_date"],
    ["Report order status", "subscription_status"],
    ["Report tier", "subscription_tier"],
    ["Report validated", "subscription_validated"],
    ["Report available", "subscription_available"],
    ["Industry", "industry"],
    ["Tags", "tags"],
]

TP_MAPPING = {
    "likelihood_label": Coalesce("inherent_risk.likelihood_label", default=None),
    "likelihood_score": Coalesce("inherent_risk.likelihood_score", default=None),
    "impact_label": Coalesce("inherent_risk.impact_label", default=None),
    "impact_score": Coalesce("inherent_risk.impact_score", default=None),
    "assessment_status": Coalesce("assessment.status", default=None),
    "assessment_progress": Coalesce("assessment.progress", default=None),
    "assessment_requested_completion_date": Coalesce("assessment.requested_completion_date", default=None),
    "assessment_completion_date": Coalesce("assessment.completion_date", default=None),
    "subscription_status": Coalesce("subscription.status", default=None),
    "subscription_tier": Coalesce("subscription.tier", default=None),
    "subscription_available": Coalesce("subscription.is_report_available", default=None),
    "subscription_validated": Coalesce("subscription.is_validated", default=None),
    "tags": (Coalesce("tags", default=[]), ",".join),
}

GAPS_COLUMNS = [
    ["Company Name", "company_name", "blue"],
    ["Control Name", "name", "orange"],
    ["Control Number", "number", "orange"],
    ["Level", "impact_level", "orange"],
    ["Remedy", "remedy", "orange"],
]

GAPS_SUMMARY = {
    "total_findings": (Coalesce("residual_risk.findings", default=[]), len),
    "total_high_findings": (
        Coalesce("residual_risk.findings", default=[]),
        ["impact_level"],
        [Check(equal_to="High", default=SKIP)],
        len,
    ),
    "total_medium_findings": (
        Coalesce("residual_risk.findings", default=[]),
        ["impact_level"],
        [Check(equal_to="Medium", default=SKIP)],
        len,
    ),
    "total_low_findings": (
        Coalesce("residual_risk.findings", default=[]),
        ["impact_level"],
        [Check(equal_to="Low", default=SKIP)],
        len,
    ),
}

SCORE_COLUMNS = [
    ["Control Number", "number", "blue"],
    ["Control Name", "number_name", "blue"],
    ["Answer State", "answer_state", "orange"],
    ["Effectiveness Score", "effectiveness_score", "orange"],
    ["Coverage Score", "coverage_score", "orange"],
    ["Maturity Score", "maturity_score", "orange"],
    ["Comment", "comment"],
    ["Validated", "validation"],
    ["Question Type", "question_type", "blue"],
]

SCORE_MAPPING = {
    "number": "number",
    "number_name": lambda v: f'{v["number"]} {v["name"]}',
    "answer_state": Coalesce("answer_state", default=None),
    "question_type": Coalesce("question_type", default=None),
    "effectiveness_score": Coalesce("effectiveness_score", default=None),
    "coverage_score": Coalesce("coverage_score", default=None),
    "maturity_score": Coalesce("maturity_score", default=None),
    "validation": (Coalesce("validation_state", default=None), validation_label),
    "comment": (Coalesce("comments", default=[]), "\n".join),
}

TAG_COLUMNS = [
    ["Company Name", "company_name", "blue"],
    ["Tag", "tag"],
]

RESIDUAL_RISK_COLUMNS = [
    ["Company Name", "company_name", "blue"],
    ["Category", "category"],
    ["Inherent Risk", "inherent_risk_label", "orange"],
    ["Inherent Risk Level", "inherent_risk_level", "orange"],
    ["Residual Risk", "residual_risk_label", "orange"],
    ["Residual Risk Level", "residual_risk_level", "orange"],
]
