import csv
import os
import time
from collections import defaultdict
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
import urllib3
from requests.exceptions import RequestException, SSLError
from urllib3.exceptions import InsecureRequestWarning


def read_bool_env(name, default=False):
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes"}


def read_positive_int_env(name, default):
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        value = int(raw_value)
        if value <= 0:
            raise ValueError
        return value
    except ValueError:
        print(f"Valeur invalide {name}={raw_value!r}, default={default}.")
        return default


def read_non_negative_int_env(name, default):
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        value = int(raw_value)
        if value < 0:
            raise ValueError
        return value
    except ValueError:
        print(f"Valeur invalide {name}={raw_value!r}, default={default}.")
        return default


def first_non_empty(*values):
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


def normalize_sample_name(value):
    text = first_non_empty(value)
    text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    return " ".join(text.split())


def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def count_rows(path):
    with open(path, "r", encoding="utf-8-sig") as handle:
        line_count = sum(1 for _ in handle)
    return max(0, line_count - 1)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(
    os.getenv("VIOME_DATA_ROOT", str(PROJECT_ROOT / "Data" / "Data_proccesing"))
).resolve()

METADATA_PATH = DATA_ROOT / "Viome_microbiome_metadata.csv"
SPECIES_PATH = (
    DATA_ROOT
    / "viome-abundance"
    / "abundance"
    / "Viome_species_readcount_40samples.csv"
)
FUNCTION_PATH = (
    DATA_ROOT
    / "viome-abundance"
    / "abundance"
    / "Viome_function_KO_readcount_40samples.csv"
)

API_ROOT = os.getenv("MGRAST_API_ROOT", "https://api.mg-rast.org").rstrip("/")
SEARCH_URL = os.getenv("BIOBANK_SEARCH_URL", f"{API_ROOT}/search").strip()
MATRIX_ORGANISM_URL = os.getenv("BIOBANK_MATRIX_ORGANISM_URL", f"{API_ROOT}/matrix/organism")
MATRIX_FUNCTION_URL = os.getenv("BIOBANK_MATRIX_FUNCTION_URL", f"{API_ROOT}/matrix/function")

TARGET_SAMPLES = read_positive_int_env("BIOBANK_TARGET_SAMPLES", 40)
SEARCH_PAGE_SIZE = read_positive_int_env("BIOBANK_SEARCH_PAGE_SIZE", 100)
SEARCH_MAX_PAGES = read_positive_int_env("BIOBANK_SEARCH_MAX_PAGES", 150)
SEARCH_SEQUENCE_TYPE = os.getenv("BIOBANK_SEQUENCE_TYPE", "WGS")

TOP_SPECIES_FEATURES = read_non_negative_int_env("BIOBANK_TOP_SPECIES", 2500)
TOP_FUNCTION_FEATURES = read_non_negative_int_env("BIOBANK_TOP_FUNCTIONS", 5000)

TIMEOUT_SECONDS = read_positive_int_env("BIOBANK_TIMEOUT_SECONDS", 120)
POLL_INTERVAL_SECONDS = read_positive_int_env("BIOBANK_POLL_INTERVAL_SECONDS", 5)
POLL_MAX_TRIES = read_positive_int_env("BIOBANK_POLL_MAX_TRIES", 120)

ALLOW_INSECURE_SSL = read_bool_env("BIOBANK_ALLOW_INSECURE_SSL", default=False)
AUTO_INSECURE_FALLBACK = read_bool_env("BIOBANK_AUTO_INSECURE_FALLBACK", default=True)

MATRIX_IDENTITY = read_positive_int_env("BIOBANK_MATRIX_IDENTITY", 60)
MATRIX_LENGTH = read_positive_int_env("BIOBANK_MATRIX_LENGTH", 15)
MATRIX_EVALUE = read_positive_int_env("BIOBANK_MATRIX_EVALUE", 5)
MATRIX_BATCH_SIZE = read_positive_int_env("BIOBANK_MATRIX_BATCH_SIZE", 10)
MATRIX_RETRIES = read_positive_int_env("BIOBANK_MATRIX_RETRIES", 3)
MATRIX_RETRY_SLEEP_SECONDS = read_positive_int_env("BIOBANK_MATRIX_RETRY_SLEEP_SECONDS", 3)
MATRIX_SINGLE_ID_RETRIES = read_positive_int_env("BIOBANK_MATRIX_SINGLE_ID_RETRIES", 1)

