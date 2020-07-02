This example application showcases the abilility to make changes to company tags in bulk using the [CyberGRX API](https://api.cybergrx.com/v1/swagger/).  This example is coded using Python, the integration code is contained in [apply_tags.py](./apply_tags.py).  You should run all commands from this directory.

# Running the example
The first step is to configure a virtual environment for the application dependencies.  Depending on the version of Python that you are using the following commands will slightly differ.
- Python 2: `pip install virtualenv && virtualenv env`
- Python 3: `pip3 install virtualenv && python3 -m venv env`
- `source env/bin/activate`
- `pip install -r requirements.txt`

At this point you are all setup to run the example, but before you do, create a file that holds your API token.
- `vi .auth-token` add the following line to this file and save it `export CYBERGRX_API_TOKEN="API-V1 TOKEN FROM UI"`

Once that is done you can source that file into your environment and run the apply_tags command
- Remember to source your python environment `source env/bin/activate` the first time you run the command
- `source .auth-token`
- This example command assumes that you have a tagging.xlsx file containing a Test sheet with at least 2 column headers ('Company Name' and 'Tag').  Take a look at the tagging.xlsx file in this directory for an example.
- `python apply_tags.py --company-header="Company Name" --tag-header="Tags" --sheet="Third Parties" tagging.xlsx`
- Once you are done **remove** the `.auth-token` file so you do not leak sensitive information.
