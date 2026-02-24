import argparse
import os
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from shikimori_parse.client import GraphQLClient
from shikimori_parse.logger import create_logger
from shikimori_parse.utils import save_json

USER_RATE_PER_PAGE = 50
SHIKI_TIMEOUT = 1
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
    client: GraphQLClient,
    query_path: Path,
    n_users: int,
    min_random_page: int,
    max_random_page: int,
    last_online_after: datetime,
) -> list[str]:
    query = query_path.read_text()
    user_ids: set[str] = set()

    attempts = 0
    max_attempts = n_users * 5

    while len(user_ids) < n_users and attempts < max_attempts:
        attempts += 1

        result = client.execute(
            query,
            variables={"page": random.randint(min_random_page, max_random_page)},
            max_pages=1,
        )

        for u in result:
            last_online_raw = u.get("lastOnlineAt")
            if not last_online_raw:
                continue

            last_online = datetime.fromisoformat(last_online_raw.replace("Z", "+00:00"))
            if last_online < last_online_after:
                continue

            user_ids.add(str(u["id"]))
            if len(user_ids) >= n_users:
                break

    return list(user_ids)


def parse_user_rates(
    client: GraphQLClient, user_id: str, query_path: Path, max_pages: int
) -> list[dict]:
    response = client.execute(
        query_path.read_text(), variables={"userId": user_id}, max_pages=max_pages
    )

    result = []
    for r in response:
        if r.get("anime") is None:
            continue

        r["user_id"] = user_id
        result.append(r)

    return result


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
        "--min-random-user-page",
        type=int,
        required=True,
        help="Min random page for users pagination",
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

    load_dotenv()

    args = parser.parse_args()
    logger = create_logger()
    client = init_client()

    users_query = Path("queries/users.gql")
    user_rate_query = Path("queries/userRates.gql")

    logger.info("Parsing user ids...")
    user_ids = parse_users(
        client,
        users_query,
        n_users=args.users,
        min_random_page=args.min_random_user_page,
        max_random_page=args.max_random_user_page,
        last_online_after=datetime.now(timezone.utc)
        - timedelta(days=365),  # active users for the last year
    )
    logger.info(f"Parsed {len(user_ids)} users")

    all_csv = args.output / "users_rates.csv"
    for user_id in user_ids:
        logger.info("Parsing rates for user %s", user_id)

        data = parse_user_rates(
            client,
            user_id,
            user_rate_query,
            max_pages=args.max_rates_per_user // USER_RATE_PER_PAGE,
        )
        if not data:
            continue

        df = pd.DataFrame(data)
        df.to_csv(
            all_csv,
            mode="a",
            index=False,
            header=not all_csv.exists(),
            encoding="utf-8",
        )

    logger.info("All user rates saved to %s", args.output / "user_rates.csv")
