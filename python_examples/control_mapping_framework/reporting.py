#########################################################################
#    _________        ___.                   ______________________  ___
#    \_   ___ \___.__.\_ |__   ___________  /  _____/\______   \   \/  /
#    /    \  \<   |  | | __ \_/ __ \_  __ \/   \  ___ |       _/\     /
#    \     \___\___  | | \_\ \  ___/|  | \/\    \_\  \|    |   \/     \
#     \______  / ____| |___  /\___  >__|    \______  /|____|_  /___/\  \
#            \/\/          \/     \/               \/        \/      \_/
#
#
import logging
import os
import stringcase
import re
from collections import defaultdict
from openpyxl import Workbook, load_workbook
from docx.shared import Cm
from docxtpl import DocxTemplate, InlineImage

from jinja2 import Environment, DebugUndefined

logger = logging.getLogger(__name__)

NUMBERS_LETTERS_SPACE = re.compile(r"[^\d\w ]")
MULTIPLE_SPACES = re.compile(r"[\s]+")
REPLACE_XML = re.compile(r"<\/{0,1}.*?>")


class SilentUndefined(DebugUndefined):
    def _fail_with_undefined_error(self, *args, **kwargs):
        logger.exception(f"{self} was in the template but not sent in the context")
        return f"{self}"


def clean_key(raw):
    lowered = f"{raw}".lower()
    single_space = MULTIPLE_SPACES.sub(" ", lowered)
    return stringcase.snakecase(NUMBERS_LETTERS_SPACE.sub("", single_space).strip())


def clean_value(raw):
    return REPLACE_XML.sub("", f"{raw}".strip()).replace("\n", "<w:br/>")


def read_report(excel_file):
    wb = load_workbook(excel_file)

    report = defaultdict(list)
    for _, s in enumerate(wb):
        headers = None
        sheet_title = clean_key(s.title)
        for row in s:
            if not headers:
                headers = {i: clean_key(col.value) for i, col in enumerate(row)}
            else:
                processed_row = {headers[i]: clean_value(col.value) for i, col in enumerate(row)}
                report[sheet_title].append(processed_row)

    return report


def debug_keys(obj, prefix=None):
    results = []

    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, dict):
                for r in debug_keys(v, prefix=f"{k}."):
                    if r not in results:
                        results.append(r)
            elif isinstance(v, list):
                for vv in v:
                    for r in debug_keys(vv, prefix=f"{k}[]"):
                        if r not in results:
                            results.append(r)
            else:
                result = f"{prefix if prefix else ''}{k}"
                if result not in results:
                    results.append(result)
    else:
        result = f"{prefix if prefix else ''}"
        if result not in results:
            results.append(result)

    return results


def create_report(excel_file, doc_template, output_name, metadata=None):
    if not metadata:
        metadata = {}

    report_data = read_report(excel_file)
    metadata.update(report_data)
    debug = debug_keys(metadata)
    debug.sort()
    metadata["debug"] = "<w:br/>".join(debug)

    template = DocxTemplate(doc_template)
    template.render(metadata, Environment(undefined=SilentUndefined))

    # Wipe the report if it exists
    if os.path.exists(output_name):
        os.remove(output_name)

    template.save(output_name)
