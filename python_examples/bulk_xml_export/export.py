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
import dicttoxml
from tqdm import tqdm
from glom import glom, Coalesce, OMIT
from xml.dom.minidom import parseString

# yapf: disable
TP_MAPPING = {
    "id": "id",
    "name": "name",
    "primary_url": "primary_url",
    "industry": "industry",
    "custom_id": "custom_id",
    "custom_metadata": "custom_metadata",
    "report_id": Coalesce("residual_risk.id", default=None),
    "report_type": Coalesce("residual_risk.report_type", default=None),
    "report_release_date": Coalesce("residual_risk.date", default=None),
    "report_tier": Coalesce("residual_risk.tier", default=None),
    "likelihood_label": Coalesce("inherent_risk.likelihood_label", default=None),
    "likelihood_score": Coalesce("inherent_risk.likelihood_score", default=None),
    "impact_label": Coalesce("inherent_risk.impact_label", default=None),
    "impact_score": Coalesce("inherent_risk.impact_score", default=None),
    "assessment_status": Coalesce("assessment.status", default=None),
    "assessment_progress": Coalesce("assessment.progress", default=None),
    "subscription_status": Coalesce("subscription.status", default=None),
    "subscription_tier": Coalesce("subscription.tier", default=None),
    "subscription_available": Coalesce("subscription.is_report_available", default=None),
    "residual_risk_outcomes": Coalesce("residual_risk.residual_risk_outcomes", default=[]),
    "scores": Coalesce(("residual_risk.scores", [{
        "name": "name",
        "number": "number",
        "question_type": "question_type",
        "parent_number": Coalesce("parent_number", default=OMIT),
        "effectiveness_score": Coalesce("effectiveness_score", default=None),
        "coverage_score": Coalesce("coverage_score", default=None),
        "maturity_score": Coalesce("maturity_score", default=None),
        "answer_state": Coalesce("answer_state", default=OMIT),
    }]), default=[]),
    "findings": Coalesce(("residual_risk.findings", [{
        "name": "name",
        "number": "number",
        "impact_level": "impact_level",
        "remedy": "remedy",
    }]), default=[]),
}
# yapf: enable


def item_type(value):
    return value[:-1]


def retrieve_ecosystem():
    api = os.environ.get("CYBERGRX_BULK_API", "https://api.cybergrx.com").rstrip("/")
    token = os.environ.get("CYBERGRX_API_TOKEN", None)
    if not token:
        raise Exception("The environment variable CYBERGRX_API_TOKEN must be set")

    uri = api + "/bulk-v1/third-parties"
    print("Fetching third parties from " + uri + " this can take some time.")
    response = requests.get(uri, headers={"Authorization": token.strip()})
    result = json.loads(response.content.decode("utf-8"))

    print("Retrieved " + str(len(result)) + " third parties from your ecosystem, building an xml manifest.")

    with open("ecosystem.json", "w") as f:
        f.write(json.dumps(result, indent=2))

    third_parties = []
    for tp in tqdm(result, total=len(result), desc="Third Party"):
        processed = glom(tp, TP_MAPPING)
        if processed["scores"]:
            third_parties.append(processed)

    third_party_xml = dicttoxml.dicttoxml(third_parties, custom_root="vendors", item_func=item_type)
    with open("ecosystem.xml", "w") as f:
        f.write(parseString(third_party_xml).toprettyxml())


if __name__ == "__main__":
    retrieve_ecosystem()
