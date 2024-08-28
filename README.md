# Kiosk

![Logo](/assets/logo.png png =250x250)

Kiosk is a small software project that is intended to be a cash register system for a vending machine. Using a Raspberry Pi, an NFC reader and a lock, any fridge or cabinet can be transformed into a small vending machine for friends and colleagues.

## Table of Contents

- [Quick Start](#quick-start)
- [Service](#service)
- [Components](#components)
- [3D-Model](#3d-model)
- [Contributing](#contributing)

## Quick Start

Kiosk is a Python application and used [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) as UI. I used [poetry](https://github.com/python-poetry/poetry) as dependency manager. To start the application you can simply call a `poetry install` and then a `poetry run python3 src/main`.py.

Normally the logging of the application is set to `INFO`, but if something should fail at startup or during runtime, the logging can be set a little more finely in the log manager. To do this, the corresponding code must be adjusted in the [logmgr.py: Line 19](https://github.com/<user>/<repo>/blob/<branch>/Projekte/Kiosk/src/logmgr/logmgr.py#L19). 

⚠️ **Important!**

Both the library for controlling the GPIO pins ([gpiod](https://pypi.org/project/gpiod/)) and the library for the pn532 NFC chip ([pn532lib](https://github.com/Liam-Deacon/py532lib))can only be used on a raspberry pi. so if you want to develop on another system, the corresponding parts of the software must be commented out or bypassed in some other way.

## Service

I use a service so that the kiosk software starts every time the Pi is started. My configuration looks like this:

```ini
[Unit]
Description=Kiosk
After=graphical.target

[Service]
ExecStart=/home/<user>/.local/bin/poetry run python3 /home/<user>/Kiosk/src/main.py
WorkingDirectory=/home/<user>/Kiosk
User=<user>
Environment=DISPLAY=:0
Restart=always

[Install]
WantedBy=graphical.target
```

I have stored this file under `/etc/systemd/system/`. As soon as the graphical user interface of Raspberry Pi OS has finished loading, my kiosk application starts.

## Components

I used the following components for my setup and my model:

- [Raspberry Pi 5](https://www.raspberrypi.com/products/raspberry-pi-5/) (In terms of performance, much older models also work, but the USB ports in the case may no longer fit well.)
- [Display](https://www.raspberrypi.com/products/raspberry-pi-touch-display/)
- [Display Cable](https://www.amazon.de/dp/B0CT5PZNRV?ref=ppx_yo2ov_dt_b_fed_asin_title) (Only needed when using a Pi 5)
- [PN532 NFC reader](https://www.berrybase.de/pn532-nfc-und-rfid-modul-inkl.-karte-dongle)
- [5V relay](https://www.berrybase.de/5v-1-kanal-relais-modul-mit-definierbarem-schaltsignal-high/low)
- [Lock](https://www.amazon.de/dp/B07MWBHQNM?ref=ppx_yo2ov_dt_b_fed_asin_title)

### 3D-Model

![3D-Model](/assets/3d_model.png)

I myself use an official Raspberry Pi display. The resolution of the software is adapted to this. In the Order 3D model you will find a model that offers space for a PI as well as the display, an NFC reader and a 5V relay.

## Contributing

Contribution are very welcome, my software is not perfect and I am happy about everyone who wants to contribute something.
