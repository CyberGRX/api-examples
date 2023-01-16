#########################################################################
#    _________        ___.                   ______________________  ___
#    \_   ___ \___.__.\_ |__   ___________  /  _____/\______   \   \/  /
#    /    \  \<   |  | | __ \_/ __ \_  __ \/   \  ___ |       _/\     /
#    \     \___\___  | | \_\ \  ___/|  | \/\    \_\  \|    |   \/     \
#     \______  / ____| |___  /\___  >__|    \______  /|____|_  /___/\  \
#            \/\/          \/     \/               \/        \/      \_/
#
#

# required dependencies 
import pandas as pd
import json
import os
from glom import glom
import requests
from tqdm import tqdm
from time import time


def map_tags(wb): 

    # a list to hold any company UUID's that fail during execution 
    failed_companies = [] 
    # a dict of company UUID : with the 8 answered impact questions 
    impact_answers = {}
    
    # checking to make sure that the excel sheet is formatted correctly 
    # UUID plus the 8 answered impact questions 
    num_columns = wb.shape[1]
    if num_columns != 9:
        raise Exception("Excel sheet formatted wrong! Check to make sure that the columns contain company UUID and the 8 scoping questions!")


    for i in range(wb.shape[0]):
        tmp = wb.iloc[1, i]
        # print(tmp)
        # print(type(tmp))
        # tmp2 = tmp.to_dict()
        # tmp2 = wb.iloc[:, 1].to_dict()
        tmp2 = tmp.to_dict()
        print(tmp2)
        # company_uuid = wb.iloc[0]
        
    
        


    # define num of columns to check for required columns(2) 
    # num_columns = wb.shape[1]
    # if num_columns != 2:
    #     raise Exception("Excel sheet formatted wrong! Format needs to be col1 : CompanyID, col2 : Tags")

    # # stripping commas out of the excel sheet
    # wb = wb.replace(',' , '', regex=True)
    # # replacing any NaN cell values with an empty string 
    # wb = wb.fillna('')

    # # mapping tags to company UUID's 
    # for i in range(wb.shape[0]):
    #     uuid = wb.iloc[i, 0]
    #     # creating an array of tags for each company
    #     tags = wb.iloc[i, 1].split()
    #     if tags == []:
    #         no_tags.append(uuid)
    #     else:
    #         company_tags[uuid] = tags

    # # displaying company UUID's that have no tags to be applied 
    # if len(no_tags) != 0:
    #     print("These companies had no tags to apply:")
    #     for id in no_tags:
    #         print(id)
    #     print()

    # # returning mapped {UUID:tags} 
    # return company_tags





# apply tags function
# reads in an excel sheet, passes the sheet to a mapping function
# gets {UUID:Tags} returned to it
# hits api to verify UUID is in portfolio 
# applies read in tags 
def answer_questions():
    # read in workbook. EXCEL SHEET MUST BE IN THE SAME DIR AS THIS SCRIPT
    wb = pd.read_excel('scoping_questions.xlsx')
    companies = map_tags(wb)
    
    # define the api and token 
    api = os.environ.get("CYBERGRX_API", "https://api-version-1.develop.new-staging.grx-dev.com").rstrip("/")
    # # api = os.environ.get("CYBERGRX_API", "https://api.cybergrx.com").rstrip("/")
    # token = os.environ.get("CYBERGRX_API_TOKEN", None)
    # if not token:
    #         raise Exception("The environment variable CYBERGRX_API_TOKEN must be set")

    # # using tqdm as a decerator to display status bar 
    # # you don't have to use this, but it's nice to know how many tags are left
    # # for uuid, tags in companies.items(): 
    # for uuid, tags in tqdm(companies.items(), total=len(companies), desc="Applying Tags"):
    #     
    #     # make a get call to verify company UUID is in portfolio
    #     uri = f"{api}/v1/third-parties/{uuid}"
    #     response = requests.get(uri, headers={"Authorization" : token.strip()})
    #     # loading the response as a json
    #     result = json.loads(response.content.decode("utf-8"))
    #     
    #     # pulling 3rd party id and company name out of the response 
    #     # if third_party_id == UUID 
    #     third_party_id = glom(result, "id")
    #     companyName = glom(result, "name")

    #     # if third_party_id matches current uuid, apply tags 
    #     if third_party_id == uuid:
    #         print(f"CompanyID: {uuid} CompanyName: {companyName}. Tags: {tags}")
    #         uri = f"{api}/v1/third-parties/{uuid}/tagging"
    #         response = requests.post(uri, headers={"Authorization": token.strip()}, json={"tags": tags})
    #         # it post request times out, call recursive retry function 
    #         if response.status_code == 504:
    #             retry_tagging(id=uuid, tag=tags)
    #         

    #     else:
    #         # company isn't in profile
    #         print(f"Company : {uuid} is not in your profile.")


answer_questions()
