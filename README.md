# Boilerplate Service
This boilerplate is the starting point for the service developers. The service template provide the following features: 

1. Integration with Postgres for persistence 
2. Integration with Keycloak for OAuth2 authentication and authorization with multi-tenant support
3. Many more goodies such as a consolidated build system, logging, documentation, etc... 
4. Standard approach to testing (in progress)
5. Exposing API documentation (in progress)


## Dependencies 
 - Keycloak for authentication and authorization with its own Postgres Database
 - Redis for session storage and caching
 
The items highlighted before can be built locally using a common generic set of containers maintained at https://github.com/Picket-Homes/sands/tree/master/environment. You will find in that location 
the docker-compose.yml file that contains all the dependencies: 

```shell script
git clone git@github.com:Picket-Homes/sands.git

cd sands/environment
docker-compose up #Create and soot the containers
```

You can stop the containers by running: 
```shell script
docker-compose stop
``` 

You can start the stopped containers by running: 
```shell script
docker-compose start
``` 

You can also read the documentation of [docker](https://www.docker.com/get-started "Please click this link") and 
[docker-compose](https://docs.docker.com/compose/ "Also, please click this link as well"). 
 

## Dev Guide
Start the environment by executing the following in your service repo: 
```shell script
docker-compose up 
```

Validate that your setup works by listing the docker containers:
```shell script
docker ps -a 
```

The output of the command should result in something similar to this: 

```shell script
CONTAINER ID        IMAGE                   COMMAND                  CREATED             STATUS              PORTS                              NAMES
4e61455cb581        jboss/keycloak:latest   "/opt/jboss/tools/do…"   16 minutes ago      Up 16 minutes       0.0.0.0:8080->8080/tcp, 8443/tcp   keycloak
bff27f832b1c        postgres:latest         "docker-entrypoint.s…"   16 minutes ago      Up 16 minutes       0.0.0.0:6432->5432/tcp             books_db
066e87a0c766        postgres:latest         "docker-entrypoint.s…"   16 minutes ago      Up 16 minutes       0.0.0.0:5432->5432/tcp             keycloak_db
029fff786a45        redis:alpine            "docker-entrypoint.s…"   16 minutes ago      Up 16 minutes       0.0.0.0:6379->6379/tcp             redis
```

### Import the authentication realm 
Navigate to the keycloak console available at http://localhost:8080/ and login to the administration console using the credentials: `admin/Pa55w0rd`

One you're logged im import the realm through the interface and import the application realm https://github.com/Picket-Homes/sands/blob/master/environment/keycloak/realm.json`

### Building the service
Run the following to build the service and run the tests: (Keep this thread running so it builds your code everytime you make changes)
```shell script
npm run build 
```

Start the service in development mode:
```shell script
npm run dev 
```

Start the service in production mode
```shell script
npm start 
```

## APIS (Common)
API Notes:

All the API calls will require two headers to be present:
 
| Header        | Value  | Description                                        | Example                                                     |
|---------------|--------|----------------------------------------------------|-------------------------------------------------------------|
| realm         | String | Name of the realm the request is submitted against | realm : "picket"                                            |
| authorization | String | Authorization Bearer header                        | Authorization: "Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAi..." |


### Direct Login 
This is a convenience API to allow direct login with the API:  

Path : `/login`
Method: `POST`
Body : 
```json
{
    "username" : "yalla",
    "password" : "password" 
}
```

Example Response: 

```json
{
    "access_token": {
        "token": "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICIySjZ6dE9oeGEtYVY3d192bk9TbXM5dGZnVlNDSVhhdGJacy1Xc0REb1RVIn0.eyJleHAiOjE2MDMxMzg1MDksImlhdCI6MTYwMzEzODIwOSwianRpIjoiZWYwMTM3NWUtNDM1Ni00MDc1LTk1MjItYWY3MmJkZjUwZmRmIiwiaXNzIjoiaHR0cDovL2xvY2FsaG9zdDo4MDgwL2F1dGgvcmVhbG1zL3BpY2tldCIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiI3YjZkYWQzYi04MmQ1LTQwMzctYWE3Mi03ZWU4YzZlNzcxZDQiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJlbGFyYW9uZSIsInNlc3Npb25fc3RhdGUiOiJjMDc5YTBlNi1hYTNlLTRiNTQtYmVkNi0zNDU4YmVhMDA5OTkiLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbIioiXSwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbImFkbWluIiwidXNlciJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfSwiZWxhcmFvbmUiOnsicm9sZXMiOlsiY29uY2llcmdlIl19fSwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwibmFtZSI6IllhbGxhIFdsYSIsInByZWZlcnJlZF91c2VybmFtZSI6InlhbGxhIiwiZ2l2ZW5fbmFtZSI6IllhbGxhIiwiZmFtaWx5X25hbWUiOiJXbGEiLCJlbWFpbCI6InlhbGxhQHNvbWV5YXJkLmxvY2FsIn0.nNgcSoUkHLVKxd7g0eD5IM9_O4l2i0-HtfcoATVZVLX-mJAs3KrtoQ35dt6ytYOd-mVGztJhF0aAJtpgMPV1Uvj9jNffrxQwuZ6nI4lJ1hLgMV7RSSTjlLVLB6PhGPjyuH_ZP9yr1ND0IxNScXw7KOy6nsFg46QhfZbvfyh21sfQY4Wao-_Lvz0TY7DPfXwgxShXXG6T5zdCf3HwzgnPSzDTgoP6rEwJ9KemSTQgP-rAVwpmqOBP2jADQpT9_tFs-KBwO7wTXGyvfFBENMl1sMqMrQHMSV-1yijFGlU6SDGlwt_VTwOZmlB5sUBA45IksSnaCMPpVILZFamA3PlYFg",
        "clientId": "elaraone",
        "header": {
            "alg": "RS256",
            "typ": "JWT",
            "kid": "2J6ztOhxa-aV7w_vnOSms9tfgVSCIXatbZs-WsDDoTU"
        },
        "content": {
            "exp": 1603138509,
            "iat": 1603138209,
            "jti": "ef01375e-4356-4075-9522-af72bdf50fdf",
            "iss": "http://localhost:8080/auth/realms/picket",
            "aud": "account",
            "sub": "7b6dad3b-82d5-4037-aa72-7ee8c6e771d4",
            "typ": "Bearer",
            "azp": "elaraone",
            "session_state": "c079a0e6-aa3e-4b54-bed6-3458bea00999",
            "acr": "1",
            "allowed-origins": [
                "*"
            ],
            "realm_access": {
                "roles": [
                    "admin",
                    "user"
                ]
            },
            "resource_access": {
                "account": {
                    "roles": [
                        "manage-account",
                        "manage-account-links",
                        "view-profile"
                    ]
                },
                "elaraone": {
                    "roles": [
                        "concierge"
                    ]
                }
            },
            "scope": "openid profile email",
            "email_verified": false,
            "name": "Yalla Wla",
            "preferred_username": "yalla",
            "given_name": "Yalla",
            "family_name": "Wla",
            "email": "yalla@someyard.local"
        },
        "signature": {
            "type": "Buffer",
            "data": []
        },
        "signed": "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICIySjZ6dE9oeGEtYVY3d192bk9TbXM5dGZnVlNDSVhhdGJacy1Xc0REb1RVIn0.eyJleHAiOjE2MDMxMzg1MDksImlhdCI6MTYwMzEzODIwOSwianRpIjoiZWYwMTM3NWUtNDM1Ni00MDc1LTk1MjItYWY3MmJkZjUwZmRmIiwiaXNzIjoiaHR0cDovL2xvY2FsaG9zdDo4MDgwL2F1dGgvcmVhbG1zL3BpY2tldCIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiI3YjZkYWQzYi04MmQ1LTQwMzctYWE3Mi03ZWU4YzZlNzcxZDQiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJlbGFyYW9uZSIsInNlc3Npb25fc3RhdGUiOiJjMDc5YTBlNi1hYTNlLTRiNTQtYmVkNi0zNDU4YmVhMDA5OTkiLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbIioiXSwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbImFkbWluIiwidXNlciJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfSwiZWxhcmFvbmUiOnsicm9sZXMiOlsiY29uY2llcmdlIl19fSwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwibmFtZSI6IllhbGxhIFdsYSIsInByZWZlcnJlZF91c2VybmFtZSI6InlhbGxhIiwiZ2l2ZW5fbmFtZSI6IllhbGxhIiwiZmFtaWx5X25hbWUiOiJXbGEiLCJlbWFpbCI6InlhbGxhQHNvbWV5YXJkLmxvY2FsIn0"
    },
    "refresh_token": {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJlNjUxOWQ0Yy1lOGNkLTRhMDAtODY1Ni1mNjdlMTUxZjQyM2QifQ.eyJleHAiOjE2MDMxNDAwMDksImlhdCI6MTYwMzEzODIwOSwianRpIjoiMGE4ODZkZWItOWI4Yi00Njc5LTg5MmItMjQzZmZlYjJlYzIxIiwiaXNzIjoiaHR0cDovL2xvY2FsaG9zdDo4MDgwL2F1dGgvcmVhbG1zL3BpY2tldCIsImF1ZCI6Imh0dHA6Ly9sb2NhbGhvc3Q6ODA4MC9hdXRoL3JlYWxtcy9waWNrZXQiLCJzdWIiOiI3YjZkYWQzYi04MmQ1LTQwMzctYWE3Mi03ZWU4YzZlNzcxZDQiLCJ0eXAiOiJSZWZyZXNoIiwiYXpwIjoiZWxhcmFvbmUiLCJzZXNzaW9uX3N0YXRlIjoiYzA3OWEwZTYtYWEzZS00YjU0LWJlZDYtMzQ1OGJlYTAwOTk5Iiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCJ9.8e6FNeN3CHQUQh-z-hGMbKEh-8QSduzYmR8fIH9h_qY",
        "header": {
            "alg": "HS256",
            "typ": "JWT",
            "kid": "e6519d4c-e8cd-4a00-8656-f67e151f423d"
        },
        "content": {
            "exp": 1603140009,
            "iat": 1603138209,
            "jti": "0a886deb-9b8b-4679-892b-243ffeb2ec21",
            "iss": "http://localhost:8080/auth/realms/picket",
            "aud": "http://localhost:8080/auth/realms/picket",
            "sub": "7b6dad3b-82d5-4037-aa72-7ee8c6e771d4",
            "typ": "Refresh",
            "azp": "elaraone",
            "session_state": "c079a0e6-aa3e-4b54-bed6-3458bea00999",
            "scope": "openid profile email"
        },
        "signature": {
            "type": "Buffer",
            "data": []
            ]
        },
        "signed": "eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJlNjUxOWQ0Yy1lOGNkLTRhMDAtODY1Ni1mNjdlMTUxZjQyM2QifQ.eyJleHAiOjE2MDMxNDAwMDksImlhdCI6MTYwMzEzODIwOSwianRpIjoiMGE4ODZkZWItOWI4Yi00Njc5LTg5MmItMjQzZmZlYjJlYzIxIiwiaXNzIjoiaHR0cDovL2xvY2FsaG9zdDo4MDgwL2F1dGgvcmVhbG1zL3BpY2tldCIsImF1ZCI6Imh0dHA6Ly9sb2NhbGhvc3Q6ODA4MC9hdXRoL3JlYWxtcy9waWNrZXQiLCJzdWIiOiI3YjZkYWQzYi04MmQ1LTQwMzctYWE3Mi03ZWU4YzZlNzcxZDQiLCJ0eXAiOiJSZWZyZXNoIiwiYXpwIjoiZWxhcmFvbmUiLCJzZXNzaW9uX3N0YXRlIjoiYzA3OWEwZTYtYWEzZS00YjU0LWJlZDYtMzQ1OGJlYTAwOTk5Iiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCJ9"
    },
    "id_token": {
        "token": "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICIySjZ6dE9oeGEtYVY3d192bk9TbXM5dGZnVlNDSVhhdGJacy1Xc0REb1RVIn0.eyJleHAiOjE2MDMxMzg1MDksImlhdCI6MTYwMzEzODIwOSwiYXV0aF90aW1lIjowLCJqdGkiOiI0ZThjOWNlMC02MDFjLTQyOTYtOTIxNi00NjgyMDM0YjIyODgiLCJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwODAvYXV0aC9yZWFsbXMvcGlja2V0IiwiYXVkIjoiZWxhcmFvbmUiLCJzdWIiOiI3YjZkYWQzYi04MmQ1LTQwMzctYWE3Mi03ZWU4YzZlNzcxZDQiLCJ0eXAiOiJJRCIsImF6cCI6ImVsYXJhb25lIiwic2Vzc2lvbl9zdGF0ZSI6ImMwNzlhMGU2LWFhM2UtNGI1NC1iZWQ2LTM0NThiZWEwMDk5OSIsImF0X2hhc2giOiJ2MXhRQlFHYzVpVmx3VmR0MkZFUkZBIiwiYWNyIjoiMSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwibmFtZSI6IllhbGxhIFdsYSIsInByZWZlcnJlZF91c2VybmFtZSI6InlhbGxhIiwiZ2l2ZW5fbmFtZSI6IllhbGxhIiwiZmFtaWx5X25hbWUiOiJXbGEiLCJlbWFpbCI6InlhbGxhQHNvbWV5YXJkLmxvY2FsIn0.dq39HTBrMU98CxPcrGfmQsVEDjMFhZPPeHg3gaBtPdjthML624z1IXJOJ4yO3cFYnb24MaPAQ1423Fe2ZN9mwNjs5RKuNEAEUzVRkxpvjNM98BBpCsRFsqoDshBUx--mOTN7VNcFBWUvEGBxHXnHALX5HzcLKJ60uTf_ANbQXveFqTs_2BiSYQUlz7QlyJfRzYnavXpUaWbEt11Wyp2GTAJYaMR0Hh_6Vq9IT604zLUh25mO5EOX3y8GMtQ50DUp2tb1I21-2IHqCm0xjgAJji5Xsc3Bo2eDvrikzStzRn1Vnw07M0b19bVbTniYdbewLJP3CF6T5Kzmt85_iXFVBw",
        "header": {
            "alg": "RS256",
            "typ": "JWT",
            "kid": "2J6ztOhxa-aV7w_vnOSms9tfgVSCIXatbZs-WsDDoTU"
        },
        "content": {
            "exp": 1603138509,
            "iat": 1603138209,
            "auth_time": 0,
            "jti": "4e8c9ce0-601c-4296-9216-4682034b2288",
            "iss": "http://localhost:8080/auth/realms/picket",
            "aud": "elaraone",
            "sub": "7b6dad3b-82d5-4037-aa72-7ee8c6e771d4",
            "typ": "ID",
            "azp": "elaraone",
            "session_state": "c079a0e6-aa3e-4b54-bed6-3458bea00999",
            "at_hash": "v1xQBQGc5iVlwVdt2FERFA",
            "acr": "1",
            "email_verified": false,
            "name": "Yalla Wla",
            "preferred_username": "yalla",
            "given_name": "Yalla",
            "family_name": "Wla",
            "email": "yalla@someyard.local"
        },
        "signature": {
            "type": "Buffer",
            "data": []
        },
        "signed": "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICIySjZ6dE9oeGEtYVY3d192bk9TbXM5dGZnVlNDSVhhdGJacy1Xc0REb1RVIn0.eyJleHAiOjE2MDMxMzg1MDksImlhdCI6MTYwMzEzODIwOSwiYXV0aF90aW1lIjowLCJqdGkiOiI0ZThjOWNlMC02MDFjLTQyOTYtOTIxNi00NjgyMDM0YjIyODgiLCJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwODAvYXV0aC9yZWFsbXMvcGlja2V0IiwiYXVkIjoiZWxhcmFvbmUiLCJzdWIiOiI3YjZkYWQzYi04MmQ1LTQwMzctYWE3Mi03ZWU4YzZlNzcxZDQiLCJ0eXAiOiJJRCIsImF6cCI6ImVsYXJhb25lIiwic2Vzc2lvbl9zdGF0ZSI6ImMwNzlhMGU2LWFhM2UtNGI1NC1iZWQ2LTM0NThiZWEwMDk5OSIsImF0X2hhc2giOiJ2MXhRQlFHYzVpVmx3VmR0MkZFUkZBIiwiYWNyIjoiMSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwibmFtZSI6IllhbGxhIFdsYSIsInByZWZlcnJlZF91c2VybmFtZSI6InlhbGxhIiwiZ2l2ZW5fbmFtZSI6IllhbGxhIiwiZmFtaWx5X25hbWUiOiJXbGEiLCJlbWFpbCI6InlhbGxhQHNvbWV5YXJkLmxvY2FsIn0"
    },
    "token_type": "bearer",
    "expires_in": 300,
    "__raw": "{\"access_token\":\"eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICIySjZ6dE9oeGEtYVY3d192bk9TbXM5dGZnVlNDSVhhdGJacy1Xc0REb1RVIn0.eyJleHAiOjE2MDMxMzg1MDksImlhdCI6MTYwMzEzODIwOSwianRpIjoiZWYwMTM3NWUtNDM1Ni00MDc1LTk1MjItYWY3MmJkZjUwZmRmIiwiaXNzIjoiaHR0cDovL2xvY2FsaG9zdDo4MDgwL2F1dGgvcmVhbG1zL3BpY2tldCIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiI3YjZkYWQzYi04MmQ1LTQwMzctYWE3Mi03ZWU4YzZlNzcxZDQiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJlbGFyYW9uZSIsInNlc3Npb25fc3RhdGUiOiJjMDc5YTBlNi1hYTNlLTRiNTQtYmVkNi0zNDU4YmVhMDA5OTkiLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbIioiXSwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbImFkbWluIiwidXNlciJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfSwiZWxhcmFvbmUiOnsicm9sZXMiOlsiY29uY2llcmdlIl19fSwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwibmFtZSI6IllhbGxhIFdsYSIsInByZWZlcnJlZF91c2VybmFtZSI6InlhbGxhIiwiZ2l2ZW5fbmFtZSI6IllhbGxhIiwiZmFtaWx5X25hbWUiOiJXbGEiLCJlbWFpbCI6InlhbGxhQHNvbWV5YXJkLmxvY2FsIn0.nNgcSoUkHLVKxd7g0eD5IM9_O4l2i0-HtfcoATVZVLX-mJAs3KrtoQ35dt6ytYOd-mVGztJhF0aAJtpgMPV1Uvj9jNffrxQwuZ6nI4lJ1hLgMV7RSSTjlLVLB6PhGPjyuH_ZP9yr1ND0IxNScXw7KOy6nsFg46QhfZbvfyh21sfQY4Wao-_Lvz0TY7DPfXwgxShXXG6T5zdCf3HwzgnPSzDTgoP6rEwJ9KemSTQgP-rAVwpmqOBP2jADQpT9_tFs-KBwO7wTXGyvfFBENMl1sMqMrQHMSV-1yijFGlU6SDGlwt_VTwOZmlB5sUBA45IksSnaCMPpVILZFamA3PlYFg\",\"expires_in\":300,\"refresh_expires_in\":1800,\"refresh_token\":\"eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJlNjUxOWQ0Yy1lOGNkLTRhMDAtODY1Ni1mNjdlMTUxZjQyM2QifQ.eyJleHAiOjE2MDMxNDAwMDksImlhdCI6MTYwMzEzODIwOSwianRpIjoiMGE4ODZkZWItOWI4Yi00Njc5LTg5MmItMjQzZmZlYjJlYzIxIiwiaXNzIjoiaHR0cDovL2xvY2FsaG9zdDo4MDgwL2F1dGgvcmVhbG1zL3BpY2tldCIsImF1ZCI6Imh0dHA6Ly9sb2NhbGhvc3Q6ODA4MC9hdXRoL3JlYWxtcy9waWNrZXQiLCJzdWIiOiI3YjZkYWQzYi04MmQ1LTQwMzctYWE3Mi03ZWU4YzZlNzcxZDQiLCJ0eXAiOiJSZWZyZXNoIiwiYXpwIjoiZWxhcmFvbmUiLCJzZXNzaW9uX3N0YXRlIjoiYzA3OWEwZTYtYWEzZS00YjU0LWJlZDYtMzQ1OGJlYTAwOTk5Iiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCJ9.8e6FNeN3CHQUQh-z-hGMbKEh-8QSduzYmR8fIH9h_qY\",\"token_type\":\"bearer\",\"id_token\":\"eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICIySjZ6dE9oeGEtYVY3d192bk9TbXM5dGZnVlNDSVhhdGJacy1Xc0REb1RVIn0.eyJleHAiOjE2MDMxMzg1MDksImlhdCI6MTYwMzEzODIwOSwiYXV0aF90aW1lIjowLCJqdGkiOiI0ZThjOWNlMC02MDFjLTQyOTYtOTIxNi00NjgyMDM0YjIyODgiLCJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwODAvYXV0aC9yZWFsbXMvcGlja2V0IiwiYXVkIjoiZWxhcmFvbmUiLCJzdWIiOiI3YjZkYWQzYi04MmQ1LTQwMzctYWE3Mi03ZWU4YzZlNzcxZDQiLCJ0eXAiOiJJRCIsImF6cCI6ImVsYXJhb25lIiwic2Vzc2lvbl9zdGF0ZSI6ImMwNzlhMGU2LWFhM2UtNGI1NC1iZWQ2LTM0NThiZWEwMDk5OSIsImF0X2hhc2giOiJ2MXhRQlFHYzVpVmx3VmR0MkZFUkZBIiwiYWNyIjoiMSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwibmFtZSI6IllhbGxhIFdsYSIsInByZWZlcnJlZF91c2VybmFtZSI6InlhbGxhIiwiZ2l2ZW5fbmFtZSI6IllhbGxhIiwiZmFtaWx5X25hbWUiOiJXbGEiLCJlbWFpbCI6InlhbGxhQHNvbWV5YXJkLmxvY2FsIn0.dq39HTBrMU98CxPcrGfmQsVEDjMFhZPPeHg3gaBtPdjthML624z1IXJOJ4yO3cFYnb24MaPAQ1423Fe2ZN9mwNjs5RKuNEAEUzVRkxpvjNM98BBpCsRFsqoDshBUx--mOTN7VNcFBWUvEGBxHXnHALX5HzcLKJ60uTf_ANbQXveFqTs_2BiSYQUlz7QlyJfRzYnavXpUaWbEt11Wyp2GTAJYaMR0Hh_6Vq9IT604zLUh25mO5EOX3y8GMtQ50DUp2tb1I21-2IHqCm0xjgAJji5Xsc3Bo2eDvrikzStzRn1Vnw07M0b19bVbTniYdbewLJP3CF6T5Kzmt85_iXFVBw\",\"not-before-policy\":1602945694,\"session_state\":\"c079a0e6-aa3e-4b54-bed6-3458bea00999\",\"scope\":\"openid profile email\"}"
}
```


### Logout
Logout the currently logged in user:   
Path : `/logout`
Method: `GET`

### Config (only available to realm admin)
Return the configuration of the service   
Path : `/config`
Method: `GET`

### Healthcheck (only available to realm admin)
Return the configuration of the service   
Path : `/healthcheck`
Method: `GET`


## Book Controller APIs
### Add a book
Add a book to the collection
Path : `/book`
Method: `POST`
Body : `{ title : 'My life', author: 'Donkey Man'}`

### Retrieve a book by id
Add a book to the collection
Path : `/:id`
Method: `GET`


