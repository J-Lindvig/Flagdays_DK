from __future__ import annotations

import logging

from .flagdays_dk_api import flagDays_DK

from homeassistant.const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
)
from .const import (
    DOMAIN,
    CONF_CLIENT,
    CONF_FLAGS,
    CONF_FLAGS_DAYS,
    CONF_HIDE_PAST,
    CONF_TIME_OFFSET,
    CONF_PLATFORM,
    DEFAULT_FLAG,
    DEFAULT_TIME_OFFSET,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)
_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    # Get the configuration
    conf = config.get(DOMAIN)
    # If no config, abort
    if conf is None:
        return True

    coordinates = {}
    coordinates["lat"] = config.get(CONF_LATITUDE, hass.config.latitude)
    coordinates["lon"] = config.get(CONF_LONGITUDE, hass.config.longitude)

    # Load flags - append default
    flags = config[DOMAIN].get(CONF_FLAGS, [DEFAULT_FLAG])
    if not DEFAULT_FLAG in flags:
        flags.append(DEFAULT_FLAG)
    _LOGGER.debug(f"Flags loaded from config: { flags }")

    # Load time offest else DEFAULT_TIME_OFFSET
    time_offset = config[DOMAIN].get(CONF_TIME_OFFSET, DEFAULT_TIME_OFFSET)
    _LOGGER.debug(f"Time offset set to: { time_offset } minutes")

    # Load boolean to hide flagdays in the past
    hidePast = config[DOMAIN].get(CONF_HIDE_PAST, True)
    _LOGGER.debug(f"Hide flagdays in the past is { hidePast }")

    # Load private flagdays
    privateFlagDays = config[DOMAIN].get(CONF_FLAGS_DAYS, [])
    if privateFlagDays:
        _LOGGER.debug(f"Added { len(privateFlagDays) } private flagdays")

    hass.data[DOMAIN] = {
        CONF_CLIENT: flagDays_DK(
            flags, coordinates, time_offset, privateFlagDays, hidePast
        )
    }

    # Add sensors
    hass.async_create_task(
        hass.helpers.discovery.async_load_platform(CONF_PLATFORM, DOMAIN, conf, config)
    )

    # Initialization was successful.
    return True
