from __future__ import annotations

import logging
import requests

from datetime import datetime
from dateutil import tz

from .const import (
    DEFAULT_COORDINATES,
)

SUN_URL = "http://api.sunrise-sunset.org/json"
UTC_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

_LOGGER: logging.Logger = logging.getLogger(__package__)
_LOGGER = logging.getLogger(__name__)


class SunFuture:
    def __init__(self, dateStr="today", coordinates=DEFAULT_COORDINATES):
        self._sunData = {"sunrise": None, "sunset": None}
        self._session = requests.Session()
        payload = {
            "lat": coordinates["lat"],
            "lng": coordinates["lon"],
            "date": dateStr,
            "formatted": 0,
        }
        _LOGGER.debug(f"Fetching sunrise/sunset on { dateStr }")
        r = self._session.get(SUN_URL, params=payload)

        _LOGGER.debug(f"{ SUN_URL }: { r.status_code }")
        if r.status_code == 200:
            r = r.json()
            if r["status"].lower() == "ok":
                for key in self._sunData.keys():
                    self._sunData[key] = self._getLocalDatetime(r["results"][key])

    def getSunDatetimes(self):
        return self._sunData

    def _getLocalDatetime(self, dateStr):
        return (
            datetime.strptime(dateStr, UTC_FORMAT)
            .replace(tzinfo=tz.gettz("UTC"))
            .astimezone(tz.gettz("Europe/Copenhagen"))
        )
