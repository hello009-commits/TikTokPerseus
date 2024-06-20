# https://rapidapi.com/reverse4free4/api/tiktokperseus4
# Support: https://t.me/reverse4free

import random
import time

import requests

from random             import choices
from device_register    import DeviceRegister
from utils              import printf


if __name__ == "__main__":
    # -------- START ONLY CHANGE HERE -------- #
    # NOTE: If you change country, please also change the domains inside domains.py!
    country = 'pk'
    proxy   = None
    #username    = ""
    #password    = ""
    #token       = ''.join(choices('0123456789abcdefghiklmnopqrstuvwxyz', k=8))
    #proxy       = f'{username}:{password}_country-{country}_session-{token}_lifetime-5m@geo.iproyal.com:12321'
    # -------- END ONLY CHANGE HERE -------- #

    session = requests.Session()
    if proxy:
        session.proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}

    device = DeviceRegister(proxy=proxy, country=country, session=session)

    printf(f'\n==== START GET DEVICE TEMPLATE ====\n')
    device.process_dev_info()
    printf(f'\n==== END GET DEVICE TEMPLATE ====')

    printf(f'\n==== START REGISTER DEVICE ====\n')
    r = device.post_device_register()
    dev_info = device.dev_info
    dev_info["params"]["iid"] = device.install_id
    dev_info["params"]["device_id"] = device.device_id
    if dev_info["params"]["iid"] and dev_info["params"]["device_id"] == 0 or dev_info["params"]["iid"] and dev_info["params"]["device_id"] == '' or dev_info["params"]["iid"] and dev_info["params"]["device_id"] == '0':
        printf('Device not registered')
        raise ('Device not registered')
    printf(f'\n==== END REGISTER DEVICE ====')
    time.sleep(3)

    printf("\n==== START GET SEED ====\n")
    obj = device.get_seed()
    try:
        dev_info["extra"]["seed"] = obj['data']['token']
        dev_info["extra"]["seed_rand"] = obj['data']['algo']
    except:
        printf('No seed')
        raise ('No seed')
    printf("\n==== END GET SEED ====")
    time.sleep(7)

    printf(f"\n==== START RI REPORT ====\n")
    device.post_ri_report(1)
    time.sleep(2)
    device.post_ri_report(2)
    time.sleep(2)
    device.post_ri_report(3)
    printf("\n==== END ri/report ====")
    time.sleep(8)

    printf(f'\n==== START GET SEC DEV ID ====\n')
    token = device.get_token()
    dev_info["extra"]["sec_device_id"] = token
    printf(f'\n==== END GET SEC DEV ID ====')

    printf(f'\n==== START APP ALERT CHECK ====\n')
    device.send_app_alert_check()
    printf(f'\n==== END APP ALERT CHECK ====')
    time.sleep(4)

    printf(f'\n==== START DEVICE TRUST USERS ====\n')
    device.send_device_trust_users()
    printf(f'\n==== END DEVICE TRUST USERS ====')

    printf("\n==== START DEVICE INFO ====\n")
    printf(dev_info)
    printf("\n==== END DEVICE INFO ====")


