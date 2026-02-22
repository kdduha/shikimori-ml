import os
import random
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from shikimori_parse.client import GraphQLClient
from shikimori_parse.logger import create_logger
from shikimori_parse.utils import save_json


def init_client() -> GraphQLClient:
    client = GraphQLClient(url="https://shikimori.io")
    client.init(os.getenv("SHIKI_ACCESS_TOKEN"))
    return client


def parse_users(
    client: GraphQLClient, query_path: Path, n_random_pages: int, max_random_page: int
) -> list[str]:
    query = query_path.read_text()
    user_ids: set[str] = set()

    for _ in range(n_random_pages):
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
    load_dotenv()
    logger = create_logger()

    OUTPUT = Path("result")
    RATES_DIR = OUTPUT / "user_rates"
    RATES_DIR.mkdir(parents=True, exist_ok=True)

    client = init_client()

    users_query = Path("queries/users.gql")
    user_rate_query = Path("queries/userRates.gql")

    logger.info("Parsing user ids...")
    user_ids = parse_users(
        client, users_query, n_random_pages=5, max_random_page=100
    )  # max 5 * 50 == 250 users
    logger.info(f"Parsed {len(user_ids)} users")

    all_csv = OUTPUT / "users_rates.csv"
    for user_id in user_ids:
        logger.info("Parsing rates for user %s", user_id)

        data = parse_user_rates(
            client, user_id, user_rate_query, max_pages=10
        )  # max 10 * 50 == 500 rates per user
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

    logger.info("All user rates saved to %s", OUTPUT / "all_user_rates.csv")
    RATES_DIR.rmdir()
