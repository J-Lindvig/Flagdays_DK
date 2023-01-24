from __future__ import annotations

from .easter import easter
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

_LOGGER: logging.Logger = logging.getLogger(__package__)
_LOGGER = logging.getLogger(__name__)

from .const import (
    CONF_EXCLUDE,
    CONF_INCLUDE,
    DEFAULT_DATE_FORMAT,
    KEY_DATE,
    KEY_DATE_END,
    KEY_FLAG,
    KEY_PRIORITY,
)

DEFAULT_FLAG = "Dannebrog"
DEFAULT_PRIORITY = 10

STRINGS = {
    "CHRISTS_ASCENSION": "Kristi Himmelfartsdag",
    "EASTER_SUNDAY": "Påskedag",
    "GOOD_FRIDAY": "Langfredag",
    "PENTECOST": "Pinsedag",
    "ROYAL": ["Kongelige", "Majestæt"],
}
HALF_MAST_DAYS = [STRINGS["GOOD_FRIDAY"], "Besættelsesdagen"]

REGULAR_FLAGDAYS = {
    "Nytårsdag": {KEY_DATE: "1-1"},
    "Hendes Kongelige Højhed Kronprinsesse Marys fødselsdag": {KEY_DATE: "5-2-1972"},
    "Hendes Kongelige Højhed Prinsesse Maries fødselsdag": {KEY_DATE: "6-2-1976"},
    "Besættelsesdagen": {KEY_DATE: "9-4-1940", KEY_PRIORITY: 20},
    "Hendes Majestæt Dronningens fødselsdag": {KEY_DATE: "16-4-1940"},
    "Hendes Kongelige Højhed Prinsesse Benediktes fødselsdag": {KEY_DATE: "29-4-1944"},
    "Befrielsesdagen": {KEY_DATE: "5-5-1945"},
    "Hans Kongelige Højhed Kronprins Frederiks fødselsdag": {KEY_DATE: "26-5-1968"},
    "Grundlovsdag": {KEY_DATE: "5-6-1849"},
    "Hans Kongelige Højhed Prins Joachims fødselsdag": {KEY_DATE: "7-7-1969"},
    "Valdemarsdag og genforeningsdag": {KEY_DATE: "15-6"},
    "Grønlands nationaldag": {KEY_DATE: "21-6", KEY_FLAG: "Erfalasorput"},
    "Færøernes nationale festdag, Olai Dag": {KEY_DATE: "29-7", KEY_FLAG: "Merkið"},
    "Danmarks udsendte": {KEY_DATE: "5-9"},
    "Hans Kongelige Højhed Prins Christians fødselsdag": {KEY_DATE: "15-10-2005"},
    "Juledag": {KEY_DATE: "25-12"},
}


