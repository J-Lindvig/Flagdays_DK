from datetime import datetime, timedelta
import math


class easter:
    def __init__(self, year=int(datetime.today().year)):

        self._holidays = {}

        # https://www.experimentarium.dk/faenomener/saadan-falder-paasken-hvert-aar/
        a = year % 19
        b = year % 4
        c = year % 7
        k = year // 100
        p = math.floor((13 + 8 * k) / 25)
        q = k / 4
        M = (15 - p + k - q) % 30
        N = (4 + k - q) % 7
        d = (19 * a + M) % 30
        e = (2 * b + 4 * c + 6 * d + N) % 7

        month = 3 if 22 + d + e <= 31 else 4
        day = int(22 + d + e if month == 3 else d + e - 9)
        if d == 29 and e == 6:
            month = 4
            if a > 10:
                day = 18
            else:
                day = 19

        self._holidays["easterSunday"] = datetime.strptime(
            f"{day}-{month}-{year}", "%d-%m-%Y"
        )
        self._holidays["goodFriday"] = self._holidays["easterSunday"] - timedelta(
            days=2
        )
        self._holidays["christsAscension"] = self._holidays["easterSunday"] + timedelta(
            days=-3, weeks=6
        )
        self._holidays["pentecost"] = self._holidays["easterSunday"] + timedelta(
            weeks=7
        )

    def getGoodFriday(self):
        return self._holidays["goodFriday"]

    def getEasterSunday(self):
        return self._holidays["easterSunday"]

    def getChristsAscension(self):
        return self._holidays["christsAscension"]

    def getPentecost(self):
        return self._holidays["pentecost"]

    def getAllHolidays(self):
        return self._holidays