FAILED_SPECIES_IDS_PATH = DATA_ROOT / "biobank_failed_species_ids.txt"
FAILED_FUNCTION_IDS_PATH = DATA_ROOT / "biobank_failed_function_ids.txt"


class MGRASTClient:
    def __init__(self):
        self.session = requests.Session()
        self.ssl_fallback_used = False
        self.force_insecure = False

    def get_json(self, url, params=None):
        if self.force_insecure:
            return self._get_json_once(url, params=params, verify_ssl=False)
        try:
            return self._get_json_once(url, params=params, verify_ssl=True)
        except SSLError:
            if not ALLOW_INSECURE_SSL and not AUTO_INSECURE_FALLBACK:
                raise
            if not self.ssl_fallback_used:
                urllib3.disable_warnings(InsecureRequestWarning)
                print("Warning: SSL verification disabled for MG-RAST requests.")
                self.ssl_fallback_used = True
            self.force_insecure = True
            return self._get_json_once(url, params=params, verify_ssl=False)

    def _get_json_once(self, url, params, verify_ssl):
        response = self.session.get(
            url, params=params, timeout=TIMEOUT_SECONDS, verify=verify_ssl
        )
        response.raise_for_status()
        try:
            return response.json()
        except ValueError as exc:
            snippet = response.text[:200].replace("\n", " ")
            raise RuntimeError(f"Non-JSON response from {response.url}: {snippet}") from exc


def payload_is_matrix(payload):
    return (
        isinstance(payload, dict)
        and isinstance(payload.get("rows"), list)
        and isinstance(payload.get("columns"), list)
        and isinstance(payload.get("data"), list)
    )


def wait_matrix_payload(client, payload):
    if payload_is_matrix(payload):
        return payload

    current = payload
    for attempt in range(1, POLL_MAX_TRIES + 1):
        poll_url = current.get("url")
        status = str(current.get("status", "")).strip() or "pending"

        if payload_is_matrix(current):
            return current

        if not poll_url:
            keys = list(current.keys()) if isinstance(current, dict) else []
            raise RuntimeError(
                "Reponse matrix inattendue (pas de rows/columns/data ni url de polling). "
                f"Keys={keys[:10]}"
            )

        print(f"[matrix] status={status} poll={attempt}/{POLL_MAX_TRIES}")
        time.sleep(POLL_INTERVAL_SECONDS)
        current = client.get_json(urljoin(f"{API_ROOT}/", str(poll_url)))

    raise TimeoutError("Timeout pendant l'attente du calcul matrix MG-RAST.")


def item_id(item):
    if isinstance(item, dict):
        return str(item.get("id", "")).strip()
    return str(item).strip()


def item_metadata(item):
    if isinstance(item, dict) and isinstance(item.get("metadata"), dict):
        return item.get("metadata")
    return {}


def matrix_column_ids(matrix_payload):
    return [item_id(col) for col in matrix_payload.get("columns", [])]


def matrix_column_ids_from_payloads(matrix_payloads):
    ordered = []
    seen = set()
    for payload in matrix_payloads:
        for col_id in matrix_column_ids(payload):
            if col_id and col_id not in seen:
                seen.add(col_id)
                ordered.append(col_id)
    return ordered


def collect_column_metadata(matrix_payloads):
    metadata_by_id = {}
    for payload in matrix_payloads:
        for col in payload.get("columns", []):
            col_id = item_id(col)
            if not col_id or col_id in metadata_by_id:
                continue
            metadata_by_id[col_id] = item_metadata(col)
    return metadata_by_id


def is_human_gut_record(record):
    text_fields = [
        "biome",
        "material",
        "feature",
        "env_package",
        "env_package_name",
        "env_package_type",
        "host",
        "host_name",
        "host_taxon",
        "name",
        "sample_name",
        "location",
    ]
    text = " ".join(str(record.get(field, "")) for field in text_fields).lower()
    has_stool = any(token in text for token in ("stool", "feces", "faeces"))
    has_human_gut = "human-gut" in text or "human gut" in text
    has_gut_and_human = (
        ("gut" in text or "intestin" in text)
        and ("human" in text or "homo sapiens" in text)
    )
    return has_stool or has_human_gut or has_gut_and_human


