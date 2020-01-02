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

Once that is done you can source that file into your environment and run the command
- Remember to source your python environment `source env/bin/activate` the first time you run the command
- `source .auth-token`
- `python sync.py`
- Once you are done **remove** the `.auth-token` file so you do not leak sensitive information.
