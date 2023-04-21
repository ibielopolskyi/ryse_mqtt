## MQTT integration for Ryse smart shades.

This allows to integrate Ryse SmartShade bypassing HomeKit bridge directly with MQTT.
No need for the app or registration either.


## Features
* No-app, no-bridge, "free without registration" onboarding and integration.
* Home Assistant auto-discovery as a cover entity grouped by device.
* Fast mode for lightning fast responsiveness (might be detrimental for battery life, since it will keep connection alive)

```
git clone https://github.com/ibielopolskyi/ryse_mqtt
cd ryse_mqtt
```

## Pairing

For now pairing is manual as there is no grouping feature.
Use `bluetoothctl`  as follows:

```
sudo bluetoothctl
```

Now, we need to locate the Ryse mac address (their name by default is always RZSS):
```
menu scan
pattern RZSS
back
scan on
```

After locating the mac address, put your Ryse device into pairing mode (3 clicks on pair button) and run:
```
trust <YOUR MAC ADDRESS HERE>
connect <YOUR MAC ADDRESS HERE>
```
Please, note that no pairing is necessary at this point.
Bluetoothctl will offer to pair and remember. Click yes.

## Configuration
```
cp example.conf config.conf
```

In `config.conf` the `[mqtt]` section is conveniently going to be passed through to the [MQTT Client](https://sbtinstruments.github.io/asyncio-mqtt/connecting-to-the-broker.html)
In the most cases, merely set up `hostname` variable there

```
[mqtt]
hostname=MQTT host IP
```

In the `[ryse]` section create a map of your device preferred names to it's MAC address:
```
[ryse]
A Blind=<Mac Address>
Another Blind=<Mac Address>
```

In `home_assistant` section set `discovery_topic` and `device_name` . Discovery topic by default is `homeassistant` and `device_name` will be used in Home Assistant device identifier to group entities. 
```
[home_assistant]
discovery_topic=homeassistant
device_name=Ryse Controller
```

Finally, if you don't want to wait for reconnect, define specific blinds in `[fast]` section. Especially useful when your shades are part of automation. 
```
[fast]
A blind=true
```

## Run!

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

## FAQ

* Ryse blind not connecting after restart.

A: go to `bluetoothctl` and run `disconnect <RYSE MAC ADDRESS>` or simply wait. It will expire previous session and reconnect.

