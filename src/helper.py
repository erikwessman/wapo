from urllib.parse import urlparse, parse_qs
from datetime import datetime
import validators
import calendar


def get_puzzle_date(url: str) -> str:
    """
    Get the date of the crossword, e.g. "17-12-2023"
    """
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    id_value = query_params["id"][0]
    date_str = id_value.removeprefix("tca")
    return f"{date_str[4:6]}-{date_str[2:4]}-20{date_str[0:2]}"


def get_puzzle_weekday(date_str: str) -> str:
    """
    Get the day of the week for the crossword, e.g. "Monday"
    """
    date_obj = datetime.strptime(date_str, "%d-%m-%y")
    day_of_week = calendar.day_name[date_obj.weekday()]
    return day_of_week


def get_puzzle_reward(day: str, complete_time: int) -> int:
    """
    Calculate the reward for a puzzle
    """
    day_score_table = {
        "Monday": 1,
        "Tuesday": 2,
        "Wednesday": 3,
        "Thursday": 4,
        "Friday": 5,
        "Saturday": 6,
        "Sunday": 10,
    }

    time_multiplier_table = {5 * 60: 5, 7 * 60: 4, 10 * 60: 3, 15 * 60: 2}

    score = day_score_table[day]

    for t in time_multiplier_table:
        if complete_time <= t:
            score *= time_multiplier_table[t]
            break

    return score


def is_message_url(message: str) -> bool:
    """
    Check if a message is a valid URL
    """
    return validators.url(message)
