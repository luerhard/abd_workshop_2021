# Installation

## Python environment

Benötigt wird eine Conda Installation.
Hierbei kann entweder [Anaconda](https://docs.anaconda.com/anaconda/install/index.html) oder [Miniconda](https://docs.conda.io/en/latest/miniconda.html) installiert werden.

Anschließend ist das Skript `install.py` in diesem Ordner auszuführen.

```bash
python3 install.py
```

Dieses installiert ein conda environment mit dem Namen `abd_workshop_2021`.

## Zugang zu den Beispieldaten für diesen Workshop

Die Daten, die im Verlauf dieses Workshops verwendet werden, können [hier](https://bwsyncandshare.kit.edu/s/jamD6Z3R82F8Tt6) heruntergeladen werden.
Da wir eine unterschriebene Datenschutzerklärung benötigen, um diese Daten zu teilen, ist dieser Ordner passwortgeschützt.
Um das Passwort zu erhalten, unterschreiben Sie bitte die Datenschutzerklärung, die Sie per Mail erhalten haben und senden diese an Saïd Unger.

Nach Erhalt der Daten, entpacken Sie diese bitte in den `data/` Ordner des Repos.

## Zugang zur KB Datenbank

Falls Sie einen Zugang zur Datenbank des Kompentenzzentrum Bibliometrie haben, finden Sie hier eine Anleitung zum Aufbauen einer Verbindung.

Die Python-Libraries, die dazu notwendig sind, werden mit dem conda-environment mitinstalliert -- dennoch ist der Oracle Libraries nötig (z.B. im [Oracle Instant Client](https://www.oracle.com/database/technologies/instant-client.html) enthalten), damit die Verbindung funkioniert. Installationsanweisungen für alle gängigen Plattformen finden sie [in der Dokumentation](https://cx-oracle.readthedocs.io/en/latest/user_guide/installation.html). Für Windows-Nutzer gibt es [hier einen Stackoverflow Artikel](https://stackoverflow.com/questions/56119490/cx-oracle-error-dpi-1047-cannot-locate-a-64-bit-oracle-client-library) mit Tipps zur Installation.

Um eine Verbindung zur Datenbank aufzubauen, muss eine Datei mit dem Namen `config.ini` erstellt werden, in der die persönlichen Zugangsdaten zur Datenbank enthalten sind.
Diese Datei muss nach dem Schema in `config[EXAMPLE].ini` aufgebaut sein und im selben Ordner liegen.

Man kann diese Datei kopieren und im Inhalt `mypassword` und `myusername` durch den entsprechenden Zugang ersetzen.

```
[fizDB]
password = mypassword
username = myusername
schema = WOS_B_2020
```

`config.ini` ist dabei in der `.gitignore` enthalten, sodass die Zugangsdaten nicht auf github veröffentlicht werden.


# abd_workshop_2021
