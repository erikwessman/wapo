from src import helper


def test_get_puzzle_date():
    url = (
        "https://www.washingtonpost.com/crossword-puzzles/daily/?"
        "id=tca231219&set=wapo-daily&puzzleType=crossword&"
        "playId=6d503407-bd5f-4857-a127-3b521c01e58e"
    )
    url_date = helper.get_puzzle_date(url)
    assert url_date == "19-12-2023"


def test_get_puzzle_weekday():
    date_str = "18-12-2023"
    weekday = helper.get_puzzle_weekday(date_str)
    assert weekday == "Monday"

    date_str = "20-12-2023"
    weekday = helper.get_puzzle_weekday(date_str)
    assert weekday == "Wednesday"

    date_str = "22-12-2023"
    weekday = helper.get_puzzle_weekday(date_str)
    assert weekday == "Friday"


def test_puzzle_reward():
    day = "Monday"
    complete_time = 60
    score = helper.get_puzzle_reward(day, complete_time)
    assert score == 5

    day = "Tuesday"
    complete_time = 901
    score = helper.get_puzzle_reward(day, complete_time)
    assert score == 2

    day = "Sunday"
    complete_time = 301
    score = helper.get_puzzle_reward(day, complete_time)
    assert score == 40
