CONF_CLIENT = 'client'
CONF_PLATFORM = 'sensor'
DEFAULT_COORDINATES = {
	'lat' : 55.395903819648304,
	'lon' : 10.388097722778282
}
DEFAULT_FLAG = 'Dannebrog'
DOMAIN = 'flagdays_dk'
EVENT_DATE_FORMAT = '%d-%m-%Y %H:%M'
FLAGS = {
	'danmark': 'Dannebrog',
	'grønland': 'Erfalasorput',
	'færø': 'Merkið',
	'pride': 'Regnbueflaget'
}
FLAGDAY_URL = 'https://www.justitsministeriet.dk/temaer/flagning/flagdage/'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Platform; Security; OS-or-CPU; Localization; rv:1.4) Gecko/20030624 Netscape/7.1 (ax)'}
HALF_MAST_DAYS = ['besættelsesdagen', 'langfredag']
HALF_MAST_ALL_DAY_STR = 'hele dagen'
MONTHS_DK = ['januar', 'februar', 'marts', 'april', 'maj', 'juni', 'juli', 'august', 'september', 'oktober', 'november', 'december']
SUN_URL = 'https://api.sunrise-sunset.org/json'
UPDATE_INTERVAL = 60
UTC_FORMAT = '%Y-%m-%dT%H:%M:%S%z'

CREDITS = [
	{ 'Created by': 'J-Lindvig (https://github.com/J-Lindvig)' },
	{ 'Data provided by': 'Justitsministeriet (' + FLAGDAY_URL + ')' },
	{ 'Sunrise/sunset provided by': 'Sunrise-Sunset (https://sunrise-sunset.org/api)' }
]