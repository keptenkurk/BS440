# BS440
Python code to talk to Medisana BS440 bluetooth enabled bathroom scale
User managementboy reports succes with the Medisana BS444 too.

# Blog info
https://keptenkurk.wordpress.com/2016/02/07/connecting-the-medisana-bs440-bluetooth-scale/

# Prequisits
* Installed Pygatt 3.0.0 release
* Installed BLE adapter

# Tested on
* Raspberry Pi B+ (Linux raspberrypi 4.1.13+ #826 
  PREEMPT Fri Nov 13 20:13:22 GMT 2015 armv6l GNU/Linux).
  
# Tested scales
* Medisana BS440
* Medisana BS444

# Description
BS440 listens for information from a BS440 or compatible bluetooth scale. 
When received, it passes the information, depending on which option are enabled in the
file _BS440.ini_, to the following possibilities: 

* Mail the last 3 stored sets of data to the user
* Update virtual sensors in [Domoticz](www.domoticz.com) smarthome controller
* Update weight and fat parameters in Google fit (http://fit.google.com)
  For creating an account and authentication file please see the Wiki for this
  repository.(https://github.com/keptenkurk/BS440/wiki/How-to-use-Google-Fit)

# Preferences
Before using this app, personalize your settings in the file _BS440.ini_.

# Domoticz
Just uncomment the following two lines in the _BS440.ini_ and fill in the right url! 
Then run it, the sensors will be automatically generated. That easy!

```
[Domoticz]
domoticz_url: 127.0.0.1:8080
```

The optional option _hardware_name_ is the name of the dummy hardware to you can use,
if you leave it empty or commented it out, it uses _Medisana_ as default.

After a first run _BS440domoticz.ini_ is generated. In which you can override
the ids to use (if necessary). Note that the weight sensors are identified by _ID_ and _Unit_
while the other sensors are identified by _idx_ in _BS440domoticz.ini_.

![domoticz](https://raw.githubusercontent.com/Tristan79/BS440/master/BS440domoticz.png)

# Runalyze
Uncomment the following lines in the _BS440.ini_ and fill in your MySQL-Settings as you used for your Runalyze installation:

```
[RunalyzeLocal]
host: localhost
user: root
passwd: insert_your_password_here
db: runalyze
```

# Disclaimer
This software is build out of personal interest and not related to 
Medisana AG in any way.
