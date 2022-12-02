#!/usr/bin/env python3
import json
import time
from typing import Any

import tokens
from common import post
from expectations import load_expectations, HelixData


class HelixCache:
    def __init__(self, crawl_delay: int = 3):
        self._cache: dict[int, dict] = {}
        self._crawl_delay: int = crawl_delay

    def _rate_limit(self) -> None:
        time.sleep(self._crawl_delay)

    def fetch(self, x: int) -> dict:
        if x in self._cache:
            return self._cache[x]
        self._rate_limit()
        result = json.loads(post(
            '{"requestType":"GetItemToTrackJson","cookie":"'
            f'{tokens.JSON_COOKIE}'
            '","serverName":"default","symmetricKey":"'
            f'{tokens.JSON_SYMMETRIC_KEY}'
            '","mode":2,"createEditObject":false,"entityType":1920036212,"entityID":'
            f'{x}'
            ',"subtypeID":0,"version":0,"pagingInfo":{},"ownerID":4294967295,'
            '"stepsDisplayMode":2,"includeHistory":true,"localeStr":"en-US"}'
        ))
        if type(result) is not dict:
            raise ValueError
        if result["errorCode"] != 0:
            raise ValueError
        self._cache[x] = result
        return result

    def upload(self, data: str) -> None:
        self._rate_limit()
        result = json.loads(post(data))
        if type(result) is not dict:
            raise ValueError
        if result["errorCode"] != 0:
            raise ValueError


def _is_linked(data: dict, a: int, b: int) -> bool:
    if a >= b:
        raise ValueError
    data = data["item"]
    if "links" not in data:
        return False
    for link in data["links"]:
        link = link["linkedItems"]
        if len(link) != 2:
            print("Ignoring strange link", "".join(map(lambda role: str(role["entityID"]), link)))
            continue
        x: int = link[0]["entityID"]
        y: int = link[1]["entityID"]
        if x > y:
            x, y = y, x
        if x == a and y == b:
            return True
    return False


def _get_summary(cache: HelixCache, requirement: HelixData) -> str:
    data = cache.fetch(requirement.uid)["item"]["fieldValues"]
    summary: str = ""
    subtype_check: bool = False
    status_check: bool = False
    for field in data:
        label: str = field["label"]
        value: Any = field["value"]
        match field["fieldID"]:
            case 9:
                if status_check:
                    raise ValueError
                if label != "Status":
                    raise ValueError
                if value != "Draft, not assigned":
                    raise ValueError
                status_check = True
            case 3:
                if subtype_check:
                    raise ValueError
                if label != "Requirement Type":
                    raise ValueError
                if value != requirement.subtype:
                    raise ValueError
                subtype_check = True
            case 2:
                if summary:
                    raise ValueError
                if label != "Summary":
                    raise ValueError
                if type(value) is not str:
                    raise TypeError
                summary = value
    if not subtype_check:
        raise EOFError
    if not status_check:
        raise EOFError
    if not summary:
        raise EOFError
    if '"' in summary or '\\' in summary:
        raise ValueError
    return summary


def _prepare_one_link_end(cache: HelixCache, x: HelixData) -> str:
    return (
        '"recordID":4294967295,"entityID":'
        f'{x.uid}'
        ',"entityType":1920036212,"subtypeID":'
        f'{x.subtype}'
        ',"summary":"'
        f'{_get_summary(cache, x)}'
        '","status":"Draft","number":'
        f'{x.uid}'
        ',"isSuspect":false,"relationship":3,"relationshipLabel":null,"dateAdded":"","canOpen":null'
    )


def _prepare_link(cache: HelixCache, a: HelixData, b: HelixData) -> str:
    if a.uid >= b.uid:
        raise ValueError
    return (
        '{"requestType":"SaveItemToTrack","cookie":"'
        f'{tokens.JSON_COOKIE}'
        '","serverName":"default","symmetricKey":"'
        f'{tokens.JSON_SYMMETRIC_KEY}'
        '","entityType":1818848875,"entityTypeList":[1920036212],"entityID":4294967295,"eSig":null,"changes":{'
        '"recordID":4294967295,"definitionID":2004,"comment":null,"isBroken":null,"isSuspect":null,"linkedItems":[{'
        f'{_prepare_one_link_end(cache, a)}'
        '},{'
        f'{_prepare_one_link_end(cache, b)}'
        '}]}}'
    )


def _make_link(cache: HelixCache, requirement: HelixData, target: HelixData) -> None:
    data: dict = cache.fetch(target.uid)
    log_detail: str = f"{target.uid} {requirement.uid}"
    if _is_linked(data, target.uid, requirement.uid):
        print("Already linked", log_detail)
        return
    print("Linking", log_detail)
    cache.upload(_prepare_link(cache, target, requirement))
    print("Linked", log_detail)


def _link_requirement(cache: HelixCache, requirement: HelixData, goal: HelixData, story: HelixData) -> None:
    _make_link(cache, requirement, story)
    _make_link(cache, requirement, goal)


def main() -> None:
    cache: HelixCache = HelixCache()
    print("Automated Requirements Linker")
    expectations: list[tuple[HelixData, HelixData, HelixData]] = load_expectations()
    print("I want", expectations)
    for requirement, goal, story in expectations:
        if requirement.uid != 65:
            continue
        _link_requirement(cache, requirement, goal, story)
    print("Done")


if __name__ == '__main__':
    main()
