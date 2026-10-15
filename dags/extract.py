import logging
import time
from pathlib import Path
import requests

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("data/extract.log")],
)


def download_file(url: str, path: Path) -> bool:
    """Télécharge un fichier. Renvoie False si absent (404)."""
    with requests.get(url, stream=True, timeout=60) as response:
        if response.status_code == 404:
            return False
        response.raise_for_status()
        with open(path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)
    return True


def download_months(start: str, end: str) -> None:
    """Télécharge les mois de start à end inclus (format 'YYYY-MM')."""
    for month in months_between(start, end):
        file_name = f"yellow_tripdata_{month}.parquet"
        path = RAW_DIR / file_name

        if path.exists():
            logging.info(f"{file_name} existe déjà, ignoré")
            continue

        try:
            logging.info(f"Téléchargement de {file_name}")
            if not download_file(f"{BASE_URL}/{file_name}", path):
                logging.warning(f"{file_name} introuvable à la source")
        except requests.exceptions.RequestException as e:
            logging.error(f"Erreur sur {file_name} : {e}")
            path.unlink(missing_ok=True)

        time.sleep(1)


def months_between(start: str, end: str) -> list[str]:
    y, m = map(int, start.split("-"))
    y_end, m_end = map(int, end.split("-"))
    result = []
    while (y, m) <= (y_end, m_end):
        result.append(f"{y}-{m:02d}")
        m += 1
        if m > 12:
            y, m = y + 1, 1
    return result


if __name__ == "__main__":
    # Télécharge les 3 premiers mois de l'année en cours (ou adapte selon tes besoins)
    download_months("2026-01", "2026-03")