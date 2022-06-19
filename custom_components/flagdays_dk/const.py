CONF_CLIENT = "client"
CONF_FLAGS = "flags"
CONF_FLAGS_DAYS = "flagdays"
CONF_HIDE_PAST = "hide_past"
CONF_TIME_OFFSET = "time_offset"
CONF_PLATFORM = "sensor"
DEFAULT_COORDINATES = {"lat": 55.395903819648304, "lon": 10.388097722778282}
DEFAULT_FLAG = "dannebrog"
DEFAULT_TIME_OFFSET = 10
DOMAIN = "flagdays_dk"
FLAGDAY_URL = "https://www.justitsministeriet.dk/temaer/flagning/flagdage/"
UPDATE_INTERVAL = 60

CREDITS = [
    {"Created by": "J-Lindvig (https://github.com/J-Lindvig)"},
    {"Data provided by": "Justitsministeriet (" + FLAGDAY_URL + ")"},
    {"Sunrise/sunset provided by": "Sunrise-Sunset (https://sunrise-sunset.org/api)"},
]
