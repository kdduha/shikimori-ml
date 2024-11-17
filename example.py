from shikimori import GraphQLClient

import os

from dotenv import load_dotenv

load_dotenv()


def main():
    url = os.environ.get("SHIKI_GRAPHQL_ENDPOINT")
    auth_code = os.environ.get("SHIKI_AUTH_CODE")
    access_token = os.environ.get("SHIKI_ACCESS_TOKEN")
    refresh_token = os.environ.get("SHIKI_REFRESH_TOKEN")

    # -- init base client
    client = GraphQLClient(url=url)

    # -- firstly you need to get your access token
    # access_response = client.get_access_token(auth_code)

    # -- if access token is dead you need to refresh it
    # refresh_token = access_response.json().get("refresh_token")
    # refresh_response = client.refresh_access_token(refresh_token)

    client.init(access_token)

    # -- simple query example
    query = """
      query {
          users(limit: 10) {
            nickname
          }
        }
    """

    response = client.execute(query)
    print(response)

    # {'users': [{'nickname': 'GSRD'}, {'nickname': 'Rawamon'}, {'nickname': 'Pastor Uezermon'},
    # {'nickname': 'SSYU'}, {'nickname': 'goidoslav'}, {'nickname': 'Asmadeus_W.Kruger'},
    # {'nickname': 'Bimitrovkaaa'}, {'nickname': 'ruyy lion'}, {'nickname': 'A_y_f_1'},
    # {'nickname': 'Jack The-Riper'}]}


if __name__ == "__main__":
    main()
