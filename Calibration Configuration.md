<table>
  <tr>
    <th colspan="2"><img  src="P:\Technology\Raspberry Pi Files\scripts\Morgan-Solar-Logo1.png" alt="Morgan Solar Inc"></th>
    <th colspan="3"><font size="4">Title: DAQ Calibration and configuration</big></th>
  </tr>
  <tr>
    <td>Author: Renan Pedrosa</td>
    <td>Doc. Type: TUT</td>
    <td>Date: Aug 22, 2018</td>
    <td>Doc. No:</td>
    <td>Rev.: 0A</td>
  </tr>
</table>


## Revisions

| REV | Issue Date  | Description | Originator |
|:-:| :--: | :--: | :--: |
| 0A | Aug 22, 2018 | Initial drafting | Renan Pedrosa |

## Motivation
This tutorial is for setting up I2C and the DAQ calibration program. It is necessary to have covered all the necessary steps for properly setting up the CAN-Bus communications, 

## Hardware needed

- Raspberry Pi 2 Model B
- MSI CANPI v0.1 Daughter Board
- MSI calibration hat

## Software Version
- [cat /etc/os-release] Raspbian GNU/Linux 7 (wheezy)
- [uname -a] Linux raspberrypi 4.1.19-v7+ #858 SMP Tue Mar 15 15:56:00 GMT 2016 armv7l GNU/Linux

## Instructions
#### 1. Before starting
This manual contains
#### 1. Update system
```bash
sudo apt-get update
```
```bash
sudo apt-get install python-smbus
sudo apt-get install i2c-tools
```
#### 2. Enable I2C
Launch raspi-config
```bash
sudo raspi-config
```
Now go to Advanced Options >> I2C, enable I2C and set to load the linux kernel for I2C by default.

#### 3. Configure I2C for boot
1) Open /boot/config.txt with:
```
sudo nano /boot/config.txt
```
Find this:
```
#device_tree_param=i2c_arm=on
```
And uncomment it (remove the # in front of this line).

2) Open /boot/cmdline.txt with:
```
sudo nano /boot/cmdline.txt
```
And at the end of the file add this:
```
bcm2708.vc_i2c_override=1
```
3) Open /etc/modules with:
```bash
sudo nano /etc/modules
```
And add this at the end:
```bash
i2c-bcm2708
i2c-dev
```
Turn off your Pi2, connect your I2C device, turn on your Pi2 and run this:
```bash
sudo i2cdetect -y 1
```
If the configuration was successfull, both DAC's should show up at addresses 0x60 and 0x61.

#### 4. Add user 'pi' to i2c group
Run this command, so that the user pi have access to the i2c bus.
```bash
sudo adduser pi i2c
```

#### 4. Configure GPIO
Install python-dev
```bash
sudo apt-get install python-dev
```
then install Python GPIO
```bash
sudo apt-get install rpi.gpio

sudo apt-get install python-rpi.gpio
```

#### 5. Installing Adafruit library
```bash
sudo apt-get install git build-essential python-dev
cd ~
git clone https://github.com/adafruit/Adafruit_Python_MCP4725.git
cd Adafruit_Python_MCP4725
sudo python setup.py install
```
#### 6. Installing Adafruit PureIO
```bash
cd ~
git clone https://github.com/adafruit/Adafruit_Python_PureIO.git
cd Adafruit_Python_PureIO
sudo python setup.py install

```



Sources:
[1] http://www.runeaudio.com/forum/how-to-enable-i2c-t1287.html
[2] https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-gpio
[3] https://github.com/adafruit/Adafruit_Python_MCP4725
[4] https://www.bggofurther.com/2015/01/create-an-interactive-command-line-menu-using-python/
