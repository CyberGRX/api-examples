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
import stringcase
from collections import defaultdict
from openpyxl import Workbook, load_workbook
from docx.shared import Cm
from docxtpl import DocxTemplate, InlineImage


def read_report(excel_file):
    wb = load_workbook(excel_file)

    report = defaultdict(list)
    for _, s in enumerate(wb):
        headers = None
        for row in s:
            if not headers:
                headers = {i: stringcase.snakecase(f"{col.value}".lower()) for i, col in enumerate(row)}
            else:
                processed_row = {headers[i]: col.value for i, col in enumerate(row)}
                report[stringcase.snakecase(f"{s.title}".lower())].append(processed_row)

    return report


def create_report(excel_file, doc_template, output_name, metadata=None):
    if not metadata:
        metadata = {}

    report_data = read_report(excel_file)
    metadata.update(report_data)

    template = DocxTemplate(doc_template)
    template.render(metadata)

    # Wipe the report if it exists
    if os.path.exists(output_name):
        os.remove(output_name)

    template.save(output_name)
