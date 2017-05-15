import os
import traceback
import subprocess
import time
import utils
import logging
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("dir", type=str, help="the directory to monitor")
parser.add_argument("-v", "--verbose", action="store_true", help="increase output verbosity")

args = parser.parse_args()
logging.info("binsnitch.py started")
utils.prepare_data_files()
print("Loaded " + str(len(utils.cached_db)) + " items from db.json into cache")

try:
    p = subprocess.Popen(['file', '--brief'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, errors = p.communicate()
except FileNotFoundError:
    print('The \"file\" command was not found on the system, which is required for binsnitch.py to run. Exiting.')
    exit()

while True:
    logging.info("Scanning system for new and modified executable files, this can take a long time")

    for dirName, subdirList, fileList in os.walk(args.dir, topdown=False):
        try:
            if args.verbose:
                print('Scanning %s' % dirName)
        except UnicodeEncodeError as e:
            continue

        for filename in fileList:
            full_path = os.path.join(dirName, filename)
            try:
                p = subprocess.Popen(['file', '--brief', full_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, errors = p.communicate()
                file_type = str(output.strip().decode())

                if "exe" in file_type:
                    file_hash = utils.sha256_checksum(full_path)

                    file_info = dict()
                    file_info["path"] = full_path
                    file_info["type"] = file_type
                    file_info["sha256"] = file_hash

                    status = utils.check_file_status(file_info)

                    if status == utils.FILE_UNKNOWN:
                        utils.add_file_to_db(file_info)

                    elif status == utils.FILE_KNOWN_TOUCHED:
                        utils.add_alert_do_db(file_info)

                    elif status == utils.FILE_KNOWN_UNTOUCHED:
                        pass

            except Exception as exc:
                traceback.print_exc()

    logging.info("Finished! Sleeping for a minute before scanning " + args.dir + " for changes again")
    time.sleep(60)

