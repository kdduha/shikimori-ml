import argparse
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from shikimori_parse.client import GraphQLClient
from shikimori_parse.logger import create_logger
from shikimori_parse.utils import load_queries, save_csv, save_json


def parse_args() -> argparse.Namespace:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Shikimori GraphQL CLI client.")

    parser.add_argument(
        "--client_id",
        help=(
            "OAuth client ID. By default trying to get from .env file SHIKI_CLIENT_ID"
        ),
        type=str,
        default=os.getenv("SHIKI_CLIENT_ID"),
    )
    parser.add_argument(
        "--client_secret",
        help=(
            "OAuth client secret. By default trying to get from .env file SHIKI_CLIENT_SECRET"
        ),
        type=str,
        default=os.getenv("SHIKI_CLIENT_SECRET"),
    )
    parser.add_argument(
        "--auth_code",
        help="Authorization code for initial access token generation. By default trying to get from .env file SHIKI_AUTH_CODE",
        default=os.getenv("SHIKI_AUTH_CODE"),
    )
    parser.add_argument(
        "--access_token",
        help="Access token for API access. By default trying to get from .env file SHIKI_ACCESS_TOKEN",
        type=str,
        default=os.getenv("SHIKI_ACCESS_TOKEN"),
    )
    parser.add_argument(
        "--refresh_token",
        help="Refresh token for obtaining a new access token. By default trying to get from .env file SHIKI_REFRESH_TOKEN",
        type=str,
        default=os.getenv("SHIKI_REFRESH_TOKEN"),
    )
    parser.add_argument(
        "--endpoint",
        help="Shikimori base endpoint. By default trying to get from .env file SHIKI_BASE_HOST",
        type=str,
        default=os.getenv("SHIKI_BASE_HOST"),
    )
    parser.add_argument(
        "--refresh_if_expired",
        action="store_true",
        help="Set this flag to automatically refresh token if expired.",
    )
    parser.add_argument(
        "--output-format",
        help="Choose output parsed data format",
        choices=["json", "csv"],
        default="json",
    )

    root = Path(__file__).resolve().parents[2]
    parser.add_argument(
        "--input",
        help="Path to a GraphQL query file (.gql) or a directory with queries. By default is `./input`",
        default=root / "input",
        type=Path,
    )
    parser.add_argument(
        "--output",
        help="Path to the output with parsed results. By default is `./output`",
        default=root / "output",
        type=Path,
    )
    parser.add_argument(
        "--max-pages",
        help="Max number of pages to be parsed. Each page limit is about 50 entities. By default is 1",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--timeout", help="Timeout between GraphQL requests.", type=float, default=1.0
    )

    return parser.parse_args()


def init_client(logger: logging.Logger, args: argparse.Namespace) -> GraphQLClient:
    client = GraphQLClient(url=args.endpoint, timeout=args.timeout)
    access_token, refresh_token = args.access_token, args.refresh_token

    if not access_token:
        if not args.auth_code:
            raise ValueError("auth_code or access_token is required")

        logger.info("Fetching access token...")
        r = client.get_access_token(args.auth_code).json()
        access_token, refresh_token = r.get("access_token"), r.get("refresh_token")

    elif args.refresh_if_expired:
        logger.info("Refreshing access token...")
        r = client.refresh_access_token(refresh_token).json()
        access_token, refresh_token = r.get("access_token"), r.get("refresh_token")

    if not access_token:
        raise ValueError("Failed to obtain access token")

    client.init(
        access_token, client_id=args.client_id, client_secret=args.client_secret
    )
    logger.info("Init client successfuly")
    return client


def main():
    logger = create_logger()
    args = parse_args()
    client = init_client(logger, args)
    queries = load_queries(args.input)

    for name, query in queries:
        response = client.execute(query, max_pages=args.max_pages)
        logger.info("Parsed %d entities from %s", len(response), name)

        out_file = args.output / f"{name}.{args.output_format}"
        args.output.mkdir(parents=True, exist_ok=True)

        if args.output_format == "json":
            save_json(out_file, response)
        else:
            save_csv(out_file, response)

        logger.info("Saved %s", out_file)


if __name__ == "__main__":
    main()
