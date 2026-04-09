"""The Ryse SmartShade integration.

Controls Ryse SmartShade BLE motorized blinds/shades directly via Bluetooth,
without requiring the Ryse app, bridge, or HomeKit.

Supports two BLE transport modes:
  - Home Assistant Bluetooth (default): Uses HA's built-in Bluetooth adapter
    management for automatic discovery and connection handling.
  - Direct BLE: Connects to the shade via bleak directly, useful when the
    shade is paired to a different Bluetooth adapter or remote host.
"""

from __future__ import annotations

import logging

from homeassistant.components.bluetooth import (
    BluetoothCallbackMatcher,
    BluetoothChange,
    BluetoothScanningMode,
    BluetoothServiceInfoBleak,
    async_ble_device_from_address,
    async_register_callback,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, CONF_NAME, Platform
from homeassistant.core import HomeAssistant, callback

from .ble_device import RyseSmartShadeDevice
from .const import CONF_FAST_MODE, CONF_USE_HA_BLE, DEFAULT_FAST_MODE, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.COVER]

type RyseSmartShadeConfigEntry = ConfigEntry[RyseSmartShadeDevice]


async def async_setup_entry(
    hass: HomeAssistant, entry: RyseSmartShadeConfigEntry
) -> bool:
    """Set up Ryse SmartShade from a config entry."""
    address: str = entry.data[CONF_ADDRESS]
    name: str = entry.data.get(CONF_NAME, f"Ryse Shade {address[-5:]}")
    use_ha_ble: bool = entry.data.get(CONF_USE_HA_BLE, True)
    fast_mode: bool = entry.options.get(CONF_FAST_MODE, DEFAULT_FAST_MODE)

    ble_device = None
    if use_ha_ble:
        ble_device = async_ble_device_from_address(hass, address, connectable=True)
        if ble_device:
            _LOGGER.debug("Using HA Bluetooth device for %s", address)
        else:
            _LOGGER.warning(
                "HA Bluetooth device not found for %s; will use direct BLE",
                address,
            )

    device = RyseSmartShadeDevice(
        address=address,
        name=name,
        fast_mode=fast_mode,
        ble_device=ble_device,
    )

    entry.runtime_data = device

    # Register a callback to update the BLEDevice when HA sees new advertisements
    if use_ha_ble:

        @callback
        def _async_update_ble_device(
            service_info: BluetoothServiceInfoBleak, change: BluetoothChange
        ) -> None:
            """Update the BLEDevice when a new advertisement is received."""
            _LOGGER.debug("New BLE advertisement from %s", service_info.address)
            device.set_ble_device(service_info.device)

        entry.async_on_unload(
            async_register_callback(
                hass,
                _async_update_ble_device,
                BluetoothCallbackMatcher(address=address),
                BluetoothScanningMode.ACTIVE,
            )
        )

    # Start the connection loop (connects immediately if fast_mode)
    await device.start_connection_loop()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Handle options updates
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: RyseSmartShadeConfigEntry
) -> bool:
    """Unload a Ryse SmartShade config entry."""
    device: RyseSmartShadeDevice = entry.runtime_data

    await device.stop_connection_loop()
    await device.disconnect()

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_update_listener(
    hass: HomeAssistant, entry: RyseSmartShadeConfigEntry
) -> None:
    """Handle options updates."""
    await hass.config_entries.async_reload(entry.entry_id)
