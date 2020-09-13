# ESP32 alarm code

This directory contains the sunrise alarm clock code for the ESP32. The language used is Micropython - see https://micropython.org/ for more information about the language and information how to flash the chip.

### The circuit

The driver circuit is very simple - DS3231 module is connected to the power source and to pins 4 and 16 of the ESP32 (these pins are used for setting and getting the time). Pins 17, 18, 19, 21, 22, 25, 26 and 33 (all of them have pulse with modulation capabilities) are each connected to a small 3.3V LED with a resistor.  All of the LEDs use a common ground. In the future, I'd like to use a stronger LED instead of multiple smaller ones, however, I am still exploring how to correctly drive a more powerful LED.

### Running

Firstly, `wifi.txt` needs to be modified - change the file to contain WI-FI login information. You may also want to modify `time.txt` to change the default alarm time. It may also be necessary to modify the MQTT information in `main.py` (such as server IP address).

Then upload `ds3231.py`, `main.py`, `time.txt` and `wifi.txt` to the board using your preferred method. I personally recommend using adafruit-ampy - `ampy -p /dev/ttyUSB0 put ds3231.py main.py time.txt wifi.txt`.

### How it works

The board first connects to the WI-FI and sets up a connection to the local MQTT server and starts infinitely looping - every second, LED intensity is updated and the MQTT connection is checked every minute for incoming messages. The intensity is calculated based on the remaining time until the set alarm in a linear fashion. To make the light a bit more pleasant, the intensity grows more slowly in the initial part of the process and starts growing faster later on. The intensity (duty) is based on the following graph:

<p align="center">
  <img src="intensity.png"/>
</p>

