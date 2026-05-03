"""Sensors for Localvolts Energy Monitor."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceEntryType

from .const import DOMAIN, SENSOR_DEFINITIONS
from .coordinator import LocalvoltsMonitorCoordinator

_LOGGER = logging.getLogger(__name__)


class LocalvoltsNumericSensor(CoordinatorEntity, SensorEntity):
    """Generic sensor for numeric API fields."""

    _attr_should_poll = False

    def __init__(
        self,
        coordinator: LocalvoltsMonitorCoordinator,
        key: str,
        suffix: str,
        unit: str,
        device_class: SensorDeviceClass | None,
        factor: float,
    ) -> None:
        super().__init__(coordinator)
        self._key = key
        nmi = coordinator.nmi_id
        self._attr_name = f"NMI {nmi} {suffix}"
        self._attr_unique_id = f"{nmi}_{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._factor = factor
        self._cached_value: float | None = None

        self._attr_device_info = {
            "identifiers": {(DOMAIN, nmi)},
            "name": f"Localvolts NMI {nmi}",
            "manufacturer": "Localvolts",
            "model": "Virtual Energy Meter",
            "entry_type": DeviceEntryType.SERVICE,
        }

    @property
    def native_value(self) -> float | None:
        raw = self.coordinator.data.get(self._key)
        if raw is None or raw == "N/A":
            return self._cached_value
        try:
            value = float(raw) * self._factor
            self._cached_value = value
            return value
        except (ValueError, TypeError):
            return self._cached_value


class LocalvoltsDataLagSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing seconds since interval start."""

    _attr_native_unit_of_measurement = "s"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_should_poll = False

    def __init__(self, coordinator: LocalvoltsMonitorCoordinator) -> None:
        super().__init__(coordinator)
        nmi = coordinator.nmi_id
        self._attr_name = f"NMI {nmi} Data Lag"
        self._attr_unique_id = f"{nmi}_data_lag"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, nmi)},
            "name": f"Localvolts NMI {nmi}",
            "manufacturer": "Localvolts",
            "model": "Virtual Energy Meter",
            "entry_type": DeviceEntryType.SERVICE,
        }

    @property
    def native_value(self) -> float | None:
        lag = self.coordinator.time_past_start
        return lag.total_seconds() if lag else None


class LocalvoltsIntervalEndSensor(CoordinatorEntity, SensorEntity):
    """Timestamp of current interval's end."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_should_poll = False

    def __init__(self, coordinator: LocalvoltsMonitorCoordinator) -> None:
        super().__init__(coordinator)
        nmi = coordinator.nmi_id
        self._attr_name = f"NMI {nmi} Interval End"
        self._attr_unique_id = f"{nmi}_interval_end"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, nmi)},
            "name": f"Localvolts NMI {nmi}",
            "manufacturer": "Localvolts",
            "model": "Virtual Energy Meter",
            "entry_type": DeviceEntryType.SERVICE,
        }

    @property
    def native_value(self) -> datetime | None:
        return self.coordinator.interval_end


class LocalvoltsLastUpdateSensor(CoordinatorEntity, SensorEntity):
    """Timestamp when data was last updated."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_should_poll = False

    def __init__(self, coordinator: LocalvoltsMonitorCoordinator) -> None:
        super().__init__(coordinator)
        nmi = coordinator.nmi_id
        self._attr_name = f"NMI {nmi} Last Update"
        self._attr_unique_id = f"{nmi}_last_update"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, nmi)},
            "name": f"Localvolts NMI {nmi}",
            "manufacturer": "Localvolts",
            "model": "Virtual Energy Meter",
            "entry_type": DeviceEntryType.SERVICE,
        }

    @property
    def native_value(self) -> datetime | None:
        return self.coordinator.last_update


class LocalvoltsQualitySensor(CoordinatorEntity, SensorEntity):
    """Data quality indicator (Act, Exp, Fcst)."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ["Act", "Exp", "Fcst"]
    _attr_should_poll = False

    def __init__(self, coordinator: LocalvoltsMonitorCoordinator) -> None:
        super().__init__(coordinator)
        nmi = coordinator.nmi_id
        self._attr_name = f"NMI {nmi} Data Quality"
        self._attr_unique_id = f"{nmi}_quality"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, nmi)},
            "name": f"Localvolts NMI {nmi}",
            "manufacturer": "Localvolts",
            "model": "Virtual Energy Meter",
            "entry_type": DeviceEntryType.SERVICE,
        }

    @property
    def native_value(self) -> str | None:
        return self.coordinator.data.get("quality")


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []
    for key, suffix, unit, device_class, factor in SENSOR_DEFINITIONS:
        entities.append(
            LocalvoltsNumericSensor(coordinator, key, suffix, unit, device_class, factor)
        )
    entities.append(LocalvoltsDataLagSensor(coordinator))
    entities.append(LocalvoltsIntervalEndSensor(coordinator))
    entities.append(LocalvoltsLastUpdateSensor(coordinator))
    entities.append(LocalvoltsQualitySensor(coordinator))

    async_add_entities(entities)
