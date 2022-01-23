from __future__ import annotations

import logging
import requests                     # Perform http/https requests
from bs4 import BeautifulSoup as BS # Parse HTML pages
import json                         # Needed to print JSON API data
from datetime import datetime
from .sun_future import SunFuture

from .const import (
	DOMAIN,
	EVENT_DATE_FORMAT,
	FLAGDAY_URL,
	HEADERS,
	HALF_MAST_DAYS,
	HALF_MAST_ALL_DAY_STR,
	MONTHS_DK,
	FLAGS,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)
_LOGGER = logging.getLogger(__name__)

class flagdays_dk_api:
	def __init__(self, custom_events = None, flags = None, coordinates = {'lat':55.2292263507843,'lon':10.249203443527222}):
		self._custom_events = custom_events
		self._flags = flags
		self._sun = None
		self._now = datetime.now()
		self._coordinates = coordinates
		self._session = None
		self._year = None
		self._next_event = {}
		self._events = []

		_LOGGER.debug("[flags] : " + str(self._flags))

	def getFlagdays(self):
		# It the events are empty, fetch data from the site
		if not self._events:
			self._session = requests.Session()
			self._sun = SunFuture()
			r = self._session.get(FLAGDAY_URL, headers = HEADERS)
			html = BS(r.text, "html.parser")
	
			# Extract current year from the site
			self._year = html.find_all('h2')[0].text.split()[-1]

			# Find all <td>
			td = html.find_all('td')
			for i in range(self._getNumOfTag(r.text, 'td')):
				add = True
				if not (i % 2):
					flagDay = {}

					# Get a "nice" date string, ex.  5. februar
					flagDay['date_str'] = td[i].text.strip()

					# Extract date and month from the site
					# Lookup the month and return the number og the month
					# Append the date, month and year
					date, month = flagDay['date_str'].split('.')
					flagDay['date'] = date + '-' + str(self._getMonthNo(month)) + '-' + self._year

					# Get the time of the sunrise and sunset and calculate the up and down time of the flag
					# Append it to the dictionary
					flagDay.update(self._getFlagTimes(self._year + "-" + str(self._getMonthNo(month)) + "-" + date))

					# Create a Date object from the date of the event
					dateObj = datetime.strptime(flagDay['date'] + " " + flagDay['flag_up_time'], EVENT_DATE_FORMAT)

					# Calculate the timestamp of the event
					flagDay['timestamp'] = int(dateObj.timestamp())
					# Calculate days to the event
					flagDay['days_to_event'] = (dateObj - self._now).days + 1
				else:
					# Extract the line with the event.
					# Split special events by the "."
					# In case of multiple "." only split the first
					eventLine = td[i].text.split('.', 1)

					# Get the name of the event
					flagDay['event_name'] = eventLine[0].strip()

					# Special event have special orders regarding the flag
					flagDay['half_mast'] = flagDay['event_name'].lower() in HALF_MAST_DAYS
					flagDay['half_mast_all_day'] = HALF_MAST_ALL_DAY_STR in eventLine[-1].lower()

					# Find the flag if it is special
					for key in FLAGS:

						# Is the flag a special flag
						# and do we have it
						# else it must be Dannebrog
						if key in eventLine[-1].lower():
							add = key in self._flags
							flagDay['flag'] = FLAGS[key]
						else:
							flagDay['flag'] = 'Dannebrog'

					if add:
						self._events.append(flagDay)
	
			# Loop through the given events from the configuration.yaml
			for event in self._custom_events:
				self._events.append(self._getCustomEvent(event))
	
			# Sort the events
			self._events = sorted(self._events, key=lambda d: d['timestamp']) 

		# Find the firstcoming event
		self._next_event = self._getNextEvent()

	def _getFlagTimes(self, dateStr):
		flagTimes = {}

		self._sun.getFutureSun(
			self._coordinates['lat'],
			self._coordinates['lon'],
			dateStr
			)

		# If sunrise is before 08:00 use 08:00 else sunrise
		flagTimes['flag_up_time'] = '08:00' if int(self._sun.get('sunrise').split(':')[0]) < 8 else self._sun.get('sunrise')
		flagTimes['flag_down_time'] = self._sun.get('sunset')

		return flagTimes

	def _getNumOfTag(self, html, tag, parser = 'html.parser'):
		soup = BS(html, parser)
		return len(soup.find_all(tag))

	def _getMonthName(self, monthNo):
		return MONTHS_DK[int(monthNo) - 1]

	def _getMonthNo(self, monthName):
		monthName = monthName.lower().strip()
		if monthName in MONTHS_DK:
			return MONTHS_DK.index(monthName) + 1
		else:
			return 0

	def _getCustomEvent(self, event):
		flagDay = {}

		# Split the given string into date, month and year
		date, month, year = event['date'].split('-')
		# Create a nice date string
		flagDay['date_str'] = f'{ date }. { self._getMonthName(month) }'
		# Add the times for up nd down
		flagDay.update(self._getFlagTimes(self._year + "-" + month + "-" + date))
		# Create a date
		flagDay['date'] = str(int(date)) + '-' + str(int(month)) + '-' + self._year

		# Create a Date object from the event
		dateObj = datetime.strptime(flagDay['date'] + " " + flagDay['flag_up_time'], EVENT_DATE_FORMAT)

		# Calculate the timestamp
		flagDay['timestamp'] = int(dateObj.timestamp())
		# Calculate the days to the event
		flagDay['days_to event'] = (dateObj - self._now).days + 1

		# Extract the name of the event
		flagDay['event_name'] = event['name']
		flagDay['half_mast'] = False
		flagDay['half_mast_all_day'] = False
		flagDay['flag'] = 'Dannebrog'

		return flagDay

	def _getNextEvent(self):
		# Find the next upcoming event
		now_ts = int(self._now.timestamp())
		for event in self._events:
			if event['timestamp'] > now_ts:
				return event