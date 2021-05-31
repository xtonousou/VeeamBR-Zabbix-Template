#! /usr/bin/env python3
# Author: Sotirios Roussis - sroussis@space.gr

import json
import os
import sys
import time

import dotenv
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

dotenv.load_dotenv()
VEEAM_USERNAME = os.getenv('VEEAM_USERNAME')
VEEAM_PASSWORD = os.getenv('VEEAM_PASSWORD')
VEEAM_HOST = os.getenv('VEEAM_HOST')
VEEAM_API_VERSION = os.getenv('VEEAM_API_VERSION')
VEEAM_CACHE_FILE = os.getenv('VEEAM_CACHE_FILE')


class Veeam(object):

    def __init__(self):
        self.url = 'https://{0}:9419'.format(VEEAM_HOST)
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-api-version': VEEAM_API_VERSION,
        }
        self.error_codes_map = {
            401: 'ERROR: Unauthorized. The authorization header has been expected but not found (or found but is expired).',
            403: 'ERROR: Forbidden. The user sending the request does not have adequate privileges to access one or more objects specified in the request.',
            500: 'ERROR: Internal server error. The request has been received but could not be completed because of an internal error at the server side.',
        }

    def auth(self):
        if not os.path.exists(VEEAM_CACHE_FILE):
            return False

        lock_file = VEEAM_CACHE_FILE + '.lock'
        while True:
            if not os.path.exists(lock_file):
                break
            time.sleep(0.5)

        with open(lock_file, 'w') as f:
            f.write('{"msg": "Locked by Python reader."}')

        with open(VEEAM_CACHE_FILE, 'r') as f:
            tokens = json.load(f)
            self.headers['Authorization'] = 'Bearer {0}'.format(tokens.get('access_token'))
            del tokens

        os.remove(lock_file)
        return True

    def jobs(self, specific=False):
        params = {
            'limit': 65534,
        }
        r = requests.get(self.url + '/api/v1/jobs/states', headers=self.headers, params=params, verify=False)
        if not r.ok:
            if r.status_code in self.error_codes_map:
                print(self.error_codes_map[r.status_code])
            return 4

        response = r.json().get('data')
        if not response:
            return 5
        
        zabbix_data = []
        for i in response:
            if specific and specific.strip().lower() == i['name'].strip().lower():
                zabbix_data = {
                    'name': i['name'],
                    'object_count': i['objectsCount'],
                    'last_result': i['lastResult'],
                    'status': i['status'],
                    'type': i['type'],
                }
                break
            elif not specific:
                zabbix_data.append({
                    '{#JOB_NAME}': i['name'],
                })

        print(json.dumps(zabbix_data))
        return 0

    def repositories(self, specific=False):
        params = {
            'limit': 65534,
        }
        r = requests.get(self.url + '/api/v1/backupInfrastructure/repositories/states', headers=self.headers, params=params, verify=False)
        if not r.ok:
            if r.status_code in self.error_codes_map:
                print(self.error_codes_map[r.status_code])
            return 4

        response = r.json().get('data')
        if not response:
            return 5
        
        zabbix_data = []
        for i in response:
            if specific and specific.strip().lower() == i['name'].strip().lower():
                zabbix_data = {
                    'name': i['name'],
                    'type': i['type'],
                    'path': i['path'],
                    'space_total': round(float(i['capacityGB']) * 1024 * 1024 * 1024),
                    'space_free': round(float(i['freeGB']) * 1024 * 1024 * 1024),
                }
                break
            elif not specific:
                zabbix_data.append({
                    '{#REPO_NAME}': i['name'],
                })

        print(json.dumps(zabbix_data))
        return 0


class Zabbix(object):

    def __init__(self):
        self.veeam = Veeam()
        self.arg_map = {
            'jobs': self.veeam.jobs,
            'repositories': self.veeam.repositories,
        }

    def main(self):
        if len(sys.argv) == 1:
            available_functions = list(self.arg_map.keys())
            print('No functions specified. Choose one of the below:\n\n{0}\n\n'.format(available_functions))
            print('For example: {0} {1}'.format(sys.argv[0], available_functions[0]))
            return 1

        func = self.arg_map.get(sys.argv[1])
        if not func:
            print('ERROR: The specified function "{0}" does not exist. Run the script without arguments to see all the available functions.'.format(sys.argv[1]))
            return 2

        if not self.veeam.auth():
            print('ERROR: Veeam cache file does not exist yet. Please make sure that the credential-manager.sh is running.')
            return 3

        if len(sys.argv) > 2:
            return func(specific=sys.argv[2])

        return func()


if __name__ == '__main__':
    sys.exit(Zabbix().main())

