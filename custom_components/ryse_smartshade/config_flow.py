"""Config flow for Ryse SmartShade integration.

Supports:
  - Automatic discovery via HA Bluetooth (devices with local_name RZSS*)
  - Manual configuration by entering the BLE MAC address
"""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_ADDRESS, CONF_NAME
from homeassistant.core import callback

from .const import (
    CONF_FAST_MODE,
    CONF_USE_HA_BLE,
    DEFAULT_FAST_MODE,
    DEFAULT_USE_HA_BLE,
    DEVICE_NAME_PREFIX,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class RyseSmartShadeConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ryse SmartShade."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovery_info: BluetoothServiceInfoBleak | None = None
        self._discovered_address: str | None = None
        self._discovered_name: str | None = None

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> ConfigFlowResult:
        """Handle Bluetooth discovery."""
        _LOGGER.debug(
            "Bluetooth discovery: %s (%s)",
            discovery_info.name,
            discovery_info.address,
        )
        await self.async_set_unique_id(discovery_info.address.upper())
        self._abort_if_unique_id_configured()

        self._discovery_info = discovery_info
        self._discovered_address = discovery_info.address
        self._discovered_name = discovery_info.name or "Ryse SmartShade"

        self.context["title_placeholders"] = {
            "name": self._discovered_name,
            "address": self._discovered_address,
        }
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm Bluetooth discovery."""
        if user_input is not None:
            name = user_input.get(CONF_NAME, self._discovered_name)
            return self.async_create_entry(
                title=name,
                data={
                    CONF_ADDRESS: self._discovered_address,
                    CONF_NAME: name,
                    CONF_USE_HA_BLE: True,
                },
                options={
                    CONF_FAST_MODE: user_input.get(CONF_FAST_MODE, DEFAULT_FAST_MODE),
                },
            )

        return self.async_show_form(
            step_id="bluetooth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=self._discovered_name): str,
                    vol.Optional(CONF_FAST_MODE, default=DEFAULT_FAST_MODE): bool,
                }
            ),
            description_placeholders={
                "name": self._discovered_name,
                "address": self._discovered_address,
            },
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle user-initiated setup.

        Offers a list of discovered Bluetooth devices or manual entry.
        """
        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            if address == "manual":
                return await self.async_step_manual()

            # User selected a discovered device
            await self.async_set_unique_id(address.upper())
            self._abort_if_unique_id_configured()

            # Find the discovery info for this address
            service_infos = async_discovered_service_info(self.hass)
            ble_name = "Ryse SmartShade"
            for info in service_infos:
                if info.address.upper() == address.upper():
                    ble_name = info.name or ble_name
                    break

            self._discovered_address = address
            self._discovered_name = ble_name
            return await self.async_step_bluetooth_confirm()

        # Build list of discovered Ryse devices
        discovered: dict[str, str] = {}
        service_infos = async_discovered_service_info(self.hass)
        for info in service_infos:
            if info.name and info.name.startswith(DEVICE_NAME_PREFIX):
                # Check this device isn't already configured
                if not self._address_already_configured(info.address):
                    discovered[info.address.upper()] = (
                        f"{info.name} ({info.address})"
                    )

        if not discovered:
            return await self.async_step_manual()

        # Add manual entry option
        discovered["manual"] = "Enter address manually..."

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ADDRESS): vol.In(discovered),
                }
            ),
        )

    async def async_step_manual(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle manual MAC address entry."""
        errors: dict[str, str] = {}

        if user_input is not None:
            address = user_input[CONF_ADDRESS].upper().strip()

            # Basic MAC address validation
            if not self._validate_mac(address):
                errors[CONF_ADDRESS] = "invalid_mac"
            else:
                await self.async_set_unique_id(address)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, f"Ryse Shade {address[-5:]}"),
                    data={
                        CONF_ADDRESS: address,
                        CONF_NAME: user_input.get(
                            CONF_NAME, f"Ryse Shade {address[-5:]}"
                        ),
                        CONF_USE_HA_BLE: user_input.get(
                            CONF_USE_HA_BLE, DEFAULT_USE_HA_BLE
                        ),
                    },
                    options={
                        CONF_FAST_MODE: user_input.get(
                            CONF_FAST_MODE, DEFAULT_FAST_MODE
                        ),
                    },
                )

        return self.async_show_form(
            step_id="manual",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ADDRESS): str,
                    vol.Required(CONF_NAME, default="Ryse SmartShade"): str,
                    vol.Optional(CONF_USE_HA_BLE, default=DEFAULT_USE_HA_BLE): bool,
                    vol.Optional(CONF_FAST_MODE, default=DEFAULT_FAST_MODE): bool,
                }
            ),
            errors=errors,
        )

    def _address_already_configured(self, address: str) -> bool:
        """Check if a device address is already configured."""
        for entry in self._async_current_entries():
            if entry.data.get(CONF_ADDRESS, "").upper() == address.upper():
                return True
        return False

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Create the options flow."""
        return RyseSmartShadeOptionsFlow()

    @staticmethod
    def _validate_mac(address: str) -> bool:
        """Validate a MAC address format (XX:XX:XX:XX:XX:XX)."""
        parts = address.split(":")
        if len(parts) != 6:
            return False
        return all(len(p) == 2 and all(c in "0123456789ABCDEF" for c in p) for p in parts)


class RyseSmartShadeOptionsFlow(OptionsFlow):
    """Handle options for Ryse SmartShade."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_FAST_MODE,
                        default=self.config_entry.options.get(
                            CONF_FAST_MODE, DEFAULT_FAST_MODE
                        ),
                    ): bool,
                }
            ),
        )
