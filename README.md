# rostar
## Setup
### Credentials
In order to run we need a .env file, rename the .env.example file to .env and fill in rostar eduflex credentials.
Example .env should look like this:

    # .env  
    ROSTAR_USER=user@example.com  
    ROSTAR_PASS=changeme  

Next we need to supply the google calender oauth token. Follow the google calender docs to obtain oath credentials and place them in ./data/credentials.json. Run the container with port 8080:8080 to obtain a token.json file.
Currently only localhost is supported. So in order to obtain an oauth token make sure you are following the authorisation url from the same system as the docker container is running. localhost:8080 must be accessible from the container.

### Klassen
Finally, change klassen.csv.example to klassen.csv and fill in the correct details for your class. The "name" field is currently only a display name, and does not need to match any actually klas. The ID can be obtained by looking at the ids of the klas field on the rostar eduflex site. The google calender ID can be obtained by first creating a new google calender on your account, then under "settings and share" navigate to "integrate calender" to obtain the calender-id.