import base64
import binascii
import json
import time

from hashlib        import md5
from urllib.parse   import urlencode
from api            import do_get_dev_tmpl, get_device_register_body, do_sign_v5, encrypt_get_token, decrypt_get_token, encrypt_get_seed, decrypt_get_seed, encrypt_get_report
from domains        import DOMAIN_APPLOG, DOMAIN_MSSDK, DOMAIN_NORMAL
from request_params import generate_url_common_params
from utils          import post_request, get_request, printf, cookie_string, cookie_json, trace_id


class DeviceRegister:
    """
    Device register
    """

    def __init__(self, session, country, proxy: str = None):
        self.session = session
        self.proxy = proxy
        self.device_id = ""
        self.install_id = ""
        self.dev_info = None
        self.country = country

    def process_dev_info(self):
        self.dev_info = do_get_dev_tmpl(self.proxy, self.country)
        printf(f'Device info: {self.dev_info}')

        return self.dev_info

    def post_device_register(self):
        """
        Send device register request
        """
        host = DOMAIN_APPLOG
        url = "/service/2/device_register/"
        extra = {
            'device_id': [
                '',
                '',
            ],
            'is_activated': '0',
            'aid': [
                '1233',
                '1233',
            ],
            'tt_data': 'a'
        }

        query_args_str = generate_url_common_params(self.dev_info, extra=extra)
        req_url = f"{DOMAIN_APPLOG}{url}?{query_args_str}"

        body = base64.b64decode(get_device_register_body(self.dev_info)).decode('utf-8')
        printf(f'Device register body hex: {body}')

        timestamp_ms = round(time.time() * 1000)
        timestamp = timestamp_ms // 1000

        x_ladon, x_argus, x_gorgon, x_khronos, x_ss_stub = do_sign_v5(timestamp=timestamp, req_url=req_url,
                                                                      dev_info=self.dev_info, body=bytes.fromhex(body))

        headers = {
            'accept': 'application/json',
            'aid': str(self.dev_info['app']['aid']),
            'connection': 'keep-alive',
            'content-type': 'application/octet-stream;tt-data=a',
            'host': DOMAIN_APPLOG.split('/')[2],
            'passport-sdk-version': '5.12.1',
            'sdk-version': '2',
            'user-agent': self.dev_info['extra']['user_agent'],
            'x-ss-dp': str(self.dev_info['app']['aid']),
            'x-tt-app-init-region': self.dev_info['geo']['app_init_region'],
            'x-tt-dm-status': 'login=0;ct=1;rt=6',
            'x-tt-request-tag': 't=0;n=0',
            'x-tt-trace-id': trace_id(self.dev_info['app']['aid']),
            'x-vc-bdturing-sdk-version': '2.3.7',
            'x-khronos': x_khronos,
            'x-gorgon': x_gorgon,
            "x-argus": x_argus,
            "x-ladon": x_ladon
        }
        response = post_request(self.session, req_url, headers, bytes.fromhex(body))
        obj = json.loads(response.text)
        self.device_id = str(obj["device_id"])
        self.install_id = str(obj["install_id"])
        printf(f"device_id_str: {self.device_id}")
        printf(f"install_id_str: {self.install_id}")

        time.sleep(2)
        if not response.cookies:
            pass
        else:
            cookies_dict = cookie_json(response)
            self.dev_info['extra']['cookies'] = cookie_string(json.loads(json.dumps(cookies_dict, indent=4)))

        return response

    def send_app_alert_check(self):
        """
        Send app alert check
        """
        host = DOMAIN_APPLOG
        url = "/service/2/app_alert_check/"

        query_args_str = urlencode({
            'mcc_mnc': self.dev_info['geo']['mcc_mnc'].__str__(),
            'app_name': 'musical_ly',
            'channel': 'App Store',
            'device_platform': 'iphone',
            'idfa': self.dev_info['params']['idfa'],
            'vid': self.dev_info['extra']['vid'],
            'device_token': self.dev_info['extra']['device_token'],
            'is_upgrade_user': '0',
            'version_code': self.dev_info['app']['app_version'],
            'ac': 'WIFI',
            'timezone': self.dev_info['geo']['timezone'],
            'os_version': self.dev_info['params']['os_version'],
            'aid': self.dev_info['app']['aid'].__str__(),
            'is_activated': '0',
            "cronet_version": '4a87e515_2024-04-01',
            "ttnet_version": '4.2.137.41-tiktok',
            'use_store_region_cookie': '1',
        })
        req_url = f"{host}{url}?{query_args_str}"

        timestamp_ms = round(time.time() * 1000)
        timestamp = timestamp_ms // 1000

        headers = {
            'Host': DOMAIN_APPLOG.split('/')[2],
            'X-Tt-Dm-Status': 'login=0;ct=0;rt=7',
            'X-Tt-Request-Tag': 't=0;n=1;s=0',
            'X-Vc-Bdturing-Sdk-Version': '2.3.7',
            'Tt-Request-Time': round(time.time()).__str__(),
            'User-Agent': self.dev_info['extra']['user_agent'],
            'Sdk-Version': '2',
            'Passport-Sdk-Version': '5.12.1',
            'X-Tt-App-Init-Region': self.dev_info['geo']['app_init_region'],
            'X-Ss-Dp': self.dev_info['app']['aid'].__str__(),
            'X-Tt-Trace-Id': trace_id(self.dev_info['app']['aid'])
        }

        response = get_request(self.session, req_url, headers)
        obj = json.loads(response.text)
        if not response.cookies:
            pass
        else:
            cookies_dict = cookie_json(response)
            self.dev_info['extra']['cookies'] = json.loads(json.dumps(cookies_dict, indent=4))
        printf(str(obj))

        time.sleep(2)

    def send_device_trust_users(self):
        """
        Send device trust users
        """
        host = DOMAIN_NORMAL
        url = "/passport/device/trust_users/"

        query_args_str = generate_url_common_params(self.dev_info)
        req_url = f"{host}{url}?{query_args_str}"

        timestamp_ms = round(time.time() * 1000)
        timestamp = timestamp_ms // 1000

        body = "last_sec_user_id=&d_ticket=&last_login_way=-1&last_login_time=0&last_login_platform="

        x_ladon, x_argus, x_gorgon, x_khronos, x_ss_stub = do_sign_v5(timestamp=timestamp, req_url=req_url,
                                                                      dev_info=self.dev_info, body=body)
        headers = {
            'host': DOMAIN_NORMAL.split('/')[2],
            'connection': 'keep-alive',
            'accept': 'application/json',
            "x-tt-dm-status": "login=1;ct=1;rt=1",
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'aid': self.dev_info['app']['aid'].__str__(),
            'user-agent': self.dev_info['extra']['user_agent'],
            'x-vc-bdturing-sdk-version': self.dev_info['app']['aid'].__str__(),
            'sdk-version': '2',
            'passport-sdk-version': '5.12.1',
            'x-ss-stub': md5(body.encode('utf-8')).hexdigest().upper(),
            'x-tt-app-init-region': self.dev_info['geo']['app_init_region'],
            'x-ss-dp': self.dev_info['app']['aid'].__str__(),
            'accept-encoding': 'gzip, deflate, br',
            'x-khronos': x_khronos,
            'x-gorgon': x_gorgon,
            "x-argus": x_argus,
            "x-ladon": x_ladon
        }

        response = post_request(self.session, req_url, headers, post_body=body)
        if not response.cookies:
            pass
        else:
            cookies_dict = cookie_json(response)
            print(f'Cookie: {json.loads(json.dumps(cookies_dict, indent=4))}')
        obj = json.loads(response.text)
        printf(str(obj))

    def get_token(self):
        """
        MSSDK send get_token get sec_did_token
        """
        timestamp_ms = round(time.time() * 1000)
        timestamp = timestamp_ms // 1000

        host = DOMAIN_MSSDK
        url = "/sdi/get_token"

        query_args = urlencode({
            'lc_id': self.dev_info['app']['mssdk']['license_id'],
            'platform': self.dev_info['params']['os'],
            'device_platform': self.dev_info['params']['os'].lower(),
            'sdk_ver': self.dev_info['app']['mssdk']['sdk_version'],
            'sdk_ver_code': self.dev_info['app']['mssdk']['sdk_version_code'],
            'app_ver': self.dev_info['app']['app_version'],
            'version_code': self.dev_info['app']['version_code'],
            'aid': self.dev_info['app']['aid'],
            'sdkid': '',
            'subaid': '',
            'iid': self.dev_info['params']['iid'],
            'did': self.dev_info['params']['device_id'],
            'bd_did': '',
            'client_type': 'inhouse',
            'region_type': 'ov',
            'mode': 2
        })
        query_args_str = query_args
        req_url = f"{host}{url}?{query_args_str}"
        body = encrypt_get_token(self.dev_info)
        x_ladon, x_argus, x_gorgon, x_khronos, x_ss_stub = do_sign_v5(dev_info=self.dev_info,
                                                                      timestamp=timestamp,
                                                                      req_url=req_url,
                                                                      body=body)
        header = {
            'accept': '*/*',
            'connection': 'Keep-Alive',
            'content-type': 'application/octet-stream',
            'host': DOMAIN_MSSDK.split('/')[2],
            'passport-sdk-version': '5.12.1',
            'sdk-version': '2',
            'sdk_aid': '3019',
            'user-agent': self.dev_info['extra']['user_agent'],
            'x-ss-dp': '1233',
            'x-tt-dm-status': 'login=0;ct=1;rt=6',
            'x-tt-request-tag': 't=0;n=1;s=0',
            'x-tt-store-region': self.dev_info['geo']['account_region'],
            'x-tt-store-region-src': 'did',
            'x-tt-trace-id':  trace_id(self.dev_info['app']['aid'], self.dev_info['params']['device_id']),
            'x-vc-bdturing-sdk-version': '2.3.7',
            "x-ss-stub": x_ss_stub,
            'x-khronos': x_khronos,
            'x-gorgon': x_gorgon,
            "x-argus": x_argus,
            "x-ladon": x_ladon
        }
        resp = post_request(self.session, req_url, header, post_body=body)
        ret = decrypt_get_token(self.dev_info["params"]["os"].lower(), self.dev_info["app"]["aid"],
                                binascii.hexlify(resp.content).decode('utf-8'))
        if not resp.cookies:
            pass
        else:
            cookies_dict = cookie_json(resp)
            self.dev_info['extra']['cookies'] = cookie_string(json.loads(json.dumps(cookies_dict, indent=4)))
        printf(ret)
        try:
            time.sleep(2)
            return ret["token"]
        except:
            raise ('No token')

    def get_seed(self):
        """
        MSSDK send get_seed get seed
        """
        timestamp_ms = round(time.time() * 1000)
        timestamp = timestamp_ms // 1000

        host = DOMAIN_MSSDK
        url = "/ms/get_seed"

        query_args = urlencode({
            'lc_id': self.dev_info['app']['mssdk']['license_id'],
            'platform': self.dev_info['params']['os'],
            'device_platform': self.dev_info['params']['os'].lower(),
            'sdk_ver': self.dev_info['app']['mssdk']['sdk_version'],
            'sdk_ver_code': self.dev_info['app']['mssdk']['sdk_version_code'],
            'app_ver': self.dev_info['app']['app_version'],
            'version_code': self.dev_info['app']['version_code'],
            'aid': self.dev_info['app']['aid'],
            'sdkid': '',
            'subaid': '',
            'iid': self.dev_info['params']['iid'],
            'did': self.dev_info['params']['device_id'],
            'bd_did': '',
            'client_type': 'inhouse',
            'region_type': 'ov',
            'mode': 2
        })
        query_args_str = query_args
        req_url = f"{host}{url}?{query_args_str}"
        body = encrypt_get_seed(self.dev_info)
        x_ladon, x_argus, x_gorgon, x_khronos, x_ss_stub = do_sign_v5(dev_info=self.dev_info,
                                                                      timestamp=timestamp,
                                                                      req_url=req_url,
                                                                      body=body)
        header = {
            'accept': '*/*',
            'connection': 'Keep-Alive',
            'content-type': 'application/octet-stream',
            'host': DOMAIN_MSSDK.split('/')[2],
            'passport-sdk-version': '5.12.1',
            'sdk-version': '2',
            'sdk_aid': '3019',
            'user-agent': self.dev_info['extra']['user_agent'],
            'x-ss-dp': '1233',
            'x-tt-dm-status': 'login=0;ct=1;rt=6',
            'x-tt-request-tag': 't=0;n=1;s=0',
            'x-tt-store-region': self.dev_info['geo']['account_region'],
            'x-tt-store-region-src': 'did',
            'x-tt-trace-id': trace_id(self.dev_info['app']['aid'], self.dev_info['params']['device_id']),
            'x-vc-bdturing-sdk-version': '2.3.7',
            "x-ss-stub": x_ss_stub,
            'x-khronos': x_khronos,
            'x-gorgon': x_gorgon,
            "x-argus": x_argus,
            "x-ladon": x_ladon
        }
        resp = post_request(self.session, req_url, header, post_body=body)
        printf(binascii.hexlify(resp.content).decode('utf-8'))
        ret = decrypt_get_seed(self.dev_info["params"]["os"].lower(), self.dev_info["app"]["aid"],
                               binascii.hexlify(resp.content).decode('utf-8'))
        if not resp.cookies:
            pass
        else:
            cookies_dict = cookie_json(resp)
            self.dev_info['extra']['cookies'] = cookie_string(json.loads(json.dumps(cookies_dict, indent=4)))
        printf(ret)
        time.sleep(1)
        return ret

    def post_ri_report(self, mode, account_info=None):
        """
        MSSDK send risk report
        """
        timestamp_ms = round(time.time() * 1000)
        timestamp = timestamp_ms // 1000

        host = DOMAIN_MSSDK
        url = "/ri/report"

        query_args = urlencode({
            'lc_id': self.dev_info['app']['mssdk']['license_id'],
            'platform': self.dev_info['params']['os'],
            'device_platform': self.dev_info['params']['os'].lower(),
            'sdk_ver': self.dev_info['app']['mssdk']['sdk_version'],
            'sdk_ver_code': self.dev_info['app']['mssdk']['sdk_version_code'],
            'app_ver': self.dev_info['app']['app_version'],
            'version_code': self.dev_info['app']['version_code'],
            'aid': self.dev_info['app']['aid'],
            'sdkid': '',
            'subaid': '',
            'iid': self.dev_info['params']['iid'],
            'did': self.dev_info['params']['device_id'],
            'bd_did': '',
            'client_type': 'inhouse',
            'region_type': 'ov',
            'mode': 2
        })
        query_args_str = query_args
        req_url = f"{host}{url}?{query_args_str}"
        body = encrypt_get_token(self.dev_info)
        x_ladon, x_argus, x_gorgon, x_khronos, x_ss_stub = do_sign_v5(dev_info=self.dev_info,
                                                                      timestamp=timestamp,
                                                                      req_url=req_url,
                                                                      body=body)
        header = {
            'accept': '*/*',
            'connection': 'Keep-Alive',
            'content-type': 'application/octet-stream',
            'host': DOMAIN_MSSDK.split('/')[2],
            'passport-sdk-version': '5.12.1',
            'sdk-version': '2',
            'sdk_aid': '3019',
            'user-agent': self.dev_info['extra']['user_agent'],
            'x-ss-dp': '1233',
            'x-tt-dm-status': 'login=0;ct=1;rt=6',
            'x-tt-request-tag': 't=0;n=1;s=0',
            'x-tt-store-region': self.dev_info['geo']['account_region'],
            'x-tt-store-region-src': 'did',
            'x-tt-trace-id': trace_id(self.dev_info['app']['aid'], self.dev_info['params']['device_id']),
            'x-vc-bdturing-sdk-version': '2.3.7',
            "x-ss-stub": x_ss_stub,
            'x-khronos': x_khronos,
            'x-gorgon': x_gorgon,
            "x-argus": x_argus,
            "x-ladon": x_ladon
        }
        if account_info is not None:
            header |= {
                'x-tt-token': account_info["x-tt-token"],
                'x-tt-cmpl-token': account_info["cookies"]["cmpl_token"],
            }
            resp = post_request(self.session, req_url, header, post_body=body, cookies=account_info["cookies"])
        else:
            resp = post_request(self.session, req_url, header, post_body=body)
        if not resp.cookies:
            pass
        else:
            cookies_dict = cookie_json(resp)
            self.dev_info['extra']['cookies'] = cookie_string(json.loads(json.dumps(cookies_dict, indent=4)))
        printf(resp)

        time.sleep(2)
