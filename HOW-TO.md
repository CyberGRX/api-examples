# Retrieve a CyberGRX API Token
You must have an active CyberGRX account that has the ability to manage users.

The workflow is pretty simple:
 - Enter `Manage my company user accounts` using the top right navigational element.
 - Click the tab to `Access Tokens`
 - Click the button to `Add a new token`
 - Accept the promt creating a token.
 - Click `view the secret` the secret and copy it, this is the only time that this token will be available over the API!
 - Close the dialog and save your token in a secure location.

 ## CyberGRX Management Workflow
 ![enter-user-management]
 ![add-a-token]
 ![confirm-new-token]
 ![view-token]
 ![copy-secret]


[enter-user-management]: /how-to/enter-user-management.png "Click top right icon and enter `Manage my company user accounts`"

[add-a-token]: /how-to/add-a-token.png "Click the tab to `Manage Access Tokens` and Add a new token"

[confirm-new-token]: /how-to/confirm-new-token.png "Accept the promt creating a token"

[view-token]: /how-to/make-sure-you-view.png "Before leaving view the token secret"

[copy-secret]: /how-to/copy-secret.png "Show the secret and copy it, this is the only time that this token will be available over the API!"


#
# Use a CyberGRX API Token in swagger

## Where

### You can access data from different namespace.

https://api-version-1.`<namespace>`.new-staging.grx-dev.com/v1/swagger/#/

eg: https://api-version-1.master.new-staging.grx-dev.com/v1/swagger/#/

##
## How

 - Click `Authorize` on the page
 - Paste the secret that you saved when creating the token, then click `Authorize`, then close the panel. 
 - Pick the API you want to use. Click `Try it out` 
 - Fill any fields that you want for parameters, then click `Execute`
 - Then you should be able to see the results that you want. 

## Workflow
![log-in-swagger]
![paste-api-secret]
![try-it-out]
![execute]

[Log-in-swagger]: /how-to/log-in-swagger.png "Click `Authorize` on the page "
[paste-api-secret]: /how-to/paste-api-secret.png "Paste the secret that you saved when creating the token, then click `Authorize`, then close the panel. "
[try-it-out]: /how-to/try-it-out.png "Pick the API you want to use. Click `Try it out` "
[execute]: /how-to/execute.png "Fill any fields that you want for parameters, then click `Execute` "


