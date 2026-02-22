import csv
import json
from pathlib import Path


def load_queries(input_path: Path) -> list[tuple[str, str]]:
    if input_path.suffix == ".gql":
        return [(input_path.stem, input_path.read_text(encoding="utf-8"))]

    elif input_path.is_dir():
        return [
            (file.stem, file.read_text(encoding="utf-8"))
            for file in sorted(input_path.iterdir())
            if file.is_file() and file.suffix == ".gql"
        ]

    else:
        raise ValueError(
            f"Input path {input_path} is neither a .gql file nor a directory"
        )


def save_json(path: Path, data: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_csv(path: Path, data: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
