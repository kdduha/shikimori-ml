# shikimori-parse

<div id="stack badges">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/-Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  </a>
  <a href="https://pypi.org/project/gql/">
    <img src="https://img.shields.io/badge/-gql-E535AB?style=for-the-badge&logo=graphql&logoColor=white" alt="gql"/>
  </a>
  <a href="https://uv.io/">
    <img src="https://img.shields.io/badge/-uv-F0DB4F?style=for-the-badge&logo=uv&logoColor=black" alt="uv"/>
  </a>
</div>

CLI tool to parse [Shikimori](https://shikimori.io/) data.
Parsing works with GraphQL API and OAuth2. You can find parsing script [here](src/shikimori_parse/cli.py) and [shikimori](./src/shikimori_parse/client.py) API client here.

You can fine usage examples with CLI or package API [here](./examples). 

## Setup

1. Copy your access token, OAuth2 client id and client secret into `.env` following 
[this guide](https://shikimori.one/oauth?oauth_application_id=15&authorization_code=32yz1tIvXUoxxbFBai_IsF9-QHb4aTXE-fYrrUu9MgE#step_2) (see. [`.env.example`](./.env.example))
1. Install project CLI:

    ```sh
    uv pip install -e .
    export PATH="$PWD/.venv/bin:$PATH"
    ```
1. Prepare your GraphQL queries in `input/` dir (`.gql` files). You can test them first in the [Shikimori GraphQL Playground](https://shikimori.io/api/doc/graphql)
1. Run CLI:
    ```sh
    shiki-parse --help

    usage: shiki-parse [-h] [--client_id CLIENT_ID] [--client_secret CLIENT_SECRET] [--auth_code AUTH_CODE] [--access_token ACCESS_TOKEN] [--refresh_token REFRESH_TOKEN] [--endpoint ENDPOINT] [--refresh_if_expired]
                      [--output-format {json,csv}] [--input INPUT] [--output OUTPUT] [--max-pages MAX_PAGES] [--timeout TIMEOUT]

    Shikimori GraphQL CLI client.

    options:
      -h, --help            show this help message and exit
      --client_id CLIENT_ID
                            OAuth client ID. By default trying to get from .env file SHIKI_CLIENT_ID
      --client_secret CLIENT_SECRET
                            OAuth client secret. By default trying to get from .env file SHIKI_CLIENT_SECRET
      --auth_code AUTH_CODE
                            Authorization code for initial access token generation. By default trying to get from .env file SHIKI_AUTH_CODE
      --access_token ACCESS_TOKEN
                            Access token for API access. By default trying to get from .env file SHIKI_ACCESS_TOKEN
      --refresh_token REFRESH_TOKEN
                            Refresh token for obtaining a new access token. By default trying to get from .env file SHIKI_REFRESH_TOKEN
      --endpoint ENDPOINT   Shikimori base endpoint. By default trying to get from .env file SHIKI_BASE_HOST
      --refresh_if_expired  Set this flag to automatically refresh token if expired.
      --output-format {json,csv}
                            Choose output parsed data format
      --input INPUT         Path to a GraphQL query file (.gql) or a directory with queries. By default is `./input`
      --output OUTPUT       Path to the output with parsed results. By default is `./output`
      --max-pages MAX_PAGES
                            Max number of pages to be parsed. Each page limit is about 50 entities. By default is 1
      --timeout TIMEOUT     Timeout between GraphQL requests.
    ```
