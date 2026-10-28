import argparse
import os
import re
import sys
import tempfile
from pathlib import Path
import requests
import snowflake.connector
from dotenv import load_dotenv
from constants import BASE_URL, STAGE, TARGET_MONTH


PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / ".env")


def build_url(month: str) -> str:
    """Construit l'URL du fichier mensuel."""
    filename = f"yellow_tripdata_{month}.parquet"
    return f"{BASE_URL}/{filename}"


def check_file(url: str) -> bool:
    """Vérifie si le fichier est disponible sans le télécharger."""
    response = requests.head(
        url,
        timeout=15,
        allow_redirects=True,
    )

    try:
        if response.status_code == 200:
            return True

        if response.status_code == 404:
            return False

        response.raise_for_status()
        raise RuntimeError(
            f"Réponse HTTP inattendue : {response.status_code}"
        )
    finally:
        response.close()


def download_file(url: str, destination: Path) -> None:
    """Télécharge le fichier par morceaux dans un fichier temporaire."""
    with requests.get(
        url,
        stream=True,
        timeout=(15, 120),
    ) as response:
        response.raise_for_status()

        with destination.open("wb") as file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    file.write(chunk)

    if destination.stat().st_size == 0:
        raise RuntimeError("Le fichier téléchargé est vide.")

    print(f"Téléchargement terminé : {destination.name}")


def upload_to_stage(file_path: Path, month: str) -> None:
    """Dépose le Parquet dans le stage interne Snowflake."""
    required = [
        "DBT_SNOWFLAKE_ACCOUNT",
        "DBT_SNOWFLAKE_USER",
        "DBT_SNOWFLAKE_PASSWORD",
        "DBT_SNOWFLAKE_WAREHOUSE",
        "DBT_SNOWFLAKE_DATABASE",
    ]

    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError(
            f"Variables d'environnement manquantes : {', '.join(missing)}"
        )

    params = {
        "account": os.environ["DBT_SNOWFLAKE_ACCOUNT"],
        "user": os.environ["DBT_SNOWFLAKE_USER"],
        "password": os.environ["DBT_SNOWFLAKE_PASSWORD"],
        "warehouse": os.environ["DBT_SNOWFLAKE_WAREHOUSE"],
        "database": os.environ["DBT_SNOWFLAKE_DATABASE"],
        "schema": "RAW",
    }

    role = os.getenv("DBT_SNOWFLAKE_ROLE")
    if role:
        params["role"] = role

    conn = snowflake.connector.connect(**params)

    try:
        with conn.cursor() as cursor:
            # L'URI est produite à partir du chemin temporaire local.
            file_uri = file_path.resolve().as_uri().replace("'", "''")

            cursor.execute(
                f"PUT '{file_uri}' "
                f"@{STAGE}/yellow/{month}/ "
                "AUTO_COMPRESS = FALSE "
                "OVERWRITE = FALSE"
            )

            columns = [column[0].lower() for column in cursor.description]
            results = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]

            if not results:
                raise RuntimeError("Snowflake n'a retourné aucun résultat PUT.")

            for result in results:
                status = result["status"]

                if status not in ("UPLOADED", "SKIPPED"):
                    raise RuntimeError(
                        f"Échec du transfert : {result}"
                    )

                if status == "SKIPPED":
                    print(
                        "Fichier déjà présent dans le stage : "
                        "aucun remplacement effectué."
                    )
                else:
                    print(
                        f"Fichier déposé : "
                        f"@{STAGE}/yellow/{month}/{file_path.name}"
                    )
    finally:
        conn.close()


def main_extraction() -> int:
    parser = argparse.ArgumentParser(
        description="Télécharge un mois NYC Taxi vers un stage Snowflake."
    )

    parser.add_argument(
        "month",
        nargs="?",
        default=TARGET_MONTH,
        help=f"Mois au format YYYY-MM (par défaut : {TARGET_MONTH})",
        )
    args = parser.parse_args()
    month = args.month

    if not re.fullmatch(r"[0-9]{4}-(0[1-9]|1[0-2])", month):
        print("Mois invalide. Format attendu : YYYY-MM.")
        return 1

    url = build_url(month)
    filename = f"yellow_tripdata_{month}.parquet"

    try:
        print(f"Vérification du fichier pour {month}...")

        if not check_file(url):
            print(f"Fichier non disponible pour le mois {month}.")
            return 1

        # Le dossier temporaire est supprimé à la sortie du bloc,
        # y compris si le téléchargement ou le transfert échoue.
        with tempfile.TemporaryDirectory(prefix="nyc_taxi_") as temp_dir:
            file_path = Path(temp_dir) / filename

            download_file(url, file_path)
            upload_to_stage(file_path, month)

        print("Extraction terminée. Fichier temporaire supprimé.")
        return 0

    except Exception as error:
        print(f"Échec de l'extraction : {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main_extraction())