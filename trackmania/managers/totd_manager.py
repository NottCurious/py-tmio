import json
from contextlib import suppress
from datetime import date, datetime
from typing import Dict, List

import redis

from trackmania.structures.map import TOTD

from ..api import APIClient
from ..config import Client
from ..constants import TMIO
from ..util import map_parsers


async def _latest_totd(leaderboard_flag: bool = False) -> TOTD:
    """
    Fetches the current TOTD map.

    Parameters
    ----------
    leaderboard_flag : bool, optional
        Whether to add the top 100 leaderboard to the data. If set to `True`, makes another api request. defaults to `False`

    Returns
    -------
    :class:`TOTD`
        The :class:`TOTD` Object.
    """
    cache_client = redis.Redis(host=Client.REDIS_HOST, port=Client.REDIS_PORT)

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        if cache_client.exists("latest_totd"):
            latest_totd = json.loads(cache_client.get("latest_totd"))
            return map_parsers.parse_totd_map(latest_totd, latest_totd["leaderboard"])

    api_client = APIClient()
    latest_totd = await api_client.get(TMIO.build([TMIO.TABS.TOTD, "0"]))
    latest_totd: dict = latest_totd["days"][-1]

    if leaderboard_flag:
        raw_lb_data = await api_client.get(
            TMIO.build(
                [TMIO.TABS.LEADERBOARD, TMIO.TABS.MAP, latest_totd["map"]["mapUid"]]
            )
            + "?offset=0&length=100"
        )
        leaderboard = raw_lb_data["tops"]
    else:
        leaderboard = None

    await api_client.close()

    latest_totd.update({"leaderboard": leaderboard})

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        hour, minute = datetime.utcnow().hour, datetime.utcnow().minute
        if not ((hour > 17 and minute > 0) and (hour < 18 and minute < 0)):
            cache_client.set(name="latest_totd", value=json.dumps(latest_totd), ex=3600)

    return map_parsers.parse_totd_map(latest_totd, leaderboard)


async def totd(
    date: date | int = -1, month: bool = False, leaderboard_flag: bool = False
) -> TOTD | List[Dict]:
    """
    Gets the TOTD of a specific date.

    Parameters
    ----------
    date : `date` | int, optional
        The date of the TOTD. If it is -1 it returns the latest totd. defaults to -1
    month : bool, optional
        If to return all totds of a given month. defaults to `False`
    leaderboard_flag : bool, optional
        Whether to add the top 100 leaderboard to the data. If set to `True`, makes another api request. defaults to `False`

    Returns
    -------
    `TOTD` | `List`[`Dict`]
        The `TOTD` Object or a list of TOTD maps.

    Raises
    ------
    ValueError
        Year must be in [2020, 2021, 2022]
    ValueError
        TM2020 Released on July 1st.
    """

    if isinstance(date, int):
        if date == -1:
            return await _latest_totd(leaderboard_flag)
        else:
            raise ValueError("date must be a datetime object or -1")

    # Date Checks
    today_date = datetime.utcnow()

    if date.year not in (2020, 2021, 2022):
        raise ValueError("Year must be 2020, 2021 or 2022")
    if date.year == 2020 and date.month < 7:
        raise ValueError("TM2020 Released on July 1st.")
    if (
        (
            date.year == today_date.year
            and date.month == today_date.month
            and date.day > today_date.day
        )
        or (date.year > today_date.year)
        or (date.year == today_date.year and date.month > today_date.month)
    ):
        raise ValueError("Date cannot be in the future")

    cache_client = redis.Redis(host=Client.REDIS_HOST, port=Client.REDIS_PORT)

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        if date.day == -1 and cache_client.exists(f"totd|{date.year}|{date.month}|-1"):
            return json.loads(cache_client.get(f"totd|{date.year}|{date.month}|-1"))

        if cache_client.exists(f"totd|{date.year}|{date.month}|{date.day}"):
            totd = cache_client.get(f"totd|{date.year}|{date.month}|{date.day}")
            return map_parsers.parse_totd_map(json.loads(totd, totd["leaderboard"]))

    # Find how many months ago the given month is.
    count = 0

    if date.year == 2020:
        count = (12 - date.month) + 12 + today_date.month
    elif date.year == 2021:
        count = (12 - date.month) + today_date.month
    else:
        count = today_date.month - date.month

    api_client = APIClient()
    month_data = await api_client.get(TMIO.build([TMIO.TABS.TOTD, str(count)]))

    if date.day == -1:
        with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
            cache_client.set(
                f"totd|{date.year}|{date.month}|-1",
                json.dumps(month_data),
                ex=None if count != 0 else 14400,
            )
        return month_data["days"]

    if leaderboard_flag:
        raw_lb_data = await api_client.get(
            TMIO.build(
                [
                    TMIO.TABS.LEADERBOARD,
                    TMIO.TABS.MAP,
                    month_data["days"][date.day - 1]["map"]["mapUid"],
                ]
            )
            + "?offset=0&length=100"
        )
        leaderboard = raw_lb_data["tops"]
    else:
        leaderboard = None
    await api_client.close()

    month_data["days"][date.day - 1].update({"leaderboard": leaderboard})

    with suppress(ConnectionRefusedError, redis.exceptions.ConnectionError):
        cache_client.set(
            f"totd|{date.year}|{month}|{date.day}",
            json.dumps(month_data["days"][date.day - 1]),
            ex=None if count != 0 else 14400,
        )
    return map_parsers.parse_totd_map(month_data["days"][date.day - 1], leaderboard)
