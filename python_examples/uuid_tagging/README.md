# UUID Tagging Script 

* Local system requirements:
  - poetry >= 1.3.1 
  - virtualenv >= 20.16.7 

- This is an example script of how to apply tags to a company using UUID's. 
- Ensure that uuidTags.py is in the same directory as uuidTags.xlsx and pyproject.toml
- All commands should be executed from this directory 


*** exporting an authentication token for use in the virtual environment ***
- In your portfolio click in the top right corner and under settings select Manage Access Tokens 
- Once you generate a token make sure that you view the secret it should look something like this 
  API-V1 xxxxxxxxxxxxxxxxxxxxxx==.xxxxxxx+xxxxxxxxxxxxxxxxxxxxx/xxxxxxxxxxxxxx="
- using a text editor of your choice create a .auth-token file
- Inside the .auth-token file take your token secret and add:
  export CYBERGRX_API_TOKEN="API-V1 xxxxxxxxxxxxxxxxxxxxxx==.xxxxxxx+xxxxxxxxxxxxxxxxxxxxx/xxxxxxxxxxxxxx="
- You have now created your auth-token to source in your environment


# This script requires 0 arguments to run. 
# Take the company UUID from your profile and add it to the uuidTags.xlsx
# Add the tags for each company in the uuidTags.xlsx
# Execute the script

* step 1 only needs to be executed once on your local system  
1. pip3 install poetry 
   pip3 install virtualenv 

* create your virtual environment  directory   
2. python3 -m venv env

* install requirements
3. poetry install 

* source API token
4. source .auth-token

* execute the script
5. python3 uuidTags.py 

* once complete deactivate the virtual environment
6. deactivate

* remove .auth-token
7 rm -rf .auth-token

- Don't forget to remove the auth-token. This is an additional protection for you. 