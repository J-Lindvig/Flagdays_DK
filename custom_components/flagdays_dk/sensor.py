from __future__ import annotations

import logging

from homeassistant.const import ATTR_ATTRIBUTION
from .const import (
    CONF_CLIENT,
    CONF_PLATFORM,
    CREDITS,
    DOMAIN,
    UPDATE_INTERVAL,
)

from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER: logging.Logger = logging.getLogger(__package__)
_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):

    # Define a update function
    async def async_update_data():
        # Retrieve the client stored in the hass data stack
        flagDays = hass.data[DOMAIN][CONF_CLIENT]
        # Call, and wait for it to finish, the function with the refresh procedure
        _LOGGER.debug("Updating flagdays...")
        await hass.async_add_executor_job(flagDays.update)

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
    def __init__(self, hass, coordinator, flagDays_DK) -> None:
        self._hass = hass
        self._coordinator = coordinator
        self._flagDays_DK = flagDays_DK
        self._nextFlagDay = self._flagDays_DK.getNextFlagDay()
        self._name = DOMAIN
        self._icon = "mdi:flag"

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def state(self):
        return self._nextFlagDay.getDays()

    @property
    def unique_id(self):
        return "8d0c7cbec0ca4fc38e980165dafe0380"

    @property
    def extra_state_attributes(self):
        attr = {}

        attr["name"] = self._nextFlagDay.getName()
        attr["flag"] = self._nextFlagDay.getFlag()
        attr["instructions"] = self._nextFlagDay.getInstructions()
        attr["flag_up_time"] = self._nextFlagDay.getTimeTable()["flagUpTime"]
        attr["flag_down_time"] = self._nextFlagDay.getTimeTable()["flagDownTime"]
        attr["flag_up_time_trigger"] = self._nextFlagDay.getTimeTable()[
            "flagUpTriggerTime"
        ]
        attr["flag_down_time_trigger"] = self._nextFlagDay.getTimeTable()[
            "flagDownTriggerTime"
        ]

        attr["future_flagdays"] = []
        for flagDay in self._flagDays_DK.getFutureFlagDays():
            attr["future_flagdays"].append(
                {
                    "name": flagDay.getName(),
                    "date": flagDay.getDateStr(),
                    "days": flagDay.getDays(),
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
