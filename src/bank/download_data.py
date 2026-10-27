from io import BytesIO
from pathlib import Path
from shutil import copyfileobj
from urllib.request import urlopen
from zipfile import ZipFile

URL = (
    "https://archive.ics.uci.edu/ml/"
    "machine-learning-databases/00222/bank-additional.zip"
)
ARCHIVE_MEMBER = "bank-additional/bank-additional-full.csv"

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = REPO_ROOT / "datasets" / "bank_additional_pre.csv"


def main() -> None:
    print("Скачивание датасета...")

    with urlopen(URL, timeout=120) as response:
        archive_bytes = response.read()

    with ZipFile(BytesIO(archive_bytes)) as archive:
        archive.getinfo(ARCHIVE_MEMBER)
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

        with archive.open(ARCHIVE_MEMBER) as source:
            with OUTPUT_PATH.open("wb") as destination:
                copyfileobj(source, destination)

    print(f"Датасет сохранён: {OUTPUT_PATH}")
    print(f"Размер файла: {OUTPUT_PATH.stat().st_size:,} байт")


if __name__ == "__main__":
    main()