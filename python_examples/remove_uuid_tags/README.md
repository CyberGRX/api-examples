# Remove Tags Script 

* Local system requirements:
  - poetry >= 1.3.1

* This is an example script of how to remove tags from a company using UUID's. 
* Ensure that removeTags.py is in the same directory as removeTags.xlsx and pyproject.toml
* All commands should be executed from this directory 


## Exporting an authentication token for use in the virtual environment

- In your portfolio click in the top right corner and under settings select Manage Access Tokens 
- Once you generate a token make sure that you view the secret it should look something like this 
  `API-V1 xxxxxxxxxxxxxxxxxxxxxx==.xxxxxxx+xxxxxxxxxxxxxxxxxxxxx/xxxxxxxxxxxxxx="`
- using a text editor of your choice create a `.auth-token` file
- Inside the `.auth-token` file take your token secret and add:
  `export CYBERGRX_API_TOKEN="API-V1 xxxxxxxxxxxxxxxxxxxxxx==.xxxxxxx+xxxxxxxxxxxxxxxxxxxxx/xxxxxxxxxxxxxx="`
- You have now created your auth-token to source in your environment


## Using the script

* This script requires no arguments to run
* Take the company UUID from your profile and add it to `uuidTags.xlsx`
* Add the tags for each company in the `uuidTags.xlsx`
* Execute the script


```
poetry install
source .auth-token
poetry run python3 removeTags.py 
rm -rf .auth-token
```

Don't forget to remove the auth-token. This is an additional protection for you. 
