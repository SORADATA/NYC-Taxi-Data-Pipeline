import logging
import time
from pathlib import Path
import requests


BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

START_MONTH = "2026-01"
END_MONTH = "2026-01"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("data/extract.log", encoding="utf-8"),
    ],
)

logger = logging.getLogger(__name__)


def parse_month(value: str) -> tuple[int, int]:
    """Valide un mois au format YYYY-MM."""
    try:
        year, month = map(int, value.split("-"))
    except ValueError as exc:
        raise ValueError(
            f"Mois invalide : {value!r}. Format attendu : YYYY-MM."
        ) from exc

    if not 1 <= year <= 9999 or not 1 <= month <= 12:
        raise ValueError(f"Mois invalide : {value!r}.")

    if value != f"{year:04d}-{month:02d}":
        raise ValueError(
            f"Format invalide : {value!r}. Format attendu : YYYY-MM."
        )

    return year, month


def months_between(start: str, end: str) -> list[str]:
    """Renvoie les mois entre start et end, bornes incluses."""
    year, month = parse_month(start)
    end_year, end_month = parse_month(end)

    if (year, month) > (end_year, end_month):
        raise ValueError(
            "Le mois de début doit précéder ou égaler le mois de fin."
        )

    months = []

    while (year, month) <= (end_year, end_month):
        months.append(f"{year:04d}-{month:02d}")

        if month == 12:
            year += 1
            month = 1
        else:
            month += 1

    return months


def download_file(url: str, path: Path) -> bool:
    """Télécharge un fichier. Renvoie False si la source retourne 404."""
    temp_path = path.with_suffix(path.suffix + ".part")

    try:
        with requests.get(
            url,
            stream=True,
            timeout=(15, 120),
        ) as response:
            if response.status_code == 404:
                return False

            response.raise_for_status()

            with temp_path.open("wb") as file:
                for chunk in response.iter_content(
                    chunk_size=1024 * 1024
                ):
                    if chunk:
                        file.write(chunk)

        if temp_path.stat().st_size == 0:
            raise ValueError(f"Le fichier téléchargé est vide : {path.name}")

        size_mb = temp_path.stat().st_size / (1024 * 1024)
        temp_path.replace(path)

        logger.info(
            "Téléchargement terminé : %s (%.2f Mio)",
            path.name,
            size_mb,
        )

        return True

    finally:
        temp_path.unlink(missing_ok=True)


def download_months(start: str, end: str) -> None:
    """Télécharge les fichiers mensuels sans modifier ceux déjà présents."""
    months = months_between(start, end)
    failures = []

    for index, month in enumerate(months):
        file_name = f"yellow_tripdata_{month}.parquet"
        path = RAW_DIR / file_name

        if path.exists() and path.stat().st_size > 0:
            logger.info("Fichier déjà présent, ignoré : %s", file_name)
            continue

        url = f"{BASE_URL}/{file_name}"

        try:
            logger.info("Téléchargement : %s", file_name)

            if not download_file(url, path):
                logger.warning(
                    "Fichier absent à la source (404) : %s",
                    file_name,
                )
                failures.append(month)

        except (requests.exceptions.RequestException, OSError, ValueError):
            logger.exception("Échec du téléchargement : %s", file_name)
            failures.append(month)

        if index < len(months) - 1:
            time.sleep(1)

    if failures:
        raise RuntimeError(
            "Extraction incomplète pour les mois : "
            + ", ".join(failures)
        )

    logger.info(
        "Extraction terminée pour la période %s à %s",
        start,
        end,
    )


if __name__ == "__main__":
    download_months(START_MONTH, END_MONTH)