This example application showcases the abilility to order assessment for existing third parties using an Excel file using the [CyberGRX API](https://api.cybergrx.com/v1/swagger/).  This example is coded using Python, the ordering code is contained in [order.py](./order.py).  You should run all commands from this directory.

# Running the example
The first step is to configure a virtual environment for the application dependencies.  Depending on the version of Python that you are using the following commands will slightly differ.
- Python 2: `pip install virtualenv && virtualenv env`
- Python 3: `pip3 install virtualenv && python3 -m venv env`
- `source env/bin/activate`
- `pip install -r requirements.txt`

At this point you are all setup to run the example, but before you do, create a file that holds your API token.
- `vi .auth-token` add the following lines to this file and save it:
```
export CYBERGRX_API_TOKEN="API-V1 TOKEN FROM UI"
```

# Running the command
There is 1 command in this example, before it can be run, setup the Python environment and the authentication settings
- Remember to source your python environment `source env/bin/activate` the first time you run the command
- `source .auth-token`
- Once you are done experimenting remember to **remove** the `.auth-token` file so you do not leak sensitive information.

## Ordering assessments in bulk
This command will order assessments for third parties that do not have orders already.
- This command expects an excel file that resembels `bulk-order.xlsx` an example has been provided in this directory.
- All columns are required except for `Vendor Contact Phone`
- `python order.py bulk-order.xlsx`
