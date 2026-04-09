"""Cover platform for Ryse SmartShade."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.cover import (
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .ble_device import RyseSmartShadeDevice
from .const import DOMAIN, POSITION_CLOSED, POSITION_OPEN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ryse SmartShade cover from a config entry."""
    device: RyseSmartShadeDevice = entry.runtime_data
    async_add_entities([RyseSmartShadeCover(device, entry)])


class RyseSmartShadeCover(CoverEntity):
    """Representation of a Ryse SmartShade as a Home Assistant Cover."""

    _attr_device_class = CoverDeviceClass.SHADE
    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.SET_POSITION
        | CoverEntityFeature.STOP
    )
    _attr_has_entity_name = True
    _attr_name = None  # Use device name as entity name

    def __init__(
        self,
        device: RyseSmartShadeDevice,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the cover entity."""
        self._device = device
        self._entry = entry
        self._unregister_callback: callable | None = None

        address = entry.data[CONF_ADDRESS]
        name = entry.data.get(CONF_NAME, device.name)

        self._attr_unique_id = address.upper().replace(":", "_")
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, address.upper())},
            name=name,
            manufacturer="Ryse",
            model="SmartShade",
            sw_version="1.0.0",
            connections={("bluetooth", address.upper())},
        )

    async def async_added_to_hass(self) -> None:
        """Run when entity is added to hass."""
        self._unregister_callback = self._device.register_callback(
            self._handle_state_update
        )

    async def async_will_remove_from_hass(self) -> None:
        """Run when entity is about to be removed from hass."""
        if self._unregister_callback:
            self._unregister_callback()
            self._unregister_callback = None

    @callback
    def _handle_state_update(self) -> None:
        """Handle a state update from the BLE device."""
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Return True if the shade is available."""
        return self._device.available

    @property
    def is_closed(self) -> bool | None:
        """Return True if the shade is fully closed."""
        if not self._device.available:
            return None
        return self._device.position == POSITION_CLOSED

    @property
    def is_opening(self) -> bool:
        """Return True if the shade is opening."""
        return self._device.state == "OPENING"

    @property
    def is_closing(self) -> bool:
        """Return True if the shade is closing."""
        return self._device.state == "CLOSING"

    @property
    def current_cover_position(self) -> int | None:
        """Return the current position (0=closed, 100=open)."""
        if not self._device.available:
            return None
        return self._device.position

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the shade."""
        await self._device.async_open()

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the shade."""
        await self._device.async_close()

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """Set the shade to a specific position."""
        position = kwargs.get("position", POSITION_OPEN)
        await self._device.async_set_position(position)

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the shade movement."""
        await self._device.async_stop()
