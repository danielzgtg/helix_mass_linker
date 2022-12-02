import json

import requests

import tokens


def post(data: str) -> str:
    json.loads(data)
    res: requests.Response = requests.request(
        method='POST',
        url='https://uottawa.helixalm.cloud/Scripts/ttcgi.exe',
        data=data.encode('utf-8'),
        headers={
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Cookie": tokens.HTTP_COOKIE,
            "DNT": "1",
            "Origin": "https://uottawa.helixalm.cloud",
            "Referer": "https://uottawa.helixalm.cloud/ttweb/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0",
            "X-Requested-With": "XMLHttpRequest",
            "X-SproutCore-Version": "1.9.0.35",
        },
    )
    return res.text
