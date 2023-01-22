# BS440 - Description
BS440 is a Python code that listens for information from a Medisana BS410/BS430/BS440/BS444
or compatible bluetooth bathroom scale (BSA45 allegedly supported, but manual adjustments needed / not yet correctly implemented in code). When received via Bluetooth LE, it passes the
information (weight, fat, bone mass, etc) over to all activated plugins for further processing.

Currently supported plugins / data processors:
- MQTT (Home Assistant, openHAB, ioBroker, etc), via Autodiscovery
- Local .csv
- Webpage
- Domoticz
- Google Fit
- InfluxDB
- Runalyze Database
- E-Mail

# Further reading:
- Project origin (5 parts): https://keptenkurk.wordpress.com/2016/02/07/connecting-the-medisana-bs440-bluetooth-scale/
- Full step-by-step installation instruction (partially outdated, see below): https://keptenkurk.wordpress.com/2017/03/05/connecting-the-medisana-bs440-bluetooth-scale-epilogue/

# Prerequisites
- Bluetooth LE adapter
- Bluez
- Pygatt >= 3.0.0 release

# Tested on:
**Raspberry Pi 1 B+**
- **OS:** Raspberry Pi OS 8 (Jessie), 4.4.38+ #938, Thu Dec 15 15:17:54 GMT 2016 armv6l GNU/Linux)
- **Bluetooth adapter:** USB device found, idVendor=0a5c, idProduct=21e8, USB device strings: Mfr=1, Product=2, SerialNumber=3, Product: BCM20702A0
- **Bluez:** 5.44 (from source), 5.23-2+rpi2 (from package manager)
- **Pygatt:** 3.0.0

**Raspberry Pi Zero W**
- **OS:** DietPi V153, 4.9.35+ #1, Tue Jul 4 17:16:26 UTC 2017 armv6l GNU/Linux
- **Bluetooth adapter:** Onboard
- **Bluez:** 5.23-2+rpi2 (from package manager)
- **Pygatt:** 3.0.0

**Raspberry Pi 3 B+**
- **OS:** Raspberry Pi OS 11 (Bullseye), 5.15.84-v7+ #1613 SMP Thu Jan 5 11:59:48 GMT 2023 armv7
- **Bluetooth adapter:** Onboard
- **Bluez:** 5.55
- **Pygatt:** 4.0.5

# Preferences / Settings
Before using this app, rename `BS440.example.ini` to `BS440.ini` and personalize your settings.
This file contains the general parameters for communicating with the scale (Bluetooth LE
MAC address) and which plugins to use.

# Run the script at startup
For the script to start automatically at system startup (to monitor the scale all the time)
the script has to be started as a service.

Open the service-file `bs440.service` located under `<...>/BS440-HA-AD/dist/init/linux-systemd/bs440.service`
and edit/verify the `WorkingDirectory` (the absolute path where the script's files are stored), the
python directory (usually `/usr/bin/python`) as well as the name of the script (default `BS440.py`).

Copy the service-file (for generic linux with SystemD support) from
`<...>/BS440-HA-AD/dist/init/linux-systemd/bs440.service` to `/etc/systemd/system`:
```bash
cp <...>/BS440-HA-AD/dist/init/linux-systemd/bs440.service /etc/systemd/system/
```

Tell SystemD to detect new service files:
```bash
systemctl daemon-reload 
```

Start the service now:
```bash
systemctl start bs440
```
Set the service to start at boot:
```bash
systemctl enable bs440
```
The logs of the new bs440 service can be shown at all times via ```journalctl -l -f -u bs440```.

If the service runs without any problem if started manually (```systemctl start bs440```) but not
as a service during startup, check /var/log/syslog for errors. E.g. when activating the mqtt-plugin,
other services, have to be started first. This can be achieved by setting ```After=multi-user.target```.

# Plugins
Currenly these plugins are available:
* BS440mqtt: Send collected data via MQTT to Home Assistant, openHAB, ioBroker for excample
* BS440csv: Store results locally in csv and graph results through webserver
* BS440webapp: Publish data on a local webpage
* BS440domoticz: Store data in virtual sensors of Domoticz home control system
* BS440google: Store data to Google Fit account
* BS440influxdb: Store collected data into InfluxDB time series database for easy graphing using Grafana
* BS440runalizel: Store data to local Runalyze database
* BS440mail: Mail the last 3 stored sets of data to the user

Plugins are found in the plugin folder and named BS440pluginname.py. Each plugin uses
its private .ini file named BS440pluginname.ini
To enable a plugin, add it to the `plugins` key in `BS440.ini`.

Directions on how to install prerequisites, configure and use a specific plugin is found in the Wiki

**BS440mail**

Maintainer: Keptenkurk

Last 3 results are mailed to the user mail adress as configured in BS440mail.ini

**BS440csv**

Maintainer: DjZU

Data is added to a local CSV file. Data is presented by running plotBS440.py which
starts a webserver and serves graphs to the user.
You can use any web server to serve a static site based on the `csv` files. You can find a
working example using the Caddy webserver in [dist/caddy/](dist/caddy/).

**BS440mqtt**

Maintainer: jinnerbichler

Send collected data via MQTT (e.g. to Home Assistant)

**BS440influxdb**

Maintainer: qistoph

Store collected data in InlfuxDB (e.g. for Grafana)

**Domoticz**

Maintainer: Tristan79 - Status: Testing

Configure the Domoticz and user details in BS440domoticz.ini.
When data is received, the sensors will be automatically generated. That easy!

The optional option _hardware_name_ is the name of the dummy hardware to you can use,
if you leave it empty or commented it out, it uses _Medisana_ as default.

After a first run _BS440domoticz.ini_ is updated. In which you can override
the ids to use (if necessary). Note that the weight sensors are identified by _ID_ and _Unit_
while the other sensors are identified by _idx_ in _BS440domoticz.ini_.

![domoticz](https://raw.githubusercontent.com/Tristan79/BS440/master/BS440domoticz.png)

**BS440google**

maintainer: managementboy / Keptenkurk

BS440google updates weight and fat parameters in Google fit (http://fit.google.com)
For creating an account and authentication file please see the Wiki for this
repository.(https://github.com/keptenkurk/BS440/wiki/How-to-use-Google-Fit)

**BS440runalizel**

maintainer: jovandeginste
This plugin stores data to local Runalyze database. Runalyze is a performance analyzer for atlethes which goes far beyond the performance trackers like runkeeper and runtastic. 

# Thanks to
* Christopher Peplin - maintainer of Pygatt
* Tristan79 - Domoticz plugin
* DjZU - CSV plugin
* managementboy - Google plugin
* jovandeginste - Runalyze plugin
* jinnerbichler - MQTT plugin
* qistoph - InfluxDB plugin and MQTT plugin
* Raudi, Remb0, Edmundo

# Disclaimer
This software is built out of personal interest and not related to
Medisana AG in any way.
