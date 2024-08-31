from datetime import datetime, timezone
import time
import random


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


def get_today_string():
    return datetime.today().strftime("%Y-%m-%d-%H")


def small_wait():
    time.sleep(random.uniform(0.5, 2.0))
