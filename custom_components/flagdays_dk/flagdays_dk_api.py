from __future__ import annotations

import logging
import requests

from bs4 import BeautifulSoup as BS
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from .sun_future import SunFuture

from .const import (
    DEFAULT_FLAG,
    FLAGDAY_URL,
)

COMMONWEALTH_FLAGS = {
    "grønland": "erfalasorput",
    "færø": "merkið",
}
DK_DATE_FORMAT = "%d-%m-%Y"
HALF_MAST_DAYS = ["besættelsesdagen", "langfredag"]
HALF_MAST_ALL_DAY_STR = "hele dagen"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Platform; Security; OS-or-CPU; Localization; rv:1.4) Gecko/20030624 Netscape/7.1 (ax)"
}
MONTHS_DK = [
    "januar",
    "februar",
    "marts",
    "april",
    "maj",
    "juni",
    "juli",
    "august",
    "september",
    "oktober",
    "november",
    "december",
]

_LOGGER: logging.Logger = logging.getLogger(__package__)
_LOGGER = logging.getLogger(__name__)


class flagDays_DK:
    def __init__(
        self, flags, coordinates, timeOffset, privateFlagDays=[], hidePast=True
    ):
        self._flagDays = []
        self._privateFlagDays = privateFlagDays
        self._hidePast = hidePast
        self._flags = flags
        self._coordinates = coordinates
        self._timeOffset = timeOffset
        self._year = None
        self._todayObj = datetime.now()
        self._todayTS = int(
            datetime.strptime(
                (datetime.strftime(self._todayObj, "%Y-%d-%m 00:00")), "%Y-%d-%m %H:%M"
            ).timestamp()
        )
        self._session = requests.Session()

    def update(self):
        self._flagDays.extend(self._getOfficialFlagDays())
        self._flagDays.extend(self._getPrivateFlagDays())
        self._flagDays.sort(key=lambda x: x._daysToFlagDay)

    def _getPrivateFlagDays(self):
        _LOGGER.debug("Processing private flagdays...")
        privateFlagDays = []
        for privateFlagDay in self._privateFlagDays:
            aFlagDay = flagDay()

            aFlagDay.setFlag()
            if "flag" in privateFlagDay:
                aFlagDay.setFlag(privateFlagDay["flag"])

            aFlagDay.setName(privateFlagDay["name"])

            dateList = privateFlagDay["date"].split("-")
            if len(dateList) > 2:
                d1 = datetime.strptime(privateFlagDay["date"], DK_DATE_FORMAT)
                d2 = datetime.strptime(
                    "-".join([dateList[0], dateList[1], self._year]),
                    DK_DATE_FORMAT,
                )
                name = (
                    aFlagDay.getName()
                    + " ("
                    + str(relativedelta(d2, d1).years)
                    + " år)"
                )
                aFlagDay.setName(name)
                dateList[2] = self._year
            else:
                dateList.append(self._year)

            # If we have provided a date_end, check if we have stated year - else add it
            # Create ad dateobject from the enddate and startdate
            # If today is in range between start and end, use todays date
            if "date_end" in privateFlagDay:
                endDateList = privateFlagDay["date_end"].split("-")
                if len(endDateList) < 3:
                    endDateList.append(self._year)
                endDateObj = datetime.strptime(
                    "-".join(endDateList), DK_DATE_FORMAT
                ) + timedelta(days=1)
                startDateObj = datetime.strptime("-".join(dateList), DK_DATE_FORMAT)

                if startDateObj <= self._todayObj <= endDateObj:
                    dateList = datetime.strftime(self._todayObj, DK_DATE_FORMAT).split(
                        "-"
                    )

            aFlagDay.setPrivateDate(dateList)

            aFlagDay.setTime(self._coordinates, self._timeOffset)

            privateFlagDays.append(aFlagDay)

        return privateFlagDays

    def _getOfficialFlagDays(self):
        _LOGGER.debug("Processing official flagdays...")
        aFlagDays = []
        r = self._session.get(FLAGDAY_URL, headers=HEADERS)

        _LOGGER.debug(f"{ FLAGDAY_URL}: {r.status_code}")
        if r.status_code != 200:
            return r.status_code

        html = BS(r.text, "html.parser")
        # Find the first <h2>, split it by whitespaces and return the last element.
        self._year = html.find("h2").text.split()[-1]

        # Loop through all the <tr> (rows)
        for row in html.find_all("tr"):
            addFlagDay = True

            aFlagDay = flagDay()

            # Find all the <td> (cells)
            cells = row.findAll("td")

            # Find cell with the name of the flagday and possible special instructions
            # Split it only by the first "."
            flagDayText = cells[1].text.split(".", 1)

            # Use the defaulf flag or find a custom flag.
            # If we do not own the custom flag, continue with the next flagday
            aFlagDay.setFlag()
            for country, flag in COMMONWEALTH_FLAGS.items():
                if country in flagDayText[-1].lower():
                    addFlagDay = flag in self._flags
                    if addFlagDay:
                        aFlagDay.setFlag(flag)
                        self._flags.remove(flag)
                    break
            if not addFlagDay:
                continue

            # Extract the name of the flagday + instructions if present
            aFlagDay.setName(flagDayText[0].strip())
            if len(flagDayText) > 1:
                aFlagDay.setInstructions(flagDayText[1].strip())

            # Set the dates etc.
            aFlagDay.setDate(cells[0].text.strip(), self._year)

            aFlagDay.setTime(self._coordinates, self._timeOffset)

            if addFlagDay:
                aFlagDays.append(aFlagDay)

        return aFlagDays

    def getNextFlagDay(self):
        for flagDay in self._flagDays:
            if flagDay.getTimestamp() >= self._todayTS:
                return flagDay

    def getFutureFlagDays(self):
        if self._hidePast:
            futureFlagDays = []
            for flagDay in self._flagDays:
                if flagDay.getTimestamp() >= self._todayTS:
                    futureFlagDays.append(flagDay)
            return futureFlagDays
        else:
            return self._flagDays


