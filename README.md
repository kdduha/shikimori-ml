# shikimori-ml

<div id="stack badges">
    <a href="https://docs.python.org/3/index.html">
        <img src="https://img.shields.io/badge/python-61ca9a?style=for-the-badge&logo=python&logoColor=white" alt="skimage badge"/>
    </a>
    <a href="https://gql.readthedocs.io/en/latest/intro.html">
        <img src="https://img.shields.io/badge/GraphQL-CB2C31?style=for-the-badge&logoColor=white" alt="pytorch badge"/>
    </a>
</div>

pet-project with [shikimori](https://shikimori.one/) data 

## Parse Data
Parsing works with GraphQL API and OAuth2. You can find parsing script [here](shikimori/parse/parse.py) and [shikimori](shikimori/graphql/graphql_client.py) API client here.
In order to parse data from Shikimori with default configuration, you need:

- Get your access_token by this [guide](https://shikimori.one/oauth?oauth_application_id=15&authorization_code=32yz1tIvXUoxxbFBai_IsF9-QHb4aTXE-fYrrUu9MgE#step_2) and write in [`.env`](.env) file
- Replace [GraphQL query request](shikimori/parse/query.txt) with your one. You can test your query firstly in [shikimori playground](https://shikimori.one/api/doc/graphql)
- Use this command and check the result in [`response.json`](shikimori/parse/response.json)
   ```sh
    python3 -m shikimori.parse.parse
    ```
   Example logs:
   ```sh
   2025-01-21 23:53:23,562 - INFO - GraphQL client is ready!
   2025-01-21 23:53:23,562 - INFO - Query is loaded!
   2025-01-21 23:53:24,613 - INFO - Page 1 fetched successfully.
   2025-01-21 23:53:25,027 - INFO - Page 2 fetched successfully.
   ...
   2025-01-21 23:54:56,316 - INFO - Page 149 fetched successfully.
   2025-01-21 23:54:56,664 - ERROR - Error while fetching page 150: 429, message='Too Many Requests', url='https://shikimori.one/api/graphql'
   2025-01-21 23:54:56,664 - INFO - Execution completed in 93.10 seconds
   2025-01-21 23:54:56,664 - INFO - You have parsed 7450 entities.
   ```
   
See in more details command help, if you want to configure the script in another way
```sh
python3 -m shikimori.parse.parse -h

usage: parse.py [-h] [--auth_code AUTH_CODE] [--access_token ACCESS_TOKEN] [--refresh_token REFRESH_TOKEN] [--endpoint ENDPOINT] [--refresh_if_expired] [--query_file QUERY_FILE] [--response_file RESPONSE_FILE] [--max-pages MAX_PAGES]

Shikimori GraphQL CLI client.

options:
  -h, --help            show this help message and exit
  --auth_code AUTH_CODE
                        Authorization code for initial access token generation. By default trying to get from .env file
  --access_token ACCESS_TOKEN
                        Access token for API access. By default trying to get from .env file
  --refresh_token REFRESH_TOKEN
                        Refresh token for obtaining a new access token. By default trying to get from .env file
  --endpoint ENDPOINT   GraphQL endpoint URL. By default trying to get from .env file
  --refresh_if_expired  Set this flag to automatically refresh token if expired.
  --query_file QUERY_FILE
                        Path to the file containing the GraphQL query. By default is shikiromir/parse/query.txt
  --response_file RESPONSE_FILE
                        Path to the file containing the response. By default is shikimori/parse/response.json
  --max-pages MAX_PAGES
                        Max number of pages to be parsed. Each page limit is about 50 entities. By default is int(10_000/50)
```