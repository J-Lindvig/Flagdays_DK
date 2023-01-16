from __future__ import annotations

import logging

from .flagdays_dk import flagdays_dk
from collections import OrderedDict

from .const import (
    DOMAIN,
    CONF_CLIENT,
    CONF_EXCLUDE,
    CONF_FLAGDAYS,
    CONF_INCLUDE,
    CONF_OFFSET,
    CONF_PLATFORM,
    DEFAULT_DATE_FORMAT,
    DEFAULT_OFFSET,
    KEY_DATE,
    KEY_FRIENDLY_NAME,
    KEY_NAME,
    KEY_PRIORITY,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)
_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    # Get the configuration
    conf = config.get(DOMAIN)
    # If no config, abort
    if conf is None:
        return True

    # Create a instance of the flagdays_dk
    flagdays = flagdays_dk(
        include=config[DOMAIN].get(CONF_INCLUDE, []),
        exclude=config[DOMAIN].get(CONF_EXCLUDE, []),
    )

    def flagdayFromSensor(entity):
        flagdayObj = hass.states.get(customFlagday)
        if KEY_DATE in flagdayObj.attributes:
            return {
                flagdayObj.attributes[KEY_FRIENDLY_NAME]: {
                    KEY_DATE: flagdayObj.attributes[KEY_DATE].strftime(
                        DEFAULT_DATE_FORMAT
                    ),
                    KEY_PRIORITY: priorityCheck(flagdayObj.attributes),
                }
            }

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
