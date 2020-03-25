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

import click
from urllib.parse import quote
from openpyxl import Workbook, load_workbook
from tqdm import tqdm
from glom import glom, Coalesce

from utils import sheet_writer
from config import YESTERDAY, CONTROL_SCORES, GAPS_TABLE, COMPANY_TAGS, TP_COLUMNS, TP_MAPPING, GAPS_COLUMNS, SCORE_COLUMNS, SCORE_MAPPING, TAG_COLUMNS


def create_sheet(wb, sheet_name):
    try:
        wb[sheet_name]
    except KeyError:
        wb.create_sheet(sheet_name)

def init_workbook(filename):
    wb = load_workbook(filename=filename)

    create_sheet(wb, CONTROL_SCORES)
    create_sheet(wb, GAPS_TABLE)
    create_sheet(wb, COMPANY_TAGS)
    
    findings_writer = sheet_writer(wb, GAPS_TABLE, GAPS_COLUMNS)
    scores_writer = sheet_writer(wb, CONTROL_SCORES, SCORE_COLUMNS, mapping=SCORE_MAPPING)
    tags_writer = sheet_writer(wb, COMPANY_TAGS, TAG_COLUMNS)

    return wb, scores_writer, findings_writer, tags_writer


@click.command()
@click.option("--template-name", help="Filename of the controls mapping template", required=False, default="template.xlsx")
@click.option("--reports-from", help="Retrieve reports that are 'newer' than this date, defaults to yesterday", required=False, default=YESTERDAY)
def map_analytics(template_name, reports_from):
    api = os.environ.get('CYBERGRX_API', "https://api.cybergrx.com").rstrip("/")
    token = os.environ.get('CYBERGRX_API_TOKEN', None)
    if not token:
        raise Exception("The environment variable CYBERGRX_API_TOKEN must be set")

    uri = f"{api}/bulk-v1/third-parties?report_date={quote(reports_from)}"
    print(f"Fetching third parties from {uri} this can take some time.")
    response = requests.get(uri, headers={'Authorization': token.strip()})
    result = json.loads(response.content.decode('utf-8'))

    print(f"Retrieved {str(len(result))} third parties from your ecosystem, building an excel.")
    for tp in tqdm(result, total=len(result), desc="Third Party"):
        company_name = tp["name"]

        scores = glom(tp, Coalesce("residual_risk.scores", default=[]))
        if not scores:
            continue
        
        tier = glom(tp, Coalesce("residual_risk.tier", default=0))
        if tier not in [1, 2]:
            print(f"{company_name} had a T{tier} report, this tier is not supported.")

        wb, scores_writer, findings_writer, tags_writer = init_workbook(template_name)

        for tag in glom(tp, Coalesce("tags", default=[])):
            tags_writer({"tag": tag, "company_name": company_name})

        for finding in glom(tp, Coalesce("residual_risk.findings", default=[])):
            finding["company_name"] = company_name
            findings_writer(finding)

        for score in scores:
            scores_writer(score)

        # Finalize each writer (fix width, ETC)
        findings_writer.finalizer()
        scores_writer.finalizer()
        tags_writer.finalizer()
        wb.save(f'{company_name}-mapped.xlsx')


@click.group()
def cli():
    pass


cli.add_command(map_analytics)


if __name__ == "__main__":
    cli()
