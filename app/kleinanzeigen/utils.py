from datetime import datetime
import pytz

def parse_date_str(date_str: str) -> datetime:
    berlin_tz = pytz.timezone("Europe/Berlin")
    dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f%z")
    dt_berlin = dt.astimezone(berlin_tz)
    return dt_berlin

def write_date_str(date: datetime) -> str:
    berlin_tz = pytz.timezone("Europe/Berlin")
    date_berlin = date.astimezone(berlin_tz)
    return date_berlin.strftime("%Y-%m-%d %H:%M:%S")
