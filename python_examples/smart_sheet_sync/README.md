This example application showcases the abilility to sync vendors from smart sheet (including answers to profile questions) into CyberGRX using the [CyberGRX API](https://api.cybergrx.com/v1/swagger/) and the Smart Sheets SDK.  This example is coded using Python, the integration code is contained in [sync.py](./sync.py).  You should run all commands from this directory.

# Running the example
The first step is to configure a virtual environment for the application dependencies.  Depending on the version of Python that you are using the following commands will slightly differ.
- Python 2: `pip install virtualenv && virtualenv env`
- Python 3: `pip3 install virtualenv && python3 -m venv env`
- `source env/bin/activate`
- `pip install -r requirements.txt`

At this point you are all setup to run the example, but before you do, create a file that holds your API tokens. 
- `vi .auth-token` add the following lines to this file and save it:
```
export CYBERGRX_API_TOKEN="API-V1 TOKEN FROM UI"
export SMARTSHEET_ACCESS_TOKEN="ACCESS TOKEN FROM SMART SHEET"
```

# Running the command
There are 2 commands in this example, before any can be run setup the Python environment and the authentication settings
- Remember to source your python environment `source env/bin/activate` the first time you run the command
- `source .auth-token`
- Once you are done experimenting remember to **remove** the `.auth-token` file so you do not leak sensitive information.

## Bidirectional sync between a smart sheet and CyberGRX
This command will sync new companies to CyberGRX, it will also apply scoping profile questions to companies in CyberGRX.  Once companies have been synced with CyberGRX, the likelihood and impact analysis is synced back to the smart sheet.
- `python sync.py sync-smart-sheet --sheet-name="Name of sheet"`
- `python sync.py sync-smart-sheet --sheet-id="ID of sheet"`

## Bulk import template
To make initial data curation easier on the CyberGRX team, it is recommended that you initially create a bulk import request from your smart sheet.  This command will generate an Excel file containing all the vendors that are not present in your CyberGRX ecosystem.  Simply generate this bulk-ingest-request and then upload the resulting Excel file to the bulk import utility on the platform.
- `python sync.py bulk-import-request --sheet-name="Name of sheet"`
- `python sync.py bulk-import-request --sheet-id="ID of sheet"`