def collect_human_gut_metagenomes(client):
    selected = []
    seen_ids = set()

    url = SEARCH_URL
    params = None
    if not urlparse(SEARCH_URL).query:
        params = {
            "sequence_type": SEARCH_SEQUENCE_TYPE,
            "limit": SEARCH_PAGE_SIZE,
            "order": "metagenome_id",
            "direction": "asc",
            "match": "all",
        }

    pages = 0
    while url and pages < SEARCH_MAX_PAGES and len(selected) < TARGET_SAMPLES:
        payload = client.get_json(url, params=params)
        params = None
        pages += 1

        data = payload.get("data", [])
        if not isinstance(data, list):
            raise RuntimeError("Reponse /search invalide: 'data' doit etre une liste.")

        for record in data:
            metagenome_id = str(record.get("metagenome_id", "")).strip()
            if not metagenome_id or metagenome_id in seen_ids:
                continue
            if not is_human_gut_record(record):
                continue
            seen_ids.add(metagenome_id)
            selected.append(record)
            if len(selected) >= TARGET_SAMPLES:
                break

        print(f"[search] page={pages} selected={len(selected)}")
        next_url = payload.get("next")
        url = next_url if isinstance(next_url, str) and next_url.strip() else None

    if not selected:
        raise RuntimeError(
            "Aucun echantillon human-gut trouve. "
            "Augmente BIOBANK_SEARCH_MAX_PAGES ou ajuste BIOBANK_SEARCH_URL."
        )

    if len(selected) < TARGET_SAMPLES:
        print(
            f"Warning: seulement {len(selected)} echantillons trouves "
            f"(cible={TARGET_SAMPLES})."
        )

    return selected


def chunks(values, size):
    for idx in range(0, len(values), size):
        yield values[idx : idx + size]


def fetch_matrix_once(client, endpoint_url, metagenome_ids, extra_params):
    params = []
    for mgid in metagenome_ids:
        params.append(("id", mgid))
    for key, value in extra_params.items():
        params.append((key, value))
    payload = client.get_json(endpoint_url, params=params)
    return wait_matrix_payload(client, payload)


def fetch_matrix_with_retry(client, endpoint_url, metagenome_ids, extra_params):
    last_error = None
    retries = MATRIX_SINGLE_ID_RETRIES if len(metagenome_ids) == 1 else MATRIX_RETRIES
    retries = max(1, retries)

    for attempt in range(1, retries + 1):
        try:
            return fetch_matrix_once(client, endpoint_url, metagenome_ids, extra_params)
        except (RequestException, RuntimeError, TimeoutError) as exc:
            last_error = exc
            status_code = getattr(getattr(exc, "response", None), "status_code", None)
            if status_code == 500:
                # MG-RAST returns deterministic 500 for some IDs/combos: no useful retry.
                break
            if attempt < retries:
                print(
                    f"[matrix] retry {attempt}/{retries} for batch size={len(metagenome_ids)}"
                )
                time.sleep(MATRIX_RETRY_SLEEP_SECONDS * attempt)
    raise last_error


def fetch_matrix_resilient(client, endpoint_url, metagenome_ids, extra_params):
    if not metagenome_ids:
        return [], []

    try:
        payload = fetch_matrix_with_retry(client, endpoint_url, metagenome_ids, extra_params)
        return [payload], []
    except (RequestException, RuntimeError, TimeoutError) as exc:
        if len(metagenome_ids) == 1:
            print(f"[matrix] skip {metagenome_ids[0]} after failures: {exc}")
            return [], [metagenome_ids[0]]
        mid = len(metagenome_ids) // 2
        left_ids = metagenome_ids[:mid]
        right_ids = metagenome_ids[mid:]
        print(
            f"[matrix] split batch size={len(metagenome_ids)} -> "
            f"{len(left_ids)} + {len(right_ids)}"
        )
        left_payloads, left_failed = fetch_matrix_resilient(
            client, endpoint_url, left_ids, extra_params
        )
        right_payloads, right_failed = fetch_matrix_resilient(
            client, endpoint_url, right_ids, extra_params
        )
        return left_payloads + right_payloads, left_failed + right_failed


