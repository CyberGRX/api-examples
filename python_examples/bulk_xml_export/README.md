This example application showcases a complete CyberGRX export to XML and JSON files using the [CyberGRX Bulk API](https://api.cybergrx.com/bulk-v1/swagger/).  This example is coded using Python, the integration code is contained in [export.py](./export.py).  You should run all commands from this directory.

# Running the example
The first step is to configure a virtual environment for the application dependencies.  Depending on the version of Python that you are using the following commands will slightly differ.
- Python 2: `pip install virtualenv && virtualenv env`
- Python 3: `pip3 install virtualenv && python3 -m venv env`
- `source env/bin/activate`
- `pip install -r requirements.txt`

At this point you are all setup to run the example, but before you do, create a file that holds your API token. 
- `vi .auth-token` add the following line to this file and save it `export CYBERGRX_API_TOKEN="API-V1 TOKEN FROM UI"`

Once that is done you can source that file into your environment and run the export
- Remember to source your python environment `source env/bin/activate` the first time you run the command
- `source .auth-token`
- `python export.py`
- Open `ecosystem.json` this is the raw payload directly form the API
- Open `ecosystem.xml` this is the payload transformed into an XML representation (fields may be renamed or missing).
- Once you are done **remove** the `.auth-token` file so you do not leak sensitive information.
