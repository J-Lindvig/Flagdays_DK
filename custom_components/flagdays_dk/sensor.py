from __future__ import annotations

import logging
from astral import Observer
from astral.sun import sun
from datetime import datetime, timedelta
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

ATTR_CONCURRENT = "concurrent_flagdays"
ATTR_DATE = "date"
ATTR_DATE_END = "date_end"
ATTR_FLAGDAY_NAME = "flagday_name"
ATTR_FLAG = "flag"
ATTR_FLAG_DOWN = "flag_down_time"
ATTR_FLAG_DOWN_TRIGGER = "flag_down_time_trigger"
ATTR_FLAG_UP = "flag_up_time"
ATTR_FLAG_UP_TRIGGER = "flag_up_time_trigger"
ATTR_HALF_MAST = "half_mast"
ATTR_YEARS = "years"

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
        self.hass = hass
        self.coordinator = coordinator
        self.flagdays = flagdays
        self.nextFlagday = flagdays.flagdays[0]

    @property
    def name(self):
        return DOMAIN

    @property
    def icon(self):
        return "mdi:flag"

    @property
    def state(self):
        return self.flagdays.days

    @property
    def unique_id(self):
        return "1708981ec9bb4fbfb5d183771a888af0"

    @property
    def extra_state_attributes(self):
        # Calculate the sunrise and sunset from the coordinates of the HA server
        geo = Observer(
            self.hass.config.latitude,
            self.hass.config.longitude,
            self.hass.config.elevation,
        )
        s = sun(
            geo, date=self.nextFlagday.getDate(), tzinfo=tz.gettz("Europe/Copenhagen")
        )

        # Calculate the correct time for flag up
        flagUpTime = (
            datetime.strptime("08:00", "%H:%M")
            if s["sunrise"].hour < 8
            else s["sunrise"]
        )

        attr = {
            ATTR_FLAGDAY_NAME: self.nextFlagday.name,
            ATTR_YEARS: self.nextFlagday.years,
            ATTR_FLAG: self.nextFlagday.flag,
            ATTR_FLAG_UP: flagUpTime.strftime("%H:%M"),
            ATTR_FLAG_DOWN: s["sunset"].strftime("%H:%M"),
            ATTR_FLAG_UP_TRIGGER: (
                flagUpTime - timedelta(minutes=self.hass.data[DOMAIN][CONF_OFFSET])
            ).strftime("%H:%M"),
            ATTR_FLAG_DOWN_TRIGGER: (
                s["sunset"] - timedelta(minutes=self.hass.data[DOMAIN][CONF_OFFSET])
            ).strftime("%H:%M"),
            ATTR_HALF_MAST: self.nextFlagday.getHalfMast(),
            ATTR_CONCURRENT: self.flagdays.getConcurrentFlagdays(self.nextFlagday.date),
        }
        attr["future_flagdays"] = []
        for flagday in self.flagdays.getFutureFlagdays():
            attr["future_flagdays"].append(
                {
                    ATTR_FLAGDAY_NAME: flagday.name,
                    ATTR_DATE: flagday.getDate("%-d-%-m"),
                    ATTR_DATE_END: flagday.getDateEnd("%-d-%-m"),
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
        return self.coordinator.last_update_success

    async def async_update(self):
        """Update the entity. Only used by the generic entity update service."""
        await self.coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