def fetch_matrix_batches(client, endpoint_url, metagenome_ids, extra_params):
    payloads = []
    failed = []
    for batch_ids in chunks(metagenome_ids, MATRIX_BATCH_SIZE):
        print(f"[matrix] request batch size={len(batch_ids)}")
        batch_payloads, batch_failed = fetch_matrix_resilient(
            client, endpoint_url, batch_ids, extra_params
        )
        payloads.extend(batch_payloads)
        failed.extend(batch_failed)
    return payloads, failed


def iter_matrix_entries(matrix_payload, selected_rows=None, allowed_cols=None):
    rows = matrix_payload.get("rows", [])
    cols = matrix_payload.get("columns", [])
    data = matrix_payload.get("data", [])
    matrix_type = str(matrix_payload.get("matrix_type", "dense")).lower()

    row_ids = [item_id(row) for row in rows]
    row_meta = [item_metadata(row) for row in rows]
    col_ids = [item_id(col) for col in cols]
    col_meta = [item_metadata(col) for col in cols]

    if matrix_type == "sparse":
        for triple in data:
            if not isinstance(triple, (list, tuple)) or len(triple) < 3:
                continue
            r_idx = int(triple[0])
            c_idx = int(triple[1])
            value = safe_float(triple[2])
            if value <= 0:
                continue
            if r_idx < 0 or r_idx >= len(row_ids) or c_idx < 0 or c_idx >= len(col_ids):
                continue
            if selected_rows is not None and r_idx not in selected_rows:
                continue
            col_id = col_ids[c_idx]
            if allowed_cols is not None and col_id not in allowed_cols:
                continue
            yield r_idx, row_ids[r_idx], row_meta[r_idx], col_id, col_meta[c_idx], value
        return

    for r_idx, row_values in enumerate(data):
        if selected_rows is not None and r_idx not in selected_rows:
            continue
        if not isinstance(row_values, list):
            continue
        for c_idx, value in enumerate(row_values):
            if c_idx >= len(col_ids):
                continue
            number = safe_float(value)
            if number <= 0:
                continue
            col_id = col_ids[c_idx]
            if allowed_cols is not None and col_id not in allowed_cols:
                continue
            yield r_idx, row_ids[r_idx], row_meta[r_idx], col_id, col_meta[c_idx], number


def top_rows_by_total(matrix_payloads, top_n, allowed_cols):
    if top_n <= 0:
        return None

    totals = defaultdict(float)
    for payload in matrix_payloads:
        for _, row_id, _, _, _, value in iter_matrix_entries(
            payload, selected_rows=None, allowed_cols=allowed_cols
        ):
            if row_id:
                totals[row_id] += value

    if len(totals) <= top_n:
        return None

    ranked = sorted(totals.items(), key=lambda pair: pair[1], reverse=True)[:top_n]
    return {row_id for row_id, _ in ranked}


def build_sample_name_map(ordered_ids, column_metadata_by_id, record_by_mgid):
    used_names = set()
    mapping = {}

    for mgid in ordered_ids:
        meta = column_metadata_by_id.get(mgid, {})
        record = record_by_mgid.get(mgid, {})
        base_name = normalize_sample_name(
            first_non_empty(
                meta.get("sample_name"),
                meta.get("name"),
                meta.get("library_name"),
                record.get("sample_name"),
                record.get("name"),
                record.get("library_name"),
                mgid,
            )
        )
        if not base_name:
            base_name = mgid

        name = base_name
        suffix = 2
        while name in used_names:
            name = f"{base_name}__{suffix}"
            suffix += 1
        used_names.add(name)
        mapping[mgid] = name

    return mapping


def format_count(value):
    int_value = int(value)
    if abs(value - int_value) < 1e-9:
        return int_value
    return round(value, 6)


