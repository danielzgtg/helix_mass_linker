import csv
import json


def _filter_ascii(x: str) -> str:
    # return ''.join([y if ord(y) < 128 else '' for y in x])
    x = x[:125]
    for y in x:
        if y != "’" and ord(y) >= 128:
            raise ValueError
    return x


class HelixData:
    def __init__(self, uid: int, subtype: int):
        self.uid: int = uid
        self.subtype: int = subtype

    def __repr__(self):
        return f"HelixData({self.uid}, {self.subtype})"


def _load_helix() -> tuple[dict[str, HelixData], dict[str, HelixData], dict[str, HelixData]]:
    goals: dict[str, HelixData] = {}
    stories: dict[str, HelixData] = {}
    requirements: dict[str, HelixData] = {}

    with open("requirements.json") as f:
        data = json.load(f)

    data = data["rows"]
    for row in data:
        draft_check: bool = False
        target_dict: dict[str, HelixData] | None = None
        summary: str = ""
        uid: int = row["entityID"]
        subtype: int = row["subtypeID"]
        obsolete: bool = False
        if type(uid) is not int:
            raise TypeError
        if type(subtype) is not int:
            raise TypeError
        for col in row["columns"]:
            match col["col"]:
                case 9:
                    if draft_check:
                        raise ValueError
                    match col["val"]:
                        case "Obsolete":
                            obsolete = True
                        case "Draft, not assigned":
                            pass
                        case _:
                            raise ValueError
                    draft_check = True
                case 2:
                    if summary:
                        raise ValueError
                    summary = _filter_ascii(col["val"])
                case 3:
                    if target_dict is not None:
                        raise ValueError
                    match col["val"]:
                        case "Goal":
                            target_dict = goals
                        case "User story":
                            target_dict = stories
                        case _:
                            target_dict = requirements
        if obsolete:
            continue
        if not draft_check:
            raise EOFError
        if target_dict is None:
            raise EOFError
        if not summary:
            raise EOFError
        if summary in target_dict:
            raise ValueError
        target_dict[summary] = HelixData(uid, subtype)

    return goals, stories, requirements


def _join_goals(helix: dict[str, HelixData]) -> dict[str, HelixData]:
    result: dict[str, HelixData] = {}
    with open('Goals.csv') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            result[str(row[0])] = helix[_filter_ascii(row[1])]
    return result


def _join_stories(helix: dict[str, HelixData]) -> dict[str, HelixData]:
    result: dict[str, HelixData] = {}
    with open('Stories.csv') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            result[str(row[0])] = helix[_filter_ascii(row[2])]
    return result


def _join_requirements(
        helix: dict[str, HelixData], stories: dict[str, HelixData], goals: dict[str, HelixData],
) -> list[tuple[HelixData, HelixData, HelixData]]:
    result: list[tuple[HelixData, HelixData, HelixData]] = []
    uid_history: set[int] = set()
    with open('Requirements.csv') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            requirement: HelixData = helix[_filter_ascii(row[5])]
            uid = requirement.uid
            if uid in uid_history:
                raise ValueError
            uid_history.add(uid)
            goal = goals[_filter_ascii(row[1])]
            story = stories[_filter_ascii(row[2])]
            if goal.uid >= uid:
                raise ValueError
            if story.uid >= uid:
                raise ValueError
            result.append((requirement, goal, story))
    return result


def load_expectations() -> list[tuple[HelixData, HelixData, HelixData]]:
    helix_goals, helix_stories, helix_requirements = _load_helix()
    stories = _join_stories(helix_stories)
    goals = _join_goals(helix_goals)
    return _join_requirements(helix_requirements, stories, goals)
