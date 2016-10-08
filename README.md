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

# Description
In it's current state this program listens for data from a BS440 
bluetooth scale. Once connected, data is read from the scale. Depending
on the config in ini the program will then
* mail the last 3 stored sets of data to the user and/or
* update a virtual sensor in Domoticz home automation system and/or
* update weight and fat parameters in Google fit (http://fit.google.com)
  For creating an account and authentication file please see the Wiki for this
  repository.(https://github.com/keptenkurk/BS440/wiki/How-to-use-Google-Fit)

# ini file
Before using this program personalize the settings in the ini file

# Disclaimer
This software is build out of personal interest and not related to 
Medisana AG in any way.
