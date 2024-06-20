from hashlib import md5

from domains import DOMAIN_NORMAL
from request_params import *
from api import *


def tt_common_post_request(session, dev_info, account_info, host, url, cookie_string=None, body=None, extra=None):
    """
    :param session:
    :param dev_info:
    :param account_info:
    :param host:
    :param url:
    :param cookie_string:
    :param body:
    :return:
    """
    url_params = generate_url_common_params(dev_info, extra if extra else None)
    query_str = f"{host}{url}?{url_params}"

    timestamp_ms = round(time.time() * 1000)
    x_ladon, x_argus, x_gorgon, x_khronos, x_ss_stub = do_sign_v5(dev_info, int(timestamp_ms / 1000), query_str, body=body)
    headers = {
        'host': DOMAIN_NORMAL.split('/')[2],
        'connection': 'keep-alive',
        'accept': 'application/json',
        'x-tt-dm-status': 'login=0;ct=0;rt=7',
        'x-tt-request-tag': 't=0;n=1',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'aid': '1233',
        'user-agent': dev_info['extra']['user_agent'],
        'x-vc-bdturing-sdk-version': '2.3.7',
        'sdk-version': '2',
        'passport-sdk-version': '5.12.1',
        'x-ss-stub': md5(body.encode('utf-8')).hexdigest().upper(),
        'x-tt-app-init-region': dev_info['geo']['app_init_region'],
        'x-ss-dp': dev_info['app']['aid'],
        'accept-encoding': 'gzip, deflate, br',
        'cookie': cookie_string,
        'x-khronos': x_khronos,
        'x-gorgon': x_gorgon,
        "x-argus": x_argus,
        "x-ladon": x_ladon
    }

    print(query_str)
    if account_info is not None:
        headers |= {
            'x-tt-token': account_info["x-tt-token"],
            'x-tt-cmpl-token': account_info["cookies"]["cmpl_token"],
            'x-bd-client-key': account_info["x-bd-client-key"],
            'x-bd-kmsv': account_info["x-bd-kmsv"],
        }
        response = post_request(session, query_str, headers, post_body=body, cookies=account_info["cookies"])
    else:
        headers |= {
            "x-tt-dm-status": "login=0;ct=1;rt=6",
        }
        response = post_request(session, query_str, headers, post_body=body)
    print(response.content)
    return response


def tt_common_get_request(session, dev_info, account_info, host, url, extra={}):
    """

    :param session:
    :param dev_info:
    :param account_info:
    :param host:
    :param url:
    :param extra:
    :return:
    """
    url_params = generate_url_common_params(dev_info, extra)
    query_str = f"{host}{url}?{url_params}"

    timestamp_ms = round(time.time() * 1000)
    x_ladon, x_argus, x_gorgon, x_khronos, x_ss_stub = do_sign_v5(dev_info, int(timestamp_ms / 1000), query_str)
    headers = {
        'host': DOMAIN_NORMAL.split('/')[2],
        'connection': 'keep-alive',
        'accept': 'application/json',
        'x-tt-dm-status': 'login=0;ct=0;rt=7',
        'x-tt-request-tag': 't=0;n=1',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'aid': dev_info['app']['aid'],
        'user-agent': dev_info['extra']['user_agent'],
        'x-vc-bdturing-sdk-version': '2.3.7',
        'sdk-version': '2',
        'passport-sdk-version': '5.12.1',
        'x-tt-app-init-region': dev_info['geo']['app_init_region'],
        'x-ss-dp': '1233',
        'accept-encoding': 'gzip, deflate, br',
        'cookie': cookie_string,
        'x-khronos': x_khronos,
        'x-gorgon': x_gorgon,
        "x-argus": x_argus,
        "x-ladon": x_ladon
    }

    print(query_str)
    if account_info is not None:
        headers |= {
            'x-tt-token': account_info["x-tt-token"],
            'x-tt-cmpl-token': account_info["cookies"]["cmpl_token"],
            'x-bd-client-key': account_info["x-bd-client-key"],
            'x-bd-kmsv': account_info["x-bd-kmsv"],
        }
        response = get_request(session, query_str, headers, cookies=account_info["cookies"])
    else:
        headers |= {
            "x-tt-dm-status": "login=0;ct=1;rt=6",
        }
        response = get_request(session, query_str, headers)
    print(response.content)
    return response
