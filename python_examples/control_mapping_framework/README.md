This example application showcases the ability to export CyberGRX data into a template file using the [CyberGRX Bulk API](https://api.cybergrx.com/bulk-v1/swagger/).  This example is coded using Python, the integration code is contained in [export.py](./export.py).  You should run all commands from this directory.

# Running the example
The first step is to configure a virtual environment for the application dependencies.
- Python 3: `pip3 install virtualenv && python3 -m venv env`
- `source env/bin/activate`
- `pip install -r requirements.txt`

At this point you are all setup to run the example, but before you do, create a file that holds your API token. 
- `vi .auth-token` add the following line to this file and save it `export CYBERGRX_API_TOKEN="API-V1 TOKEN FROM UI"`

# Running the command
There are 2 commands in this example, before any can be run setup the Python environment and the authentication settings
- Remember to source your python environment `source env/bin/activate` the first time you run the command
- `source .auth-token`
- Once you are done experimenting remember to **remove** the `.auth-token` file so you do not leak sensitive information.

## Sync new reports
This command will retrieve all reports that have been updated within the last 24 hours.
- `python export.py map-analytics`
- `python export.py map-analytics --template-name="my custom template.xlsx"`

## Sync all reports
This command will retrieve all available reports from CyberGRX by using a "reports-from" filter set to 2016.  This command will take some time to process be patient.
- `python export.py map-analytics --reports-from=2016-01-01`
- `python export.py map-analytics --reports-from=2016-01-01 --template-name="my custom template.xlsx"`