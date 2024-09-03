# Kiosk

<div align="center">
    <img src="/assets/logo.png" alt="Logo" width="250" height="250">
</div>

Kiosk is a small software project that is intended to be a cash register system for a vending machine. Using a Raspberry Pi, an NFC reader and a lock, any fridge or cabinet can be transformed into a small vending machine for friends and colleagues.

## 📋 Table of Contents

- [🚀 Quick Start](#quick-start)
- [✨ Features](#features)
- [🛠️ Service](#service)
- [🔧 Components](#components)
- [📐 3D-Model](#3d-model)
- [🤝 Contributing](#contributing)

## 🚀 Quick Start

Kiosk is a Python application and used [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) as UI. I used [poetry](https://github.com/python-poetry/poetry) as dependency manager. To start the application you can simply call a `poetry install` and then a `poetry run python3 src/main`.py.

Normally the logging of the application is set to `INFO`, but if something should fail at startup or during runtime, the logging can be set a little more finely in the log manager. To do this, the corresponding code must be adjusted in the [logmgr.py: Line 19](https://github.com/morzan1001/Kiosk/blob/main/src/logmgr/logmgr.py#L19).

⚠️ **Important!**

Both the library for controlling the GPIO pins ([gpiod](https://pypi.org/project/gpiod/)) and the library for the pn532 NFC chip ([pn532lib](https://github.com/Liam-Deacon/py532lib))can only be used on a raspberry pi. so if you want to develop on another system, the corresponding parts of the software must be commented out or bypassed in some other way.

## ✨ Features

The kiosk is intended to be a small application to simplify the use of a communal refrigerator or other goods cupboard for a group of people.

<div align="center">
    <img src="/assets/login_screen.png" alt="Login" height="250">
    <img src="/assets/card_screen.png>" alt="Shopping Card" height="250"> 
</div>
<br/>

Each user is stored with an NFC ID. You can either use your own cards or dongles or use existing access cards or similar. A user can then select products using a barcode scanner and the costs are deducted from their (internal) account.

<div align="center">
    <img src="/assets/admin_screen.png" alt="Admin" height="250">
    <img src="/assets/product_screen.png>" alt="Product" height="250"> 
</div>
<br/>

An admin can manage the stock and users and, of course, buy something themselves.

### Future plans

Here are a few ideas on how to expand the software:

- 🎵 Play sounds on successful or unsuccessful checkout
- 📊 More precise evaluation of the purchasing behavior of individual persons
- 📧 E-mail notifications for admins when product stock is low or for users when credit is low.
- ...

## 🛠️ Service

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

I have stored this file under `/etc/systemd/system/`. As soon as the graphical user interface of Raspberry Pi OS has finished loading, the kiosk application starts.

## 🔧 Components

I used the following components for my setup:

- [Raspberry Pi 5](https://www.raspberrypi.com/products/raspberry-pi-5/) (In terms of performance, much older models also work, but the USB ports in the case may no longer fit well.)
- [Display](https://www.raspberrypi.com/products/raspberry-pi-touch-display/)
- [Display Cable](https://www.amazon.de/dp/B0CT5PZNRV?ref=ppx_yo2ov_dt_b_fed_asin_title) (Only needed when using a Pi 5)
- [PN532 NFC reader](https://www.berrybase.de/pn532-nfc-und-rfid-modul-inkl.-karte-dongle)
- [5V relay](https://www.berrybase.de/5v-1-kanal-relais-modul-mit-definierbarem-schaltsignal-high/low)
- [Lock](https://www.amazon.de/dp/B07MWBHQNM?ref=ppx_yo2ov_dt_b_fed_asin_title)
- [Barcode scanner](https://www.amazon.de/Tera-Kabelloser-Handheld-Barcode-Scanner-Akkustandsanzeige-Ergonomischem/dp/B078SQ91FB) (The barcode scanner is not absolutely necessary, if you want to use the barcode function, any USB barcode scanner will do.)

### 📐 3D-Model

<div align="center">
    <img src="/assets/3d_model.png" alt="3D-Model" width="250" height="250">
</div>

I myself use an official Raspberry Pi display. The resolution of the software is adapted to this. In the folder [3D model](https://github.com/morzan1001/Kiosk/tree/main/3d_model) you will find a model that offers space for a Pi as well as the display, an NFC reader and a 5V relay.

## 🤝 Contributing

Contribution are very welcome, my software is not perfect and I am happy about everyone who wants to contribute something.
