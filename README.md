# KStickFix 1.1

KStickFix ist ein grafisches Linux-Werkzeug zum Analysieren und Wiederherstellen von USB-Sticks.

Diese Version ist eine saubere Basisversion ohne eigenen ISO-Schreiber. Für ISO-Dateien startet KStickFix ein bewährtes externes Werkzeug und zeigt klar an, welche ISO und welcher USB-Stick dort ausgewählt werden sollen.

## Funktionen

- USB-Sticks erkennen
- USB-Sticks analysieren
- USB-Sticks wiederherstellen
- exFAT, FAT32, NTFS und ext4
- MBR und GPT
- externe ISO-Schreiber starten
- Warnung, wenn der Stick kleiner als die ISO ist
- Warnung, wenn der Stick eingehängt ist
- Auswahl zurücksetzen
- Diagnose
- Systemprüfung

## ISO-Schreiben

KStickFix schreibt ISO-Dateien nicht selbst. Stattdessen startet KStickFix ein vorhandenes Linux-Werkzeug:

- KDE ISO Image Writer
- SUSE Studio Imagewriter
- GNOME Laufwerke

KStickFix zeigt vorher deutlich an, welche ISO-Datei und welcher USB-Stick im externen Programm gewählt werden sollen.

## openSUSE Pakete

```bash
sudo zypper install python3 python3-pyside6 util-linux parted exfatprogs dosfstools ntfs-3g e2fsprogs udisks2 polkit imagewriter
```

## Starten

```bash
./start.sh
```

oder:

```bash
python3 src/main.py
```

## KDE-Menü-Installation

```bash
./INSTALLIEREN.sh
```

## Autor

Christian Wolf  
E-Mail: christianwolf5@gmx.net

Entwicklungspartner und technische Unterstützung: OpenAI ChatGPT

## Lizenz

MIT License
