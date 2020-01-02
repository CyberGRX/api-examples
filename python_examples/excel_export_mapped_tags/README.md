This example application showcases the abilility to export an ecosystem and map tags with prefixes to specific columns using the [CyberGRX Bulk API](https://api.cybergrx.com/bulk-v1/swagger/).  This example is coded using Python, the integration code is contained in [export.py](./export.py).  You should run all commands from this directory.

# Tagging formats
This example uses tagging conventions to map tagging values to specific columns within the export.  By using tags to manage these details we can still filter and sort using the CyberGRX user interface, addiitonally we can build standardized exports that we can sync into a GRC tool of our choosing.  Tagging conventions are as follows:
- Tags starting with `BU:` are mapped to the column `Business Unit`
- Tags starting with `VO:` are mapped to the column `Vendor Owner`
- Tags starting with `REG:` are mapped to the column `Regulation`
- All other tags are treated as normal

## Technical details for mapping
Mapping is pretty trivial, we are using glom as a foundational driver to transform API responses into a standardized format for the Excel template.  There are 3 configurations that set that glom state.  Basically we select the tags field from the Third Party response (this is an array of strings), pass that through the tag_categorization filter which only selects tags that start with a prefix.

The following snips are from [export.py](./export.py) and capture the business logic for mapping tags with a specific prefix to a field that can be interpreted by the Excel template.

```
def tag_categorization(tagging_prefix):
    return lambda value: ", ".join([v.replace(tagging_prefix, "", 1).strip() for v in value if v.startswith(tagging_prefix)])

TP_MAPPING = {
    ...
    "business_unit": (Coalesce("tags", default=[]), tag_categorization("BU:")),
    "vendor_owner": (Coalesce("tags", default=[]), tag_categorization("VO:")),
    "regulation": (Coalesce("tags", default=[]), tag_categorization("REG:")),
}
```

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
- `python export.py`
- Once you are done **remove** the `.auth-token` file so you do not leak sensitive information.
