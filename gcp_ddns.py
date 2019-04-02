#!/usr/bin/env python3
import os
import re
import json
import time
import signal

import yaml
import requests
from google.cloud import dns

config_path = os.environ.get('CONFIG_PATH', 'config/config.yml')
auth_path = os.environ.get('AUTH_PATH', 'config/auth.json')
last_ip_path = os.environ.get('LAST_IP_PATH', 'config/last_ip.txt')
my_ip_url = os.environ.get('MY_IP_URL', 'http://ifconfig.co/ip')

# Exit on SIGTERM
signal.signal(signal.SIGTERM, exit)
# For google.cloud stuff
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = auth_path


class GCPDDNS:
    def __init__(self):
        print('Initializing...')
        self.ip = self.get_stored_ip()
        try:
            self.config = yaml.load(open(config_path), Loader=yaml.Loader)
            self.auth = json.load(open(auth_path))
        except SyntaxError:
            exit()
        # TODO: validate config:
        # zones: list(dict(name: str, TTL: int, records: list(str, ends-with-dot))]
        self.client = dns.Client(project=self.auth['project_id'])

    def run(self):
        interval = self.config.get('interval', 300)
        print('Monitoring IP for change...')
        while True:
            if self.ip_changed():
                self.update_records()
                print('Monitoring IP for change...')
            time.sleep(interval)

    def ip_changed(self):
        r = requests.get(my_ip_url)
        m = re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', r.text)
        ip = m.group(0)
        if ip != self.ip:
            print(f'IP changed from {self.ip} to {ip}')
            self.store_ip(ip)
            return True
        else:
            return False
    
    def get_stored_ip(self):
        print(f'Reading last known IP address from {last_ip_path}...', end='')
        try:
            ip = open(last_ip_path).read()
            print(ip)
            return ip
        except FileNotFoundError:
            print('Not found')
            return
        
    def store_ip(self, ip):
        self.ip = ip
        open(last_ip_path, 'w').write(ip)

    def update_records(self):
        for zone_config in self.config['zones']:
            zone = self.client.zone(zone_config['name'])
            # Load and cache existing records for the zone
            zone.records = list(zone.list_resource_record_sets())
            changes = zone.changes()
            for record in zone_config['records']:
                record_set = zone.resource_record_set(record, 'A', zone_config['TTL'], [self.ip])
                existing_record_set = self.get_matching_record_set(zone, record_set)
                if existing_record_set:
                    changes.delete_record_set(existing_record_set)
                changes.add_record_set(record_set)
            # Make API request
            print(f'Requesting to set IP for zone {zone.name}...', end='')
            changes.create()  # API request
            print('OK')
            print(f'Waiting for confirmation...', end='')
            while changes.status != 'done':
                time.sleep(5)
                changes.reload()  # API request
            print('OK')

    def get_matching_record_set(self, zone, record_set):
        for rs in zone.records:
            if rs.name == record_set.name and rs.record_type == record_set.record_type:
                return rs


if __name__ == '__main__':
    ddns = GCPDDNS()
    ddns.run()

