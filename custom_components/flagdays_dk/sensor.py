from __future__ import annotations

import logging
from astral import Observer
from astral.sun import sun
from datetime import datetime
from dateutil import tz

from homeassistant.const import ATTR_ATTRIBUTION
from .const import (
    CONF_CLIENT,
    CONF_OFFSET,
    CONF_PLATFORM,
    CREDITS,
    DOMAIN,
    UPDATE_INTERVAL,
)

ATTR_AGE = "age"
ATTR_CONCURRENT = "concurrent_flagdays"
ATTR_NAME = "name"
ATTR_FLAG = "flag"
ATTR_FLAG_DOWN = "flag_down_time"
ATTR_FLAG_DOWN_TRIGGER = "flag_down_time_trigger"
ATTR_FLAG_UP = "flag_up_time"
ATTR_FLAG_UP_TRIGGER = "flag_up_time_trigger"
ATTR_HALF_MAST = "half_mast"
ATTR_YEARS = "years"

from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER: logging.Logger = logging.getLogger(__package__)
_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):

    # Define a update function
    async def async_update_data():
        # Retrieve the client stored in the hass data stack
        flagdays = hass.data[DOMAIN][CONF_CLIENT]
        # Call, and wait for it to finish, the function with the refresh procedure
        _LOGGER.debug("Updating flagdays...")
        await hass.async_add_executor_job(flagdays.update)

    # Create a coordinator
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=CONF_PLATFORM,
        update_method=async_update_data,
        update_interval=timedelta(minutes=UPDATE_INTERVAL),
    )

    # Immediate refresh
    await coordinator.async_request_refresh()

    # Add the sensor to Home Assistant
    async_add_entities(
        [FlagDaysSensor(hass, coordinator, hass.data[DOMAIN][CONF_CLIENT])]
    )


class FlagDaysSensor(SensorEntity):
    def __init__(self, hass, coordinator, flagdays) -> None:
        self._hass = hass
        self._coordinator = coordinator
        self._flagdays = flagdays
        self._nextFlagday = flagdays.getFlagdays()[0]

    @property
    def name(self):
        return self._nextFlagday.getName()

    @property
    def icon(self):
        return "mdi:flag"

    @property
    def state(self):
        return self._flagdays.getDays()

    @property
    def unique_id(self):
        return "8d0c7cbec0ca4fc38e980165dafe0380"

    @property
    def extra_state_attributes(self):
        # Calculate the sunrise and sunset from the coordinates of the HA server
        geo = Observer(
            self._hass.config.latitude,
            self._hass.config.longitude,
            self._hass.config.elevation,
        )
        s = sun(
            geo, date=self._nextFlagday.getDate(), tzinfo=tz.gettz("Europe/Copenhagen")
        )

        # Calculate the correct time for flag up
        flagUpTime = (
            datetime.strptime("08:00", "%H:%M")
            if s["sunrise"].hour < 8
            else s["sunrise"]
        )

        attr = {
            ATTR_YEARS: self._nextFlagday.getYears(),
            ATTR_FLAG: self._nextFlagday.getFlag(),
            ATTR_FLAG_UP: flagUpTime.strftime("%H:%M"),
            ATTR_FLAG_DOWN: s["sunset"].strftime("%H:%M"),
            ATTR_FLAG_UP_TRIGGER: (
                flagUpTime - timedelta(minutes=self._hass.data[DOMAIN][CONF_OFFSET])
            ).strftime("%H:%M"),
            ATTR_FLAG_DOWN_TRIGGER: (
                s["sunset"] - timedelta(minutes=self._hass.data[DOMAIN][CONF_OFFSET])
            ).strftime("%H:%M"),
            ATTR_HALF_MAST: self._nextFlagday.getHalfMast(),
            ATTR_CONCURRENT: self._flagdays.getConcurrentFlagdays(
                self._nextFlagday.getDate()
            ),
        }
        attr["future_flagdays"] = []
        for flagday in self._flagdays.getFutureFlagdays():
            attr["future_flagdays"].append(
                {
                    "name": flagday.getName(),
                    "date": flagday.getDate("%-d-%-m"),
                    "date_end": flagday.getDateEnd("%-d-%-m"),
                }
            )
        attr[ATTR_ATTRIBUTION] = CREDITS
        return attr

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
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )
