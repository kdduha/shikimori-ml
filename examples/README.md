
Here you can find examples, how to parse different shikimori entities via CLI or Python package API:
1. In order to parse genres, run:
    ```sh
    shiki-parse --input=./queries/genres.gql --output-format=csv --output=result/
    ```
1. In order to parse anime (approximately 10k titles), run:
    ```sh
    shiki-parse --input=./queries/anime.gql --output-format=csv --output=result/ --max-pages=200 --timeout=2
    ```
1. In order to parse users rates, run:
    ```sh
    uv run --dev parse.py
    ```
