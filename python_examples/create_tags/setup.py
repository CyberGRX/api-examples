#########################################################################
#    _________        ___.                   ______________________  ___
#    \_   ___ \___.__.\_ |__   ___________  /  _____/\______   \   \/  /
#    /    \  \<   |  | | __ \_/ __ \_  __ \/   \  ___ |       _/\     /
#    \     \___\___  | | \_\ \  ___/|  | \/\    \_\  \|    |   \/     \
#     \______  / ____| |___  /\___  >__|    \______  /|____|_  /___/\  \
#            \/\/          \/     \/               \/        \/      \_/
#
#

from setuptools import find_packages
from setuptools import setup

def requirements(f):
    with open(f) as fd:
        return [
            l for l in [r.strip() for r in fd.readlines()] if l and not l.startswith('-') and not l.startswith("#")
        ]

install_requires = requirements('requirements.txt')

setup(
    name='api-create-tags',
    url='https://github.com/CyberGRX//api-examples/tree/master/python_examples/create_tags',
    author='CyberGRX Engineering Team',
    author_email='engineers@cybergrx.com',
    version="1.0.0",
    packages=find_packages("."),
    install_requires=install_requires,
    extras_require={
        'license': 'pip-licenses==1.7.1',
    },
)