from urllib.parse import urlparse, parse_qs
from datetime import datetime
import calendar


def get_day_of_week(url: str) -> str:
    """
    """
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    id_value = query_params['id'][0]
    date_str = id_value.removeprefix('tca')

    date_obj = datetime.strptime(date_str, "%y%m%d")
    day_of_week = calendar.day_name[date_obj.weekday()]
    return day_of_week
