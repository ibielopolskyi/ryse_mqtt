"""BLE GATT communication for Ryse SmartShade devices.

Supports two modes:
  1. HA Bluetooth: Uses Home Assistant's built-in Bluetooth stack for device
     discovery and connection management.
  2. Direct BLE: Uses bleak directly (for systems where HA Bluetooth is
     unavailable or the adapter is on a remote host).
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable

from bleak import BleakClient
from bleak.backends.device import BLEDevice
from bleak_retry_connector import establish_connection

from .const import (
    BLE_CONNECT_TIMEOUT,
    CMD_HEADER,
    CMD_PARAM1,
    CMD_PARAM2,
    CMD_TYPE,
    MOTION_CLOSING,
    MOTION_OPENING,
    MOTION_STOPPED,
    POSITION_CLOSED,
    POSITION_OPEN,
    RECONNECT_INTERVAL,
    STATE_MOTION_INDEX,
    STATE_POSITION_INDEX,
    UUID_RX,
    UUID_TX,
)

_LOGGER = logging.getLogger(__name__)


class RyseSmartShadeDevice:
    """Manages BLE communication with a single Ryse SmartShade."""

    def __init__(
        self,
        address: str,
        name: str,
        fast_mode: bool = False,
        ble_device: BLEDevice | None = None,
    ) -> None:
        """Initialize the device.

        Args:
            address: The BLE MAC address.
            name: Friendly name for the shade.
            fast_mode: If True, keep the BLE connection alive.
            ble_device: Optional BLEDevice from HA Bluetooth discovery.
        """
        self.address = address
        self.name = name
        self.fast_mode = fast_mode
        self._ble_device: BLEDevice | None = ble_device
        self._client: BleakClient | None = None
        self._lock = asyncio.Lock()

        # State
        self.position: int = 0
        self.state: str = "STOPPED"
        self.moving: bool = False
        self.available: bool = False

        # Callbacks
        self._state_callbacks: list[Callable[[], None]] = []
        self._running: bool = False
        self._connection_task: asyncio.Task | None = None

    def set_ble_device(self, ble_device: BLEDevice) -> None:
        """Update the BLEDevice reference (from HA Bluetooth scanner)."""
        self._ble_device = ble_device

    def register_callback(self, callback: Callable[[], None]) -> Callable[[], None]:
        """Register a callback for state updates. Returns unregister function."""
        self._state_callbacks.append(callback)

        def unregister() -> None:
            if callback in self._state_callbacks:
                self._state_callbacks.remove(callback)

        return unregister

    def _fire_callbacks(self) -> None:
        """Notify all registered callbacks of a state change."""
        for callback in self._state_callbacks:
            try:
                callback()
            except Exception:
                _LOGGER.exception("Error in state callback")

    @staticmethod
    def _build_position_command(position: int) -> bytes:
        """Build the BLE command bytes for a target position (0-100).

        The device expects the inverted position value.
        """
        device_pos = POSITION_OPEN - position
        return bytes([CMD_HEADER, CMD_TYPE, CMD_PARAM1, CMD_PARAM2, device_pos, device_pos + 2])

    def _parse_state(self, data: bytearray | bytes) -> None:
        """Parse a BLE notification/read response and update internal state."""
        if len(data) < 6:
            _LOGGER.warning("Received short BLE response (%d bytes)", len(data))
            return

        motion = int(data[STATE_MOTION_INDEX])
        raw_position = int(data[STATE_POSITION_INDEX])

        if motion == MOTION_STOPPED:
            self.moving = False
        elif motion == MOTION_OPENING:
            self.state = "OPENING"
            self.moving = True
        elif motion == MOTION_CLOSING:
            self.state = "CLOSING"
            self.moving = True

        if not self.moving:
            self.state = "STOPPED"
            if raw_position == 0:
                self.state = "OPEN"
            elif raw_position == 100:
                self.state = "CLOSED"

        self.position = POSITION_OPEN - raw_position

        _LOGGER.debug(
            "%s state=%s position=%d moving=%s",
            self.name,
            self.state,
            self.position,
            self.moving,
        )
        self._fire_callbacks()

    def _on_notification(self, _sender: Any, data: bytearray) -> None:
        """Handle BLE GATT notification from the shade."""
        self._parse_state(data)

    def _on_disconnect(self, _client: BleakClient) -> None:
        """Handle BLE disconnection."""
        _LOGGER.info("%s disconnected", self.name)
        self.available = False
        self._fire_callbacks()

    @property
    def is_connected(self) -> bool:
        """Return True if the BLE client is connected."""
        return self._client is not None and self._client.is_connected

    async def connect(self) -> bool:
        """Establish a BLE connection and subscribe to notifications."""
        async with self._lock:
            if self.is_connected:
                return True
            try:
                if self._ble_device is not None:
                    # Use HA Bluetooth stack via bleak_retry_connector
                    self._client = await establish_connection(
                        BleakClient,
                        self._ble_device,
                        self.name,
                        disconnected_callback=self._on_disconnect,
                        max_attempts=3,
                    )
                else:
                    # Direct bleak connection (fallback)
                    self._client = BleakClient(
                        self.address,
                        disconnected_callback=self._on_disconnect,
                        timeout=BLE_CONNECT_TIMEOUT,
                    )
                    await self._client.connect()

                if self._client.is_connected:
                    self.available = True
                    # Read initial state
                    initial_data = await self._client.read_gatt_char(UUID_RX)
                    self._parse_state(initial_data)
                    # Subscribe to notifications for live updates
                    await self._client.start_notify(UUID_RX, self._on_notification)
                    _LOGGER.info("%s connected", self.name)
                    self._fire_callbacks()
                    return True

            except Exception:
                _LOGGER.exception("Failed to connect to %s", self.name)
                self.available = False
                self._fire_callbacks()
            return False

    async def disconnect(self) -> None:
        """Disconnect from the BLE device."""
        async with self._lock:
            if self._client and self._client.is_connected:
                try:
                    await self._client.disconnect()
                except Exception:
                    _LOGGER.exception("Error disconnecting %s", self.name)
            self._client = None
            self.available = False
            self._fire_callbacks()

    async def async_set_position(self, position: int) -> None:
        """Set the shade position (0=closed, 100=open)."""
        position = max(POSITION_CLOSED, min(POSITION_OPEN, position))
        if not self.is_connected:
            await self.connect()
        if self.is_connected:
            cmd = self._build_position_command(position)
            await self._client.write_gatt_char(UUID_TX, cmd)
            _LOGGER.debug("%s set position to %d", self.name, position)
        else:
            _LOGGER.warning("Cannot set position: %s not connected", self.name)

    async def async_open(self) -> None:
        """Fully open the shade."""
        await self.async_set_position(POSITION_OPEN)

    async def async_close(self) -> None:
        """Fully close the shade."""
        await self.async_set_position(POSITION_CLOSED)

    async def async_stop(self) -> None:
        """Stop the shade at its current position.

        The Ryse protocol does not have a dedicated stop command.
        We send the current known position which effectively stops movement.
        """
        await self.async_set_position(self.position)

    async def start_connection_loop(self) -> None:
        """Start the background connection loop (for fast mode)."""
        if self._running:
            return
        self._running = True
        self._connection_task = asyncio.ensure_future(self._connection_loop())

    async def stop_connection_loop(self) -> None:
        """Stop the background connection loop."""
        self._running = False
        if self._connection_task:
            self._connection_task.cancel()
            try:
                await self._connection_task
            except asyncio.CancelledError:
                pass
            self._connection_task = None

    async def _connection_loop(self) -> None:
        """Maintain the BLE connection when fast mode is enabled."""
        while self._running:
            try:
                if not self.is_connected and self.fast_mode:
                    await self.connect()
                await asyncio.sleep(RECONNECT_INTERVAL)
            except asyncio.CancelledError:
                break
            except Exception:
                _LOGGER.exception("Connection loop error for %s", self.name)
                await asyncio.sleep(RECONNECT_INTERVAL)
