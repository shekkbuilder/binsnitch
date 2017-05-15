import hashlib
import json
import logging
import os
import signal
import traceback

logging.basicConfig(format = '%(asctime)s - %(levelname)s - %(message)s',
                    datefmt = '%m/%d/%Y %I:%M:%S %p',
                    filename = 'data/alerts.log',
                    level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())

# Status Constants
FILE_KNOWN_UNTOUCHED = "FILE_KNOWN_UNTOUCHED"
FILE_KNOWN_TOUCHED = "FILE_KNOWN_TOUCHED"
FILE_UNKNOWN = "FILE_UNKNOWN"

cached_db = None


def rscandir(path):
    for entry in os.scandir(path):
        try:
            yield entry
            if entry.is_dir():
                yield from rscandir(entry.path)
        except Exception as exc:
            pass


def shellquote(s):
    return "'" + s.replace("'", "'\\''") + "'"


def sha256_checksum(filename, block_size=65536):
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()


def check_file_status(file_info):
    global cached_db

    known_path = False

    for db_file in cached_db:
        if db_file["path"] == file_info["path"]:
            known_path = True

            if file_info["sha256"] in db_file["sha256"]:
                return FILE_KNOWN_UNTOUCHED
            else:
                return FILE_KNOWN_TOUCHED

    if not known_path:
        return FILE_UNKNOWN


def add_alert_do_db(file_info):
    global cached_db

    with open('data/db.json') as data_file:
        db_data = json.load(data_file)

    for db_file in db_data:
        if db_file["path"] == file_info["path"]:
            db_file["sha256"].append(file_info["sha256"])
            logging.info("Modified binary detected:" + db_file["path"] + " - new hash: " + file_info["sha256"])

    cached_db = db_data
    write_to_db(cached_db)


def write_to_db(db_data):
    s = signal.signal(signal.SIGINT, signal.SIG_IGN)
    json.dump(db_data, open("data/db.json", 'w'), sort_keys=False, indent=4, separators=(',', ': '))
    signal.signal(signal.SIGINT, s)


def add_file_to_db(file_info):
    global cached_db

    with open('data/db.json') as data_file:
        db_data = json.load(data_file)

    file_info_to_add = {"path": file_info["path"], "type": file_info["type"], "sha256": [file_info["sha256"]]}

    db_data.append(file_info_to_add)
    cached_db = db_data
    write_to_db(cached_db)


def refresh_cache():
    global cached_db
    try:
        file = open("data/db.json", 'r')
        cached_db = json.load(file)
    except Exception as exc:
        traceback.print_exc()


def prepare_data_files():
    global cached_db

    try:
        file = open("data/db.json", 'r')
    except IOError:
        json.dump([], open("data/db.json", 'w'))

    try:
        file = open("data/alerts.log", 'r')
    except IOError:
        open("data/alerts.log", 'a').close()

    refresh_cache()
