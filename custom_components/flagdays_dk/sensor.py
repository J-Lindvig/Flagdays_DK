from __future__ import annotations

import logging

from .const import (
	ATTRIBUTION,
	CREDITS,
	DOMAIN,
	CONF_CLIENT,
	CONF_PLATFORM,
	ICON,
	UPDATE_INTERVAL,
)
from homeassistant.const import ATTR_ATTRIBUTION

from datetime import datetime, timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER: logging.Logger = logging.getLogger(__package__)
_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info = None):
	"""Setup sensor platform"""

	async def async_update_data():
		# try:
		flagDays = hass.data[DOMAIN][CONF_CLIENT]
		await hass.async_add_executor_job(flagDays.getFlagdays)
		# except Exception as e:
		# 	raise UpdateFailed(f"Error communicating with server: {e}")

	coordinator = DataUpdateCoordinator(
		hass,
		_LOGGER,
		name = CONF_PLATFORM,
		update_method = async_update_data,
		update_interval = timedelta(minutes = UPDATE_INTERVAL)
	)

	# Immediate refresh
	await coordinator.async_request_refresh()

	# Add the sensors
	flagDays = hass.data[DOMAIN][CONF_CLIENT]
	entities = []
	entities.append(FlagDaysSensor(hass, coordinator, flagDays))

	async_add_entities(entities)

class FlagDaysSensor(SensorEntity):
	def __init__(self, hass, coordinator, flagDays) -> None:
		self._hass = hass
		self._coordinator = coordinator
		self._name = 'Flagdays'
		self._icon = 'mdi:flag'
		self._next_event = flagDays._next_event
		self._events = flagDays._events

	@property
	def name(self) -> str:
		return self._name

	@property
	def state(self):
		return self._next_event['days_to_event']

	@property
	def extra_state_attributes(self):
		# Prepare a dictionary with a list of credits
		attr = { ATTR_ATTRIBUTION: [ATTRIBUTION] }

		for credit in CREDITS:
			attr[ATTR_ATTRIBUTION].append(credit['organization'] + " (" + credit['site'] + ")")

		for key in self._next_event:
			attr[key] = self._next_event[key]

		attr['events'] = self._events

		return attr

	@property
	def icon(self):
		return self._icon

	@property
	def unique_id(self):
		return '8d0c7cbec0ca4fc38e980165dafe0380'

	@property
	def should_poll(self):
		"""No need to poll. Coordinator notifies entity of updates."""
		return False

	@property
	def available(self):
		"""Return if entity is available."""
		return self._coordinator.last_update_success

	async def async_update(self):
		"""Update the entity. Only used by the generic entity update service."""
		await self._coordinator.async_request_refresh()

	async def async_added_to_hass(self):
		"""When entity is added to hass."""
		self.async_on_remove(
			self._coordinator.async_add_listener(
				self.async_write_ha_state
			)
		)