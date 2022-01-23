from __future__ import annotations

import logging
import requests                 # Perform http/https requests
from bs4 import BeautifulSoup   # Parse HTML pages
import json                     # Needed to print JSON API data
import datetime as DT

from .const import (
	SUN_URL,
	UTC_FORMAT,
)

_LOGGER = logging.getLogger(__name__)

class SunFuture:
	def __init__(self):
		self._session = None
		self._data = {}

	def getFutureSun(self, lat = 55.395903819648304, lon = 10.388097722778282, dateStr = 'today'):
		self._session = requests.Session()
		payload = {
			'lat': lat,
			'lng': lon,
			'date': dateStr,
			'formatted': 0
		}
		r = self._session.get(SUN_URL, params = payload)

		if r.status_code == 200:
			r = r.json()
			if r['status'].lower() == 'ok':
				for key in r['results']:
					value = r['results'][key]
					if key.lower() != 'day_length':
						value = self._getLocalDatetime(value)
					self._data[key] = value
			self._data['date'] = self._getLocalDatetime(r['results']['sunrise'], '%d-%m-%Y')

	def get(self, key):
		return self._data[key]

	def _getLocalDatetime(self, dateStr, dateFormat = '%H:%M'):
		ts = DT.datetime.strptime(dateStr, UTC_FORMAT).timestamp()
		return DT.datetime.strftime(DT.datetime.fromtimestamp(ts), dateFormat)