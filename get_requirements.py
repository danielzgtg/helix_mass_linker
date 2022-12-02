#!/usr/bin/env python3
import tokens
from common import post


def main() -> None:
    result: str = post(
        '{"requestType":"GetRecordList","cookie":"'
        f'{tokens.JSON_COOKIE}'
        '","serverName":"default","symmetricKey":"'
        f'{tokens.JSON_SYMMETRIC_KEY}'
        '","entityType":1920036212,"fromIndex":1,"getAvailableColumns":true,'
        '"getDisplayColumns":true,"forceCachedListRefresh":true,"tabID":0,"filterID":0}'
    )
    with open("requirements.json", "w") as f:
        f.write(result)


if __name__ == '__main__':
    main()
