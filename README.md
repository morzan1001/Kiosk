# Kiosk

<div align="center">
    <img src="/assets/logo.png" alt="Logo" width="250" height="250">
</div>

Kiosk is a small software project that is intended to be a cash register system for a vending machine. Using a Raspberry Pi, an NFC reader and a lock, any fridge or cabinet can be transformed into a small vending machine for friends and colleagues.

## 📋 Table of Contents

- [🚀 Quick Start](#quick-start)
- [✨ Features](#features)
- [🛠️ Service](#service)
- [🏢 Database](#database)
- [💾 Backup](#backup)
- [🔧 Components](#components)
- [🤝 Contributing](#contributing)

## 🚀 Quick Start
<a name="quick-start"></a>

Kiosk is a Python application and uses [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) as UI. I used [poetry](https://github.com/python-poetry/poetry) as a dependency manager. To start the application you can simply run `poetry install` and then `poetry run python3 src/main.py`.

Normally the logging of the application is set to `INFO`, but if something should fail at startup or during runtime, the logging can be set a little more finely. To do this, just change the loglevel in [config.json](https://github.com/morzan1001/Kiosk/blob/main/config_example.json).

In order for the application to start, the [config_example.json](https://github.com/morzan1001/Kiosk/blob/main/config_example.json) must be renamed to `config.json`, it is not absolutely necessary to specify a mailserver, so the program should also start with the values from the [config_example.json](https://github.com/morzan1001/Kiosk/blob/main/config_example.json). However, any adjustments can of course be made here. 

⚠️ **Important!**

Both the library for controlling the GPIO pins ([gpiod](https://pypi.org/project/gpiod/)) and the library for the pn532 NFC chip ([pn532lib](https://github.com/Liam-Deacon/py532lib)) can only be used on a raspberry pi. If you want to develop on another system, the corresponding parts of the software must be commented out or bypassed in some other way.

## ✨ Features
<a name="features"></a>

The kiosk is intended to be a small application to simplify the use of a communal refrigerator or other goods cupboard for a group of people.

<div align="middle">
    <img src="/assets/login_screen.png" alt="Login" height="200">
    <img src="/assets/card_screen.png" alt="Shopping Card" height="200"> 
</div>
<br/>

Each user is stored with an NFC ID. You can either use your own cards or dongles or use existing access cards or similar. A user can then select products using a barcode scanner and the costs are deducted from their (internal) account.

<div align="middle">
    <img src="/assets/admin_screen.png" alt="Admin" height="200">
    <img src="/assets/product_screen.png" alt="Product" height="200"> 
</div>
<br/>

An admin can manage the stock and users and, of course, buy something themselves.

### Future plans

Here are a few ideas on how to expand the software:

- 🎵 Play sounds on successful or unsuccessful checkout (✅)
- 📊 More precise evaluation of the purchasing behavior of individual persons
- 📧 E-mail notifications for admins when product stock is low or for users when credit is low. (✅)
- ...

### 🎵 Sounds

As no gag I have implemented that the kiosk can play sounds when a product is purchased or when a purchase fails. For this purpose, sound files can be specified in two folders. Once positive sounds and once negative sounds. the whole thing can be switched on and off in [config.json](https://github.com/morzan1001/Kiosk/blob/main/config_example.json#L37).

### 📧 E-Mail

The kiosk can notify users when their account balance gets low, or administrators when a product stock is running low. In addition, the kiosk can send monthly statistics to users about their purchasing behavior. A corresponding SMTP server can be configured in [config.json](https://github.com/morzan1001/Kiosk/blob/main/config_example.json#L15). If a user does not have a stored e-mail address in the database, he simply does not receive any e-mails, the field is not mandatory.

### 🎺 Mattermost

the kiosk can also notify users via a mattermost bot account. On the one hand, standard messages such as “low account balance” or for admins “low stock” are possible. On the other hand, short-term marketing messages can also be sent. The idea is that the kiosk regularly evaluates which users have bought little, on this basis individual users are offered a discount via mattermost that is valid for a certain time. the entire mattermost integration can be configured in [config.json](https://github.com/morzan1001/Kiosk/blob/main/config_example.json#L21).

## 🛠️ Service
<a name="service"></a>

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

## 🏢 Database
<a name="database"></a>

Thanks to [sqlalchemy](https://www.sqlalchemy.org/), Kiosk gives you the freedom to choose which database you want to use. I started using a [sqlite](https://sqlite.org/) database, but have since switched to a [postgresql](https://www.postgresql.org/) database. In the [config.json](https://github.com/morzan1001/Kiosk/blob/main/config_example.json) you can select which database you want to use. [pgloader](https://pgloader.io/) can be used to perform a migration from sqlite to postgres. however, it is advisable to perform an alembic migration afterwards so that all settings (such as `autoincrement`) are also adopted. 

```bash
pgloader sqlite://src/database/kiosk.db  postgresql://kiosk:your_password_here@localhost/kiosk
```

If you decide to use a [postgresql](https://www.postgresql.org/) database, it might also be worth taking a look at my [dashboard repository](https://github.com/morzan1001/Kiosk-Data-Frontend) for data analysis :grin:.

## 💾 Backup
<a name="backup"></a>

As i have already painfully discovered, it makes sense to back up the database. 

I provide a script under [utils/db_backup.sh](https://github.com/morzan1001/Kiosk/blob/main/utils/db_backup.sh) with the name db_backup.sh which can be used to create database backups. The script creates a directory, checks whether a sqlite or a postgres database is used and then executes the corresponding backup routine. 

I call the script via cronjob to create a backup every day.

```crontab
0 2 * * * /home/<user>/backup_script.sh >> /home/<user>/backup.log 2>&1
```

The script ensures that I always have backups of the last 7 days and can simply restore them if the worst comes to the worst. 

## 🔧 Components
<a name="components"></a>

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
    <img src="/assets/3d_model.png" alt="3D-Model" height="250">
</div>

I myself use an official Raspberry Pi display. The resolution of the software is adapted to this. In the folder [3D model](https://github.com/morzan1001/Kiosk/tree/main/3d_model) you will find a model that offers space for a Pi as well as the display, an NFC reader and a 5V relay.

## 🤝 Contributing
<a name="contributing"></a>

Contribution are very welcome, my software is not perfect and I am happy about everyone who wants to contribute something.

### Dev hints

I kept adding new features to this project and changing others. To make my life a little easier, especially with the database, I used [alembic](https://alembic.sqlalchemy.org/en/latest/). Alembic is not necessary to run the program or to develop for it but to make changes on an existing dataset it is great. 

To use alembic, `alembic init alembic` must be called once. This creates a directory with the name “alembic” in which the database revisions and configs are stored. In addition, an `alembic.ini` is placed in the root directory. In this ini, the database location can be specified as follows:

```ini
sqlalchemy.url = sqlite:///src/database/kiosk.db
```
or 
```ini
sqlalchemy.url = postgresql://kiosk:your_password_here@localhost:5432/kiosk
``` 

The `env.py` must also be adapted in the alembic directory. I have saved an example of what this `env.py` can look like under [assets](/assets/alembic_env_example.py). I think the alembic folder does not belong in the repo and therefore this file is located there separately. 

The following command can be used to create an Alembic revision: 

```bash
alembic revision --autogenerate -m "Sync existing schema"
```

And then to carry out the database migration: 

```bash
alembic upgrade head
```

By the way, if you've messed something up with your migrations, `alembic stamp head` is worth its weight in gold. :bowtie:
