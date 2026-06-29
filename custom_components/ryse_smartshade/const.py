"""Constants for the Ryse SmartShade integration."""

DOMAIN = "ryse_smartshade"

# BLE GATT UUIDs
UUID_TX = "a72f2802-b0bd-498b-b4cd-4a3901388238"
UUID_RX = "a72f2801-b0bd-498b-b4cd-4a3901388238"
UUID_SERVICE = "a72f2800-b0bd-498b-b4cd-4a3901388238"

# BLE device default name prefix
DEVICE_NAME_PREFIX = "RZSS"

# Configuration keys
CONF_USE_HA_BLE = "use_ha_ble"
CONF_FAST_MODE = "fast_mode"

# Default values
DEFAULT_FAST_MODE = False
DEFAULT_USE_HA_BLE = True

# Position constants
POSITION_OPEN = 100
POSITION_CLOSED = 0

# BLE command structure
CMD_HEADER = 245  # 0xF5
CMD_TYPE = 3
CMD_PARAM1 = 1
CMD_PARAM2 = 1

# State byte indices in BLE response
STATE_MOTION_INDEX = 5
STATE_POSITION_INDEX = 4

# Motion states from device
MOTION_STOPPED = 0
MOTION_OPENING = 1
MOTION_CLOSING = 2

# Reconnection settings
RECONNECT_INTERVAL = 5.0
BLE_DISCONNECT_DELAY = 0.5
BLE_CONNECT_TIMEOUT = 30.0

# Local patch (keepalive-debounce):
# - While connected, issue a keep-alive GATT read every RECONNECT_INTERVAL so
#   the shade does not drop an idle BLE link (root cause of the unavailable
#   flapping on a stable proxy).
# - Debounce: a brief disconnect no longer flips the entity to unavailable;
#   it only goes unavailable if the link stays down this many seconds.
UNAVAILABLE_GRACE = 30.0
