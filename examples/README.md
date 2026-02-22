
Here you can find examples, how to parse different shikimori entities via CLI or Python package API:
1. In order to parse genres, run:
    ```sh
    shiki-parse --input=./queries/genres.gql --output-format=csv --output=result/
    ```
1. In order to parse anime (approximately 10k titles), run:
    ```sh
    shiki-parse --input=./queries/anime.gql --output-format=csv --output=result/ --max-pages=200 --timeout=1.5
    ```
1. In order to parse users rates (not more than 300k users rates), run:
    ```sh
    uv run parse.py \
        --users 1000 \
        --max-rates-per-user 300 \
        --max-random-user-page 10000 \
        --output=result/
    ```