class flagdays_dk:
    flagdays = []
    days = -1

    def __init__(self, include=[], exclude=[]):

        self.in_exclude = {
            CONF_INCLUDE: [DEFAULT_FLAG.lower()]
            + list(map(lambda x: x.lower(), include)),
            CONF_EXCLUDE: list(map(lambda x: x.lower(), exclude)),
        }

        e = easter()
        REGULAR_FLAGDAYS[STRINGS["EASTER_SUNDAY"]] = {KEY_DATE: e.getEasterSunday()}
        REGULAR_FLAGDAYS[STRINGS["GOOD_FRIDAY"]] = {KEY_DATE: e.getGoodFriday()}
        REGULAR_FLAGDAYS[STRINGS["CHRISTS_ASCENSION"]] = {
            KEY_DATE: e.getChristsAscension()
        }
        REGULAR_FLAGDAYS[STRINGS["PENTECOST"]] = {KEY_DATE: e.getPentecost()}

        self._filter()

        self.add(REGULAR_FLAGDAYS)

    def _filter(self):
        removeList = set()
        for flagdayName, flagdayData in REGULAR_FLAGDAYS.items():

            # Inclusion by removal of flagdays which doesn't meet our list of include
            # Does the flagday have a special flag?
            if KEY_FLAG in flagdayData:
                # Is the flag in our list of inclusion OR
                # Does the name of the flagday containing our inclusion string
                # If so - reverse the boolean
                if not (
                    flagdayData[KEY_FLAG].lower() in self.in_exclude[CONF_INCLUDE]
                    or any(
                        includeStr in flagdayName.lower()
                        for includeStr in self.in_exclude[CONF_INCLUDE]
                    )
                ):
                    removeList.add(flagdayName)

            # Exlude by removal of matching flagdays
            if any(
                excludeStr in flagdayName.lower()
                for excludeStr in self.in_exclude[CONF_EXCLUDE]
            ):
                removeList.add(flagdayName)

        # The actual removal
        for flagdayName in removeList:
            REGULAR_FLAGDAYS.pop(flagdayName)

    def add(self, flagdays):
        if type(flagdays) is dict:
            for flagdayName, flagdayData in flagdays.items():
                self.flagdays.append(flagday(name=flagdayName, data=flagdayData))

            self.sort()

    def sort(self):
        self.flagdays.sort(
            key=lambda flagdayObj: (flagdayObj.date, flagdayObj.priority)
        )
        self.update()

    def update(self):
        today = datetime.today()
        for flagdayObj in self.flagdays:

            # Update the dates and remove old flagdays
            if relativedelta(flagdayObj.getDate(), today).days < 0:

                # Is it a prolonged flagday and are we still in the period of the flagday?
                # then changed the date of the flagday to todays date.
                dateEnd = flagdayObj.getDateEnd()
                if (
                    type(dateEnd) is datetime
                    and relativedelta(dateEnd, today).days >= 0
                ):
                    flagdayObj.date = today.date()
                else:
                    self.flagdays.remove(flagdayObj)

        # Update number of days to next flagday
        self.days = relativedelta(
            self.flagdays[0].getDate(), datetime.today().date()
        ).days

    def getFutureFlagdays(self):
        return self.flagdays[1:]

    def getConcurrentFlagdays(self, date):
        # Loop from 2nd element, searching for flagdays with the same date
        # Return list of flagdaynames.
        return list(
            (flagday.getName())
            for flagday in self.flagdays[1:]
            if flagday.getDate() == date
        )


class flagday:
    name = None
    flag = None
    years = None
    dateEnd = None
    halfMast = False

    def __init__(self, name=str, data=dict):
        self.name = name

        # Date of flagday
        if type(data[KEY_DATE]) is str:
            if data[KEY_DATE].count("-") > 1:
                # Strip the year from the datestring, append current year and convert to datetime
                self.date = datetime.strptime(
                    data[KEY_DATE].rpartition("-")[0]
                    + "-"
                    + str(datetime.today().year),
                    DEFAULT_DATE_FORMAT,
                )
                self.years = relativedelta(
                    self.date, datetime.strptime(data[KEY_DATE], "%d-%m-%Y")
                ).years
            else:
                self.date = datetime.strptime(
                    data[KEY_DATE] + "-" + str(datetime.today().year),
                    DEFAULT_DATE_FORMAT,
                )
        else:
            self.date = data[KEY_DATE]

        # End of prolonged flagday
        if KEY_DATE_END in data:
            self.dateEnd = datetime.strptime(
                data[KEY_DATE_END] + "-" + str(datetime.today().year),
                DEFAULT_DATE_FORMAT,
            )

        # Halfmast
        if self.name in HALF_MAST_DAYS:
            self.halfMast = (
                True
                if self.name == STRINGS["GOOD_FRIDAY"]
                else datetime.combine(
                    self.date, datetime.strptime("12:00", "%H:%M").time()
                )
            )

        if name in STRINGS["ROYAL"]:
            self.priority = 30

        self.priority = data[KEY_PRIORITY] if KEY_PRIORITY in data else DEFAULT_PRIORITY

        self.flag = data[KEY_FLAG] if KEY_FLAG in data else DEFAULT_FLAG

    def getDate(self, dateFormat=None):
        if dateFormat is None:
            return self.date
        return self.date.strftime(dateFormat)

    def getDateEnd(self, dateFormat=None):
        if dateFormat is None:
            return self.dateEnd
        elif type(self.dateEnd) is datetime:
            return self.dateEnd.strftime(dateFormat)

    def getHalfMast(self, timeFormat="%H:%M"):
        return self.halfMast
