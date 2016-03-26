# BS440
Python code to talk to Medisana BS440 bluetooth enabled bathroom scale

# Blog info
https://keptenkurk.wordpress.com/2016/02/07/connecting-the-medisana-bs440-bluetooth-scale/

# Prequisits
* Installed Pygatt
* Installed BLE adapter

# Tested on
* Raspberry Pi B+ (Linux raspberrypi 4.1.13+ #826 
  PREEMPT Fri Nov 13 20:13:22 GMT 2015 armv6l GNU/Linux).

# Description
In it's current state this program listens for data from a BS440 
bluetooth scale. Once connected, data is read from the scale and
the last 3 stored sets of data will be mailed to the user.

# ini file
Before using this program change the settings in the ini file

# Future
WIP is storing data into a database and graphing them in a web page

# Disclaimer
This software is build out of personal interest and not related to 
Medisana AG in any way.
