
Here you can find examples, how to parse different shikimori entities via CLI or Python package API. 
These scripts were used to form Kaggle [shikimori-recsys dataset](https://www.kaggle.com/datasets/kdduha/shikimori-recsys).
1. In order to parse genres, run:
    ```sh
    shiki-parse --input=./queries/genres.gql --output-format=csv --output=result/
    ```
1. In order to parse anime (approximately 10k titles), run:
    ```sh
    shiki-parse --input=./queries/anime.gql --output-format=csv --output=result/ --max-pages=200 --timeout=1.5
    ```
1. In order to parse users rates of active users for the last year (not more than 100k users rates), run:
    ```sh
    uv run parse.py \
        --users=5000 \
        --max-rates-per-user=200 \
        --max-random-user-page=1000 \
        --min-random-user-page=100 \
        --output=result/
    ```
