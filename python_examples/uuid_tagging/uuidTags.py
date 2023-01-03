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

# map uuid:tags function 
# iterate through company UUID's in excel sheet and map tags 
# return a dict of UUID : Tags
def mapTags(wb): 

    # a list to hold companies that don't have any tags
    # dict to contain UUID:tags 
    noTags = []
    companyTags = {} 

    # define num of columns to check for required columns(2) 
    numColumns = wb.shape[1]
    if numColumns != 2:
        raise Exception("Excel sheet formatted wrong! Format needs to be col1 : CompanyID, col2 : Tags")

    # stripping commas out of the excel sheet
    wb = wb.replace(',' , '', regex=True)
    # replacing any NaN cell values with an empty string 
    wb = wb.fillna('')

    # mapping tags to company UUID's 
    for i in range(wb.shape[0]):
        uuid = wb.iloc[i, 0]
        # creating an array of tags for each company
        tags = wb.iloc[i, 1].split()
        if tags == []:
            noTags.append(uuid)
        else:
            companyTags[uuid] = tags

    # displaying company UUID's that have no tags to be applied 
    if len(noTags) != 0:
        print("These companies had no tags to apply:")
        for id in noTags:
            print(id)
        print()

    # returning mapped {UUID:tags} 
    return companyTags


# apply tags function
# reads in an excel sheet, passes the sheet to a mapping function
# gets {UUID:Tags} returned to it
# hits api to verify UUID is in portfolio 
# applies read in tags 
def applyTags():
    # read in workbook. EXCEL SHEET MUST BE IN THE SAME DIR AS THIS SCRIPT
    wb = pd.read_excel('uuidTags.xlsx')
    companies = mapTags(wb)
    
    # define the api and token 
    # api = 'https://api-version-1.develop.new-staging.grx-dev.com'
    # token = "API-V1 JdgTu6TdQlGsVdcBuapxIw==.94zFwok+ZUxY4tyNFMv97iNb0qa3G/M8Q5FQJbyWB8Y="
    api = os.environ.get("CYBERGRX_API", "https://api-version-1.develop.new-staging.grx-dev.com").rstrip("/")
    token = os.environ.get("CYBERGRX_API_TOKEN", None)

    # using tqdm as a decerator to display status bar 
    # you don't have to use this, but it's nice to know how many tags are left
    # for uuid, tags in companies.items(): 
    for uuid, tags in tqdm(companies.items(), total=len(companies), desc="Applying Tags"):
        
        # make a get call to verify company UUID is in portfolio
        uri = f"{api}/v1/third-parties/{uuid}"
        response = requests.get(uri, headers={"Authorization" : token.strip()})
        # response = requests.get(uri, headers={"Authorization" : token})
        result = json.loads(response.content.decode("utf-8"))
        thirdPartyId = glom(result, "id")
        
        # if thirdPartyId matches current uuid, apply tags 
        if thirdPartyId == uuid:
            print(uuid, tags)
            uri = f"{api}/v1/third-parties/{uuid}/tagging"
            response = requests.post(uri, headers={"Authorization": token.strip()}, json={"tags": tags})
            # response = requests.post(uri, headers={"Authorization": token}, json={"tags": tags})

        else:
            # company isn't in profile
            print(f"Company : {uuid} is not in your profile.")


if __name__ == "__main__":
    applyTags()


