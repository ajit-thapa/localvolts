"""Localvolts Energy Monitor integration."""
import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from .const import DOMAIN
from .coordinator import LocalvoltsMonitorCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


def validate_api_key(key: str) -> bool:
    return bool(key.strip())


def validate_partner_id(pid: str) -> bool:
    return bool(pid.strip())


def validate_nmi_id(nmi: str) -> bool:
    nmi = nmi.strip().upper()
    return len(nmi) == 10 and nmi.isalnum()


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = LocalvoltsMonitorCoordinator(
        hass,
        entry.data["api_key"],
        entry.data["partner_id"],
        entry.data["nmi_id"],
    )
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
