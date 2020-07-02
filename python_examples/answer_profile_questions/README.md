This example application showcases the abilility to submit answers to vendor profile questions in bulk using the [CyberGRX API](https://api.cybergrx.com/v1/swagger/) and an Excel file.  This example is coded using Python, the integration code is contained in [answer_profile.py](./answer_profile.py).  You should run all commands from this directory.

# Running the example
The first step is to configure a virtual environment for the application dependencies.  Depending on the version of Python that you are using the following commands will slightly differ.
- Python 2: `pip install virtualenv && virtualenv env`
- Python 3: `pip3 install virtualenv && python3 -m venv env`
- `source env/bin/activate`
- `pip install -r requirements.txt`

At this point you are all setup to run the example, but before you do, create a file that holds your API token.
- `vi .auth-token` add the following line to this file and save it `export CYBERGRX_API_TOKEN="API-V1 TOKEN FROM UI"`

Once that is done you can source that file into your environment and run the command
- Remember to source your python environment `source env/bin/activate` the first time you run the command
- `source .auth-token`
- This example command assumes that you have a profile-answers.xlsx file containing a list of companies with answers to the scoping profile.  Take a look at the profile-answers.xlsx file in this directory for an example.
- `python answer_profile.py profile-answers.xlsx`
- Once you are done **remove** the `.auth-token` file so you do not leak sensitive information.
