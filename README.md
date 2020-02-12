# BS440  v2.0.0
Python code to talk to Medisana BS440 bluetooth enabled bathroom scale
User managementboy reports succes with the Medisana BS444 too.

# Blog info
https://keptenkurk.wordpress.com/2016/02/07/connecting-the-medisana-bs440-bluetooth-scale/
with a full step-by-step installation instruction on
https://keptenkurk.wordpress.com/2017/03/05/connecting-the-medisana-bs440-bluetooth-scale-epilogue/

# Prerequisites
* Installed Pygatt >= 3.0.0 release
  WARNING: Pygatt 3.1.1 has been reported to work but Pygatt 3.2 fails to show all characteristics (26-1-2018)
* Installed BLE adapter
* Installed Bluez

# Tested on:

* Raspberry Pi B+ running latest Jessie
	4.4.38+ #938
	Thu Dec 15 15:17:54 GMT 2016 armv6l GNU/Linux)
* USB bluetooth adapter:
	USB device found, idVendor=0a5c, idProduct=21e8
	USB device strings: Mfr=1, Product=2, SerialNumber=3
	Product: BCM20702A0
* Bluez
  - 5.44 (from source)
  - 5.23-2+rpi2 (from package manager)
* Pygatt 3.0.0 installed


* Raspberry Pi Zero W running DietPi V153
	4.9.35+ #1
	Tue Jul 4 17:16:26 UTC 2017 armv6l GNU/Linux
* onboard bluetooth adapter
* Bluez
  - 5.23-2+rpi2 (from package manager)
* Pygatt 3.0.0 installed

# Description
BS440 listens for information from a Medisana BS410/BS430/BS440/BS444 or compatible bluetooth
scale. When received, it passes the information to all found data processors found in
the plugin folder.

# Preferences
Before using this app, copy `BS440.example.ini` to `BS440.ini` and personalize your settings.
This file contains the general parameters for communicating with the scale, and which plugins to use.

# Automatically start

Copy the right files from the `dist/init` directory.

For generic linux with SystemD support:

```bash
cp dist/init/linux-systemd/bs440.service /etc/systemd/system/
systemctl daemon-reload   # tell SystemD to detect new service files
systemctl start bs440     # start the service now
systemctl enable bs440    # start the service at boot
journalctl -l -f -u bs440 # show + tail the logs of bs440
```

Attention: the systemd service file assumes you copied the contents of this repo to `/opt/BS440`

# Plugins
Currenly these plugins are available:
* BS440mail: Mail the last 3 stored sets of data to the user
* BS440csv: Store results locally in csv and graph results through webserver
* BS440domoticz: Store data in virtual sensors of Domoticz home control system
* BS440google: Store data to Google Fit account
* BS440runalizel: Store data to local Runalyze database
* BS440mqtt: Send collected data via MQTT to Home Assistant for excample
* BS440influxdb: Store collected data into InfluxDB time series database for easy graphing using Grafana

Plugins are found in the plugin folder and named BS440pluginname.py. Each plugin uses
its private .ini file named BS440pluginname.ini
To enable a plugin, add it to the `plugins` key in `BS440.ini`.

Directions on how to install prerequisites, configure and use a specific plugin is found
in the Wiki

## BS440mail
Maintainer: Keptenkurk

Last 3 results are mailed to the user mail adress as configured in BS440mail.ini

## BS440csv
Maintainer: DjZU

Data is added to a local CSV file. Data is presented by running plotBS440.py which
starts a webserver and serves graphs to the user.
You can use any web server to serve a static site based on the `csv` files. You can find a
working example using the Caddy webserver in [dist/caddy/](dist/caddy/).

## BS440mqtt
Maintainer: jinnerbichler

Send collected data via MQTT (e.g. to Home Assistant)

## BS440influxdb
Maintainer: qistoph

Store collected data in InlfuxDB (e.g. for Grafana)

## Domoticz
Maintainer: Tristan79 - Status: Testing

Configure the Domoticz and user details in BS440domoticz.ini.
When data is received, the sensors will be automatically generated. That easy!

The optional option _hardware_name_ is the name of the dummy hardware to you can use,
if you leave it empty or commented it out, it uses _Medisana_ as default.

After a first run _BS440domoticz.ini_ is updated. In which you can override
the ids to use (if necessary). Note that the weight sensors are identified by _ID_ and _Unit_
while the other sensors are identified by _idx_ in _BS440domoticz.ini_.

![domoticz](https://raw.githubusercontent.com/Tristan79/BS440/master/BS440domoticz.png)

## BS440google
maintainer: managementboy / Keptenkurk

BS440google updates weight and fat parameters in Google fit (http://fit.google.com)
For creating an account and authentication file please see the Wiki for this
repository.(https://github.com/keptenkurk/BS440/wiki/How-to-use-Google-Fit)

## BS440runalizel
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
