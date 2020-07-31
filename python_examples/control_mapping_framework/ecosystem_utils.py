#########################################################################
#    _________        ___.                   ______________________  ___
#    \_   ___ \___.__.\_ |__   ___________  /  _____/\______   \   \/  /
#    /    \  \<   |  | | __ \_/ __ \_  __ \/   \  ___ |       _/\     /
#    \     \___\___  | | \_\ \  ___/|  | \/\    \_\  \|    |   \/     \
#     \______  / ____| |___  /\___  >__|    \______  /|____|_  /___/\  \
#            \/\/          \/     \/               \/        \/      \_/
#
#
from attrdict import AttrDict


def init_ecosystem_writer(ecosystem, excel_template_name):
    if not ecosystem:
        return AttrDict(
            {
                "tags_writer": lambda tag_meta: False,
                "findings_writer": lambda finding: False,
                "scores_writer": lambda score, company_name: False,
                "third_party_writer": lambda tp: False,
                "procecss_excel": lambda excel_filename, company_name: False,
                "finalizer": lambda: False,
            }
        )
