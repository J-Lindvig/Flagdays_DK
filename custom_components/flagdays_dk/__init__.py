from __future__ import annotations

import logging

from .flagdays import flagdays_dk_api
from homeassistant.const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
    )
from .const import (
	DOMAIN,
	CONF_CLIENT,
	CONF_PLATFORM,
	)

_LOGGER: logging.Logger = logging.getLogger(__package__)
_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
	conf = config.get(DOMAIN)
	if conf is None:
		return True

	# Get the coordinates from the HA config
	coordinates = {}
	coordinates['lat'] = config.get(CONF_LATITUDE, hass.config.latitude)
	coordinates['lon'] = config.get(CONF_LONGITUDE, hass.config.longitude)

	# Get custom events and the flags in inventory from the config
	events = config[DOMAIN].get('events', {})
	flags = config[DOMAIN].get('flags', {})

	# Initialize the Client
	client  = flagdays_dk_api(events, flags, coordinates)
	hass.data[DOMAIN] = {
		CONF_CLIENT: client,
	}

	# Add sensors
	hass.async_create_task(
		hass.helpers.discovery.async_load_platform(CONF_PLATFORM, DOMAIN, conf, config)
	)

	# Initialization was successful.
	return True