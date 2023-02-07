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
    KEY_TYPE,
)

DEFAULT_FLAG = "Dannebrog"
DEFAULT_PRIORITY = 10

STRINGS = {
    "CHRISTS_ASCENSION": "Kristi Himmelfartsdag",
    "EASTER_SUNDAY": "Påskedag",
    "GOOD_FRIDAY": "Langfredag",
    "PENTECOST": "Pinsedag",
}
EXCLUDE_TYPE_STRINGS = {
    "MEMORIAL": ["krig"],
    "RELIGIOUS": ["krist", "religiøs", "kirke"],
    "ROYAL": ["kongelige", "majestæt", "højhed", "royale"],
}
HALF_MAST_DAYS = [STRINGS["GOOD_FRIDAY"], "Besættelsesdagen"]

REGULAR_FLAGDAYS = {
    "Nytårsdag": {KEY_DATE: "1-1"},
    "Hendes Kongelige Højhed Kronprinsesse Marys fødselsdag": {
        KEY_DATE: "5-2-1972",
        KEY_TYPE: "ROYAL",
    },
    "Hendes Kongelige Højhed Prinsesse Maries fødselsdag": {
        KEY_DATE: "6-2-1976",
        KEY_TYPE: "ROYAL",
    },
    "Besættelsesdagen": {KEY_DATE: "9-4-1940", KEY_PRIORITY: 20, KEY_TYPE: "MEMORIAL"},
    "Hendes Majestæt Dronningens fødselsdag": {
        KEY_DATE: "16-4-1940",
        KEY_TYPE: "ROYAL",
    },
    "Hendes Kongelige Højhed Prinsesse Benediktes fødselsdag": {
        KEY_DATE: "29-4-1944",
        KEY_TYPE: "ROYAL",
    },
    "Befrielsesdagen": {KEY_DATE: "5-5-1945", KEY_TYPE: "MEMORIAL"},
    "Hans Kongelige Højhed Kronprins Frederiks fødselsdag": {
        KEY_DATE: "26-5-1968",
        KEY_TYPE: "ROYAL",
    },
    "Grundlovsdag": {KEY_DATE: "5-6-1849", KEY_TYPE: "MEMORIAL"},
    "Hans Kongelige Højhed Prins Joachims fødselsdag": {
        KEY_DATE: "7-7-1969",
        KEY_TYPE: "ROYAL",
    },
    "Valdemarsdag og genforeningsdag": {KEY_DATE: "15-6", KEY_TYPE: "MEMORIAL"},
    "Grønlands nationaldag": {KEY_DATE: "21-6", KEY_FLAG: "Erfalasorput"},
    "Færøernes nationale festdag, Olai Dag": {KEY_DATE: "29-7", KEY_FLAG: "Merkið"},
    "Danmarks udsendte": {KEY_DATE: "5-9", KEY_TYPE: "MEMORIAL"},
    "Hans Kongelige Højhed Prins Christians fødselsdag": {
        KEY_DATE: "15-10-2005",
        KEY_TYPE: "ROYAL",
    },
    "Juledag": {KEY_DATE: "25-12"},
}


class flagdays_dk:
    flagdays = []
    days = -1

    def __init__(self, include=[], exclude=[]):

        global REGULAR_FLAGDAYS

        self.in_exclude = {
            CONF_INCLUDE: [DEFAULT_FLAG.lower()] + include,
            CONF_EXCLUDE: exclude,
        }

        e = easter()
        REGULAR_FLAGDAYS[STRINGS["EASTER_SUNDAY"]] = {
            KEY_DATE: e.getEasterSunday(),
            KEY_TYPE: "RELIGIOUS",
        }
        REGULAR_FLAGDAYS[STRINGS["GOOD_FRIDAY"]] = {
            KEY_DATE: e.getGoodFriday(),
            KEY_TYPE: "RELIGIOUS",
        }
        REGULAR_FLAGDAYS[STRINGS["CHRISTS_ASCENSION"]] = {
            KEY_DATE: e.getChristsAscension(),
            KEY_TYPE: "RELIGIOUS",
        }
        REGULAR_FLAGDAYS[STRINGS["PENTECOST"]] = {
            KEY_DATE: e.getPentecost(),
            KEY_TYPE: "RELIGIOUS",
        }

        REGULAR_FLAGDAYS = self._filter()

        self.add(REGULAR_FLAGDAYS)

    def _filter(self, flagdays=REGULAR_FLAGDAYS):
        removeList = set()
        removeTypes = set()

        if not "all" in self.in_exclude[CONF_EXCLUDE]:
            # Loop all the types and their exclude strings
            for exType, exStrings in EXCLUDE_TYPE_STRINGS.items():
                # Loop all the give exclude strings and see if it is
                # present in the joined list of exclusion strings
                if any(
                    excludeStr in "".join(exStrings)
                    for excludeStr in self.in_exclude[CONF_EXCLUDE]
                ):
                    removeTypes.add(exType)

            for flagdayName, flagdayData in flagdays.items():

                # Remove specific types
                if KEY_TYPE in flagdayData and flagdayData[KEY_TYPE] in removeTypes:
                    removeList.add(flagdayName)
                    continue

                # Remove flagdays with special flag, which we have not specified we own
                if KEY_FLAG in flagdayData:
                    if not (
                        flagdayData[KEY_FLAG].lower() in self.in_exclude[CONF_INCLUDE]
                        or any(
                            includeStr in flagdayName.lower()
                            for includeStr in self.in_exclude[CONF_INCLUDE]
                        )
                    ):
                        removeList.add(flagdayName)
                        continue

                # Exclude based on keywords
                if any(
                    excludeStr in flagdayName.lower()
                    for excludeStr in self.in_exclude[CONF_EXCLUDE]
                ):
                    removeList.add(flagdayName)

            # The actual removal
            for flagdayName in removeList:
                del flagdays[flagdayName]

            return flagdays
        return []

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
            if flagdayObj.getDate().date() < today.date():
                # Is it a prolonged flagday and are we still in the period of the flagday?
                # then changed the date of the flagday to todays date.
                dateEnd = flagdayObj.getDateEnd()
                if (
                    type(dateEnd) is datetime
                    and (dateEnd.date() - today.date()).days >= 0
                ):
                    flagdayObj.date = today.date()
                else:
                    self.flagdays.remove(flagdayObj)

        # Update number of days to next flagday
        self.days = (self.flagdays[0].getDate().date() - today.date()).days

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
                # Calculate years passed from the original date and the flagday
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

        if KEY_TYPE in data and data[KEY_TYPE] == "ROYAL":
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
