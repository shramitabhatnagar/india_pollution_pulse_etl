import azure.functions as func
import logging
import requests
import pyodbc
import os
from datetime import datetime
from dateutil import parser

app = func.FunctionApp()

def safe_float(value):
    if value in ("NA", "", None, "null", "--"):
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def safe_datetime(date_str):
    if not date_str:
        return None
    try:
        return parser.parse(date_str, dayfirst=True)
    except Exception as e:
        logging.warning(f"Invalid date format '{date_str}': {e}")
        return None

@app.timer_trigger(schedule="0 */5 * * * *", arg_name="mytimer", run_on_startup=True)
def PollutionETL(mytimer: func.TimerRequest) -> None:
    logging.info(f"🔥 PollutionETL started at {datetime.utcnow().isoformat()} UTC")

    try:
        api_key = os.environ["DATA_GOV_API_KEY"]
        sql_conn_str = os.environ["AZURE_SQL_CONNECTION_STRING"]

        url = f"https://api.data.gov.in/resource/3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69?api-key={api_key}&format=json&limit=10000"

        logging.info("Fetching data from API...")
        response = requests.get(url, timeout=90)

        if response.status_code != 200:
            logging.error(f"API error {response.status_code}: {response.text[:300]}")
            return

        data = response.json().get("records", [])
        logging.info(f"Fetched {len(data)} records")

        # Optional: log first record keys for debugging
        if data:
            logging.info(f"Sample record keys: {list(data[0].keys())}")

        conn = pyodbc.connect(sql_conn_str, timeout=90)
        cursor = conn.cursor()
        cursor.fast_executemany = True

        inserted = 0
        skipped = 0
        errors = 0

        for row in data:
            try:
                # Deduplication check
                cursor.execute(
                    """
                    SELECT 1 FROM pollution_raw 
                    WHERE station = ? AND last_update = ? AND pollutant = ?
                    """,
                    row.get('station'),
                    safe_datetime(row.get('last_update')),
                    row.get('pollutant_id')
                )

                if cursor.fetchone():
                    skipped += 1
                    continue

                # ──── CORRECT FIELD NAMES FROM API ─────
                min_val = safe_float(row.get('min_value'))
                max_val = safe_float(row.get('max_value'))
                avg_val = safe_float(row.get('avg_value'))

                cursor.execute(
                    """
                    INSERT INTO pollution_raw 
                    (last_update, state, city, station, latitude, longitude, pollutant, min_val, max_val, avg_val)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        safe_datetime(row.get('last_update')),
                        row.get('state'),
                        row.get('city'),
                        row.get('station'),
                        safe_float(row.get('latitude')),
                        safe_float(row.get('longitude')),
                        row.get('pollutant_id'),
                        min_val,
                        max_val,
                        avg_val
                    )
                )

                inserted += 1

            except pyodbc.Error as sql_err:
                errors += 1
                logging.warning(f"SQL error for station '{row.get('station')}': {sql_err}")
            except Exception as ex:
                errors += 1
                logging.warning(f"Row processing error: {ex} | Row: {row}")

        conn.commit()
        conn.close()

        logging.info(f"✅ Inserted {inserted} new records")
        logging.info(f"⚠️ Skipped {skipped} duplicates")
        logging.info(f"❌ {errors} rows failed")

    except Exception as fatal:
        logging.error(f"❌ FATAL ERROR: {str(fatal)}", exc_info=True)