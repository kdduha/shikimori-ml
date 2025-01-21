import os
import json
import argparse
import logging
from shikimori.graphql import GraphQLClient
from shikimori import create_logger

from pathlib import Path
from dotenv import load_dotenv


def _parse_args() -> argparse.Namespace:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Shikimori GraphQL CLI client.")
    parser.add_argument("--auth_code", help="Authorization code for initial access token generation.",
                        default=os.getenv("SHIKI_AUTH_CODE"))
    parser.add_argument("--access_token", help="Access token for API access.", default=os.getenv("SHIKI_ACCESS_TOKEN"))
    parser.add_argument("--refresh_token", help="Refresh token for obtaining a new access token.",
                        default=os.getenv("SHIKI_REFRESH_TOKEN"))
    parser.add_argument("--endpoint", help="GraphQL endpoint URL.", default=os.getenv("SHIKI_GRAPHQL_ENDPOINT"))
    parser.add_argument("--refresh_if_expired", action="store_true", help="Automatically refresh token if expired.")

    project_root = Path(__file__).resolve().parent.parent
    query_file_path = project_root / "parse" / "query.txt"
    response_file_path = project_root / "parse" / "response.json"

    parser.add_argument("--query_file", help="Path to the file containing the GraphQL query.", default=query_file_path)
    parser.add_argument("--response_file", help="Path to the file containing the response.",  default=response_file_path)

    return parser.parse_args()


def _init_client(logger: logging.Logger, args: argparse.Namespace) -> GraphQLClient:

    if not args.endpoint:
        raise ValueError(
            "GraphQL endpoint URL must be provided via --endpoint or SHIKI_GRAPHQL_ENDPOINT environment variable.")

    client = GraphQLClient(
        logger=logger,
        url=args.endpoint
    )

    access_token = args.access_token
    refresh_token = args.refresh_token

    if not access_token:
        if not args.auth_code:
            raise ValueError("Authorization code (--auth_code) or access token (--access_token) must be provided.")

        logger.info("Access token not provided, attempting to retrieve using auth_code...")
        access_response = client.get_access_token(args.auth_code)
        access_token = access_response.json().get("access_token")
        refresh_token = access_response.json().get("refresh_token")

        if not access_token or not refresh_token:
            raise ValueError("Failed to retrieve access token and refresh token.")

        logger.info("Access token and refresh token successfully retrieved.")

    elif args.refresh_if_expired:
        logging.info("Attempting to refresh access token if it is expired...")
        refresh_response = client.refresh_access_token(refresh_token)
        access_token = refresh_response.json().get("access_token")
        refresh_token = refresh_response.json().get("refresh_token")

        if not access_token or not refresh_token:
            raise ValueError("Failed to refresh access token.")

        logger.info("Access token successfully refreshed.")

    client.init(access_token)
    logger.info("GraphQL client is ready!")
    return client


def _load_query_json(logger: logging.Logger, file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        logger.info("Query is loaded!")
        return file.read()


if __name__ == "__main__":
    logger = create_logger()

    args = _parse_args()
    client = _init_client(logger, args)
    query = _load_query_json(logger, args.query_file)

    response = client.execute(query, max_pages=int(10_000 / 50))
    logger.info(f"You have parsed {len(response)} entities.")

    if args.response_file:
        with open(args.response_file, 'w') as file:
            json.dump(response, file, indent=4)
    else:
        print(json.dumps(response, indent=4))
