from urllib.parse import urlparse, parse_qs
from datetime import datetime
import calendar
import validators
import discord

from const import GITHUB_REPOSITORY, GITHUB_ICON, DAY_SCORE_TABLE, TIME_MULTIPLIER_TABLE


def calculate_new_average_price(
    initial_shares, initial_avg_price, additional_shares, purchase_price
):
    total_cost_initial = initial_shares * initial_avg_price
    total_cost_additional = additional_shares * purchase_price
    new_total_cost = total_cost_initial + total_cost_additional
    new_total_shares = initial_shares + additional_shares
    new_average_price = new_total_cost / new_total_shares
    return new_average_price


def get_embed(
    title: str, description: str, color: discord.Color, url: str = None
) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=color, url=url)
    embed.set_footer(text=GITHUB_REPOSITORY, icon_url=GITHUB_ICON)
    return embed


def get_puzzle_date(url: str) -> str:
    """
    Extracts the date of the crossword puzzle from its URL.

    Parameters:
    - url (str): The URL of the crossword puzzle.

    Returns:
    - str: The date of the crossword in the format "DD-MM-YYYY".
    """
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    puzzle_id = query_params["id"][0]
    date_str = puzzle_id.removeprefix("tca")
    return f"{date_str[4:6]}-{date_str[2:4]}-20{date_str[0:2]}"


def get_puzzle_weekday(date_str: str) -> str:
    """
    Determines the day of the week for a given date string.

    Parameters:
    - date_str (str): The date of the crossword puzzle in the format "DD-MM-YYYY".

    Returns:
    - str: The name of the weekday corresponding to the given date.
    """
    date_obj = datetime.strptime(date_str, "%d-%m-%Y")
    day_of_week = calendar.day_name[date_obj.weekday()]
    return day_of_week


def get_puzzle_reward(day: str, complete_time: int) -> int:
    """
    Calculates the reward score for completing a crossword puzzle based on the day and completion time.

    Parameters:
    - day (str): The day of the week when the crossword puzzle was completed.
    - complete_time (int): The time taken to complete the puzzle in seconds.

    Returns:
    - int: The calculated reward score.
    """

    score = DAY_SCORE_TABLE[day]

    for time_s, multiplier in TIME_MULTIPLIER_TABLE.items():
        if complete_time <= time_s:
            score *= multiplier
            break

    return score


def is_message_url(message: str) -> bool:
    """
    Determines whether a given message string is a valid URL.

    Parameters:
    - message (str): The message string to be validated.

    Returns:
    - bool: True if the message is a valid URL, False otherwise.
    """
    return validators.url(message)