class flagDay:
    def __init__(self):
        self._name = ""
        self._instructions = {
            "halfMast": False,
            "halfMastAllDay": False,
            "halfMastEndTime": "12:00",
        }
        self._flag = ""
        self._daysToFlagDay = 0
        self._dateTable = {
            "dateStr": "",
            "year": "",
            "monthName": "",
            "monthNo": "",
            "date": "",
        }
        self._timeTable = {
            "sunrise": "",
            "flagUpTime": "",
            "flagUpTimestamp": 0,
            "flagDownTime": "",
            "flagUpTriggerTime": "",
            "flagDownTriggerTime": "",
        }

    def setName(self, name):
        self._name = name

    def setInstructions(self, instructions):
        self._instructions["halfMast"] = any(
            halfMast in self._name.lower() for halfMast in HALF_MAST_DAYS
        )
        if self._instructions["halfMast"]:
            self._instructions["halfMastAllDay"] = (
                HALF_MAST_ALL_DAY_STR in instructions.lower()
            )

    def setFlag(self, flag=DEFAULT_FLAG):
        self._flag = flag.title()

    def setDate(self, dateStr, year):
        self._dateTable["year"] = year
        # Extract date and monthName
        # Find the number of the month (monthNo)
        self._dateTable["date"], self._dateTable["monthName"] = dateStr.split(".")
        self._dateTable["monthNo"] = self._getMonthNo(self._dateTable["monthName"])
        self._dateTable["dateStr"] = "-".join(
            [
                self._dateTable["date"],
                self._dateTable["monthNo"],
                self._dateTable["year"],
            ]
        )

    def setPrivateDate(self, dateList):
        self._dateTable["year"] = dateList[-1]
        self._dateTable["date"] = dateList[0]
        self._dateTable["monthNo"] = str(dateList[1]).lstrip("0")
        self._dateTable["monthName"] = MONTHS_DK[int(self._dateTable["monthNo"]) - 1]
        self._dateTable["dateStr"] = "-".join(
            [
                self._dateTable["date"],
                self._dateTable["monthNo"],
                self._dateTable["year"],
            ]
        )

    def setTime(self, coordinates, timeOffset=0):
        # Prepare a Y-M-D Date String
        dateStr = "-".join(
            [
                self._dateTable["year"],
                self._dateTable["monthNo"],
                self._dateTable["date"],
            ]
        )
        # Get the Sunrise/Sunset from the online API
        self._timeTable["sunDateTimes"] = SunFuture(
            dateStr, coordinates
        ).getSunDatetimes()

        # Sunrise
        self._timeTable["sunrise"] = self._timeTable["sunDateTimes"][
            "sunrise"
        ].strftime("%H:%M")

        # FlagUpTime, if before 08:00, set it to 08:00 else sunrise
        self._timeTable["flagUpTime"] = (
            "08:00"
            if int(self._timeTable["sunDateTimes"]["sunrise"].strftime("%-H")) < 8
            else self._timeTable["sunrise"]
        )

        dateObj = datetime.strptime(
            dateStr + " " + self._timeTable["flagUpTime"], "%Y-%m-%d %H:%M"
        )
        # FlagUpTimestamp
        self._timeTable["flagUpTimestamp"] = int(dateObj.timestamp())

        # FlagDownTime is sunset
        self._timeTable["flagDownTime"] = self._timeTable["sunDateTimes"][
            "sunset"
        ].strftime("%H:%M")

        # Remove ["sunDateTimes"]
        self._timeTable.pop("sunDateTimes")

        # FlagUpTriggerTime is FlagUpTime - offset
        self._timeTable["flagUpTriggerTime"] = (
            datetime.strptime(self._timeTable["flagUpTime"], "%H:%M")
            - timedelta(minutes=timeOffset)
        ).strftime("%H:%M")

        # FlagDownTriggerTime is FlagDownTime - offset
        self._timeTable["flagDownTriggerTime"] = (
            datetime.strptime(self._timeTable["flagDownTime"], "%H:%M")
            - timedelta(minutes=timeOffset)
        ).strftime("%H:%M")

        # Calculate days to the event
        self._daysToFlagDay = (dateObj - datetime.now()).days + 1

    def getName(self):
        return self._name

    def getInstructions(self):
        return self._instructions

    def getDateStr(self):
        return self._dateTable["dateStr"]

    def getDays(self):
        return self._daysToFlagDay

    def getFlag(self):
        return self._flag

    def getTimeTable(self):
        return self._timeTable

    def getTimestamp(self):
        return self._timeTable["flagUpTimestamp"]

    def _getMonthNo(self, monthName, returnAsString=True):
        monthName = monthName.lower().strip()
        if monthName in MONTHS_DK:
            monthNo = MONTHS_DK.index(monthName) + 1
            if returnAsString:
                return str(monthNo)
            else:
                return monthNo
        else:
            return 0
