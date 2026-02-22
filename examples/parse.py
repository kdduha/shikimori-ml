import argparse
import os
import random
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from shikimori_parse.client import GraphQLClient
from shikimori_parse.logger import create_logger
from shikimori_parse.utils import save_json

USERS_PER_PAGE = 50
SHIKI_TIMEOUT = 1.5
SHIKI_URL = "https://shikimori.io"
SHIKI_ACCESS_TOKEN_ENV = "SHIKI_ACCESS_TOKEN"
SHIKI_CLIENT_ID_ENV = "SHIKI_CLIENT_ID"
SHIKI_CLIENT_SECRET_ENV = "SHIKI_CLIENT_SECRET"


def init_client() -> GraphQLClient:
    client = GraphQLClient(url=SHIKI_URL, timeout=SHIKI_TIMEOUT)
    client.init(
        access_token=os.getenv(SHIKI_ACCESS_TOKEN_ENV),
        client_id=os.getenv(SHIKI_CLIENT_ID_ENV),
        client_secret=os.getenv(SHIKI_CLIENT_SECRET_ENV),
    )
    return client


def parse_users(
    client: GraphQLClient, query_path: Path, n_users: int, max_random_page: int
) -> list[str]:
    query = query_path.read_text()
    user_ids: set[str] = set()

    pages_needed = n_users // USERS_PER_PAGE
    for _ in range(pages_needed):
        page = random.randint(1, max_random_page)
        result = client.execute(
            query,
            variables={"page": page},
            max_pages=1,
        )
        for u in result:
            user_ids.add(str(u["id"]))

    return list(user_ids)


def parse_user_rates(
    client: GraphQLClient, user_id: str, query_path: Path, max_pages: int
) -> list[dict]:
    response = client.execute(
        query_path.read_text(), variables={"userId": user_id}, max_pages=max_pages
    )
    for r in response:
        r["user_id"] = user_id
    return response


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Shikimori user rates parser")

    parser.add_argument(
        "--users",
        type=int,
        required=True,
        help="Approximate number of users to parse",
    )
    parser.add_argument(
        "--max-rates-per-user",
        type=int,
        required=True,
        help="Approximate number of anime rates per user",
    )
    parser.add_argument(
        "--max-random-user-page",
        type=int,
        required=True,
        help="Maximum random page for users pagination",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output directory",
    )

    args = parser.parse_args()
    load_dotenv()
    logger = create_logger()

    RATES_DIR = args.output / "user_rates"
    RATES_DIR.mkdir(parents=True, exist_ok=True)

    client = init_client()

    users_query = Path("queries/users.gql")
    user_rate_query = Path("queries/userRates.gql")

    logger.info("Parsing user ids...")
    user_ids = parse_users(
        client,
        users_query,
        n_users=args.users,
        max_random_page=args.max_random_user_page,
    )
    logger.info(f"Parsed {len(user_ids)} users")

    all_csv = args.output / "users_rates.csv"
    for user_id in user_ids:
        logger.info("Parsing rates for user %s", user_id)

        data = parse_user_rates(
            client, user_id, user_rate_query, max_pages=args.max_rates_per_user
        )
        if not data:
            continue

        tmp_json = RATES_DIR / f"user_{user_id}.json"
        save_json(tmp_json, data)
        tmp_json.unlink()

        df = pd.DataFrame(data)
        df.to_csv(
            all_csv,
            mode="a",
            index=False,
            header=not all_csv.exists(),
            encoding="utf-8",
        )

    logger.info("All user rates saved to %s", args.output / "user_rates.csv")
    RATES_DIR.rmdir()