def write_species_csv(path, matrix_payloads, sample_name_map, allowed_cols, top_rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    headers = [
        "sample_name",
        "species_name",
        "species_readcount",
        "genus_name",
        "family_name",
        "order_name",
        "class_name",
        "phylum_name",
    ]

    written = 0
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for payload in matrix_payloads:
            for _, row_id, row_meta, col_id, _, value in iter_matrix_entries(
                payload, selected_rows=None, allowed_cols=allowed_cols
            ):
                if top_rows is not None and row_id not in top_rows:
                    continue
                species_name = first_non_empty(row_id)
                if not species_name:
                    continue
                genus_name = first_non_empty(row_meta.get("genus"))
                if not genus_name:
                    genus_name = species_name.split(" ")[0] if " " in species_name else ""

                writer.writerow(
                    {
                        "sample_name": sample_name_map[col_id],
                        "species_name": species_name,
                        "species_readcount": format_count(value),
                        "genus_name": first_non_empty(genus_name),
                        "family_name": first_non_empty(row_meta.get("family")),
                        "order_name": first_non_empty(row_meta.get("order")),
                        "class_name": first_non_empty(row_meta.get("class")),
                        "phylum_name": first_non_empty(row_meta.get("phylum")),
                    }
                )
                written += 1
    return written


def write_function_csv(path, matrix_payloads, sample_name_map, allowed_cols, top_rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    headers = [
        "sample_name",
        "function_name",
        "readcount",
        "function_entry",
        "function_definition",
    ]

    written = 0
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for payload in matrix_payloads:
            for _, row_id, row_meta, col_id, _, value in iter_matrix_entries(
                payload, selected_rows=None, allowed_cols=allowed_cols
            ):
                if top_rows is not None and row_id not in top_rows:
                    continue
                function_name = first_non_empty(row_id)
                if not function_name:
                    continue
                function_entry = first_non_empty(
                    row_meta.get("id"), row_meta.get("accession"), function_name
                )
                function_definition = first_non_empty(
                    row_meta.get("function"),
                    row_meta.get("name"),
                    row_meta.get("description"),
                    "",
                )

                writer.writerow(
                    {
                        "sample_name": sample_name_map[col_id],
                        "function_name": function_name,
                        "readcount": format_count(value),
                        "function_entry": function_entry,
                        "function_definition": function_definition,
                    }
                )
                written += 1
    return written


def build_metadata_rows(ordered_ids, sample_name_map, record_by_mgid):
    rows = []
    pair_index = 1
    idx = 0
    while idx < len(ordered_ids):
        id_t1 = ordered_ids[idx]
        id_t2 = ordered_ids[idx + 1] if idx + 1 < len(ordered_ids) else None
        rec_t1 = record_by_mgid.get(id_t1, {})
        rec_t2 = record_by_mgid.get(id_t2, {}) if id_t2 else {}

        age = first_non_empty(rec_t1.get("age"), rec_t2.get("age"), "")
        gender = first_non_empty(rec_t1.get("gender"), rec_t2.get("gender"), "U")
        bmi = first_non_empty(rec_t1.get("bmi"), rec_t2.get("bmi"), "")
        symptom_t1 = first_non_empty(rec_t1.get("symptom_level"), rec_t1.get("symptom"), "Unknown")
        symptom_t2 = (
            first_non_empty(rec_t2.get("symptom_level"), rec_t2.get("symptom"), "Unknown")
            if id_t2
            else ""
        )

        rows.append(
            {
                "subject_id": f"BIOBANK_{pair_index:04d}",
                "age": age,
                "gender": gender,
                "bmi": bmi,
                "symptom_T1": symptom_t1,
                "symptome_T2": symptom_t2,
                "sample_name_T1": sample_name_map[id_t1],
                "sample_name_T2": sample_name_map[id_t2] if id_t2 else "",
            }
        )
        pair_index += 1
        idx += 2
    return rows


def write_metadata_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    headers = [
        "subject_id",
        "age",
        "gender",
        "bmi",
        "symptom_T1",
        "symptome_T2",
        "sample_name_T1",
        "sample_name_T2",
    ]
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def write_failed_ids(path, failed_ids):
    unique_ids = sorted({str(x).strip() for x in failed_ids if str(x).strip()})
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        for mgid in unique_ids:
            handle.write(f"{mgid}\n")


def main():
    print("Recuperation biobanque MG-RAST -> format notebook BiomeX")
    print(f"Sortie: {DATA_ROOT}")
    print(f"Cible echantillons: {TARGET_SAMPLES}")

    client = MGRASTClient()
    selected_records = collect_human_gut_metagenomes(client)
    selected_ids = [str(record["metagenome_id"]).strip() for record in selected_records]
    record_by_mgid = {str(record["metagenome_id"]).strip(): record for record in selected_records}

    print(f"Metagenomes retenus: {len(selected_ids)}")

    species_payloads, species_failed = fetch_matrix_batches(
        client,
        MATRIX_ORGANISM_URL,
        selected_ids,
        extra_params={
            "group_level": "species",
            "source": "RefSeq",
            "result_type": "abundance",
            "identity": MATRIX_IDENTITY,
            "length": MATRIX_LENGTH,
            "evalue": MATRIX_EVALUE,
        },
    )

    function_payloads, function_failed = fetch_matrix_batches(
        client,
        MATRIX_FUNCTION_URL,
        selected_ids,
        extra_params={
            "group_level": "function",
            "source": "KO",
            "result_type": "abundance",
            "identity": MATRIX_IDENTITY,
            "length": MATRIX_LENGTH,
            "evalue": MATRIX_EVALUE,
        },
    )

    if species_failed:
        print(f"Warning: species matrix failed ids={len(species_failed)}")
        write_failed_ids(FAILED_SPECIES_IDS_PATH, species_failed)
        print(f"- failed species ids -> {FAILED_SPECIES_IDS_PATH}")
    if function_failed:
        print(f"Warning: function matrix failed ids={len(function_failed)}")
        write_failed_ids(FAILED_FUNCTION_IDS_PATH, function_failed)
        print(f"- failed function ids -> {FAILED_FUNCTION_IDS_PATH}")

    species_ids = set(matrix_column_ids_from_payloads(species_payloads))
    function_ids = set(matrix_column_ids_from_payloads(function_payloads))
    common_ids = [mgid for mgid in selected_ids if mgid in species_ids and mgid in function_ids]

    if not common_ids:
        raise RuntimeError(
            "Aucun metagenome commun entre matrix species et matrix function."
        )

    if len(common_ids) < len(selected_ids):
        print(
            f"Warning: {len(common_ids)} metagenomes communs utilises "
            f"(sur {len(selected_ids)} trouves)."
        )

    combined_column_metadata = collect_column_metadata(species_payloads + function_payloads)
    sample_name_map = build_sample_name_map(
        common_ids, combined_column_metadata, record_by_mgid
    )

    allowed_cols = set(common_ids)
    top_species_rows = top_rows_by_total(species_payloads, TOP_SPECIES_FEATURES, allowed_cols)
    top_function_rows = top_rows_by_total(
        function_payloads, TOP_FUNCTION_FEATURES, allowed_cols
    )

    species_written = write_species_csv(
        SPECIES_PATH,
        species_payloads,
        sample_name_map,
        allowed_cols=allowed_cols,
        top_rows=top_species_rows,
    )
    function_written = write_function_csv(
        FUNCTION_PATH,
        function_payloads,
        sample_name_map,
        allowed_cols=allowed_cols,
        top_rows=top_function_rows,
    )

    metadata_rows = build_metadata_rows(common_ids, sample_name_map, record_by_mgid)
    write_metadata_csv(METADATA_PATH, metadata_rows)

    print("Fichiers generes:")
    print(f"- {METADATA_PATH} | rows={count_rows(METADATA_PATH)}")
    print(f"- {SPECIES_PATH} | rows={count_rows(SPECIES_PATH)} | long_rows={species_written}")
    print(f"- {FUNCTION_PATH} | rows={count_rows(FUNCTION_PATH)} | long_rows={function_written}")

    print("Termine. Les fichiers sont conformes au format attendu par le notebook.")


if __name__ == "__main__":
    try:
        main()
    except RequestException as exc:
        print(f"Erreur reseau MG-RAST: {exc}")
        raise SystemExit(1) from exc
    except Exception as exc:
        print(f"Erreur: {exc}")
        raise SystemExit(1) from exc
