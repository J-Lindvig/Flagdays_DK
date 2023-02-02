from __future__ import annotations

import logging
from collections import OrderedDict
from datetime import datetime

from homeassistant.const import ATTR_DATE, ATTR_FRIENDLY_NAME

from .const import (
	CONF_ATTRIBUTE_NAMES,
	CONF_CLIENT,
	CONF_EXCLUDE,
	CONF_FLAGDAYS,
	CONF_INCLUDE,
	CONF_OFFSET,
	CONF_PLATFORM,
	DEFAULT_ATTRIBUTE_NAMES,
	DEFAULT_DATE_FORMAT,
	DEFAULT_OFFSET,
	DOMAIN,
	KEY_NAME,
	KEY_PRIORITY
)
from .flagdays_dk import flagdays_dk

_LOGGER: logging.Logger = logging.getLogger(__package__)
_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
	# Get the configuration
	conf = config.get(DOMAIN)
	# If no config, abort
	if conf is None:
		return True

	# Create a instance of the flagdays_dk
	# Pass the include/exclude list if any, else pass empty list
	flagdays = flagdays_dk(
		include=config[DOMAIN].get(CONF_INCLUDE, []),
		exclude=config[DOMAIN].get(CONF_EXCLUDE, []),
	)

	# Extract attribute names to search for - make it lowercase
	attr_names = set([x.lower() for x in config[DOMAIN].get(CONF_ATTRIBUTE_NAMES, [])])

	# Load a flagday from a sensor
	def flagdayFromSensor(entity):
		# Get the sensor
		flagdayObj = hass.states.get(customFlagday)

		# Create a list of keys from the attribute names which are present in the attributes
		attr_date_keys = list(attr_names.intersection(set(flagdayObj.attributes)))

		# find the first key of type datetime
		attr_date_key = None
		for date_key in attr_date_keys:
			if type(flagdayObj.attributes[date_key]) is datetime:
				attr_date_key = date_key
				break

		# Did we find a key of datetime type
		if attr_date_key:
			return {
				flagdayObj.attributes[ATTR_FRIENDLY_NAME]: {
					ATTR_DATE: flagdayObj.attributes[attr_date_key].strftime(
						DEFAULT_DATE_FORMAT
					)
				}
			}

	# Load a manual flagday
	def flagdayFromConfig(customFlagday):
		flagdayData = dict(customFlagday)
		flagdayData.update({KEY_PRIORITY: priorityCheck(customFlagday)})
		return {customFlagday.pop(KEY_NAME): flagdayData}

	def priorityCheck(payload, priority=0):
		return priority if not KEY_PRIORITY in payload else payload[KEY_PRIORITY]

	# Dict to hold the possible custom flagdays
	customFlagdays = {}
	for customFlagday in config[DOMAIN].get(CONF_FLAGDAYS, []):

		# Sensor or Group of Sensors
		if type(customFlagday) is str:
			domain = customFlagday.split(".", 1)[0]

			# Sensor
			if domain == "sensor":
				customFlagdays.update(flagdayFromSensor(customFlagday))

			# Group of Sensors
			elif domain == "group":
				for customFlagday in hass.states.get(customFlagday).attributes[
					"entity_id"
				]:
					if customFlagday.split(".", 1)[0] == "sensor":
						customFlagdays.update(flagdayFromSensor(customFlagday))

		# Element from YAML
		elif type(customFlagday) is OrderedDict:
			customFlagdays.update(flagdayFromConfig(customFlagday))

	# Add the custom flagdays
	flagdays.add(customFlagdays)

	hass.data[DOMAIN] = {
		CONF_CLIENT: flagdays,
		CONF_OFFSET: config[DOMAIN].get(CONF_OFFSET, DEFAULT_OFFSET),
	}

	# Add sensors
	hass.async_create_task(
		hass.helpers.discovery.async_load_platform(CONF_PLATFORM, DOMAIN, conf, config)
	)

	# Initialization was successful.
	return True
