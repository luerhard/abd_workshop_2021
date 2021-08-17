# Installation

## Python environment

Benötigt wird eine Conda Installation. 
Hierbei kann entweder [Anaconda](https://docs.anaconda.com/anaconda/install/index.html) oder [Miniconda](https://docs.conda.io/en/latest/miniconda.html) installiert werden.

Anschließend ist das Skript `install.py` in diesem Ordner auszuführen.

```bash
python3 install.py
```

Dieses installiert ein conda environment mit dem Namen `abd_workshop_2021`.

## Zugang zur Datenbank

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
