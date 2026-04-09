## Ryse SmartShade Integration

Direct BLE integration for Ryse SmartShade motorized blinds/shades. No app, no bridge, no HomeKit, no registration required.

## Features

* No-app, no-bridge, "free without registration" onboarding and integration
* Home Assistant custom integration with UI-based config flow
* Automatic Bluetooth discovery of Ryse shades (RZSS devices)
* Uses Home Assistant's built-in Bluetooth stack (or direct BLE as fallback)
* Cover entity with full position control (open/close/set position/stop)
* Fast mode for instant responsiveness (keeps BLE connection alive)
* Options flow to change fast mode after setup
* Standalone MQTT mode also available (legacy)

---

## Option 1: Home Assistant Custom Integration (Recommended)

### Install

Copy the `custom_components/ryse_smartshade` folder to your Home Assistant `config/custom_components/` directory:

```
# From this repo
cp -r custom_components/ryse_smartshade /path/to/ha/config/custom_components/
```

Or with HACS: add this repository as a custom repository (Integration category).

Restart Home Assistant.

### Setup

**Automatic Discovery (HA Bluetooth):**

If your HA instance has a Bluetooth adapter, Ryse shades (named `RZSS*`) will be discovered automatically. You'll see a notification to configure them.

**Manual Setup:**

1. Go to **Settings > Devices & Services > Add Integration**
2. Search for **Ryse SmartShade**
3. Either select a discovered device or enter the MAC address manually

### Configuration Options

| Option | Description |
|--------|-------------|
| **Device name** | Friendly name for the shade |
| **Use HA Bluetooth** | Use Home Assistant's built-in Bluetooth (recommended) |
| **Fast mode** | Keep BLE connection alive for instant responsiveness (uses more battery) |

Fast mode can be changed after setup via the integration's **Configure** button.

### Pairing

Put your Ryse shade into pairing mode (3 clicks on the pair button). If using HA Bluetooth, the device should be discovered automatically.

For manual pairing (or if HA Bluetooth is not available):
```
sudo bluetoothctl
menu scan
pattern RZSS
back
scan on
```

After locating the MAC address:
```
trust <YOUR MAC ADDRESS HERE>
connect <YOUR MAC ADDRESS HERE>
```
Bluetoothctl will offer to pair and remember. Click yes.

---

## Option 2: Standalone MQTT Mode (Legacy)

This mode runs as a standalone Python service that bridges BLE to MQTT with Home Assistant auto-discovery.

```
git clone https://github.com/ibielopolskyi/ryse_mqtt
cd ryse_mqtt
```

### Configuration
```
cp example.conf config.conf
```

In `config.conf` the `[mqtt]` section is passed through to the [MQTT Client](https://sbtinstruments.github.io/asyncio-mqtt/connecting-to-the-broker.html).
In most cases, merely set up `hostname`:

```
[mqtt]
hostname=MQTT host IP
```

In the `[ryse]` section create a map of your device preferred names to its MAC address:
```
[ryse]
A Blind=<Mac Address>
Another Blind=<Mac Address>
```

In `home_assistant` section set `discovery_topic` and `device_name`. Discovery topic by default is `homeassistant` and `device_name` will be used in Home Assistant device identifier to group entities.
```
[home_assistant]
discovery_topic=homeassistant
device_name=Ryse Controller
```

For instant responsiveness, define specific blinds in `[fast]` section:
```
[fast]
A blind=true
```

### Run

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python ryse_mqtt
```
Or:
```
python ryse_mqtt <path to config file>
```

---

## FAQ

* **Ryse blind not connecting after restart.**
  Go to `bluetoothctl` and run `disconnect <RYSE MAC ADDRESS>` or simply wait. It will expire the previous session and reconnect.

* **HA Bluetooth vs Direct BLE?**
  HA Bluetooth is recommended as it shares the adapter with other integrations and supports automatic discovery. Direct BLE is useful if the shade is paired to a different adapter or remote host.

