# Rusty – Discord Bot

Rusty ist ein KI-gestützter Discord-Bot mit einer ausgeprägten Persönlichkeit,
entwickelt und betrieben als privates Heimprojekt.

## Über das Projekt

Rusty wurde mit dem Ziel entwickelt, Serverinteraktionen lebendiger und
unterhaltsamer zu gestalten. Anstatt auf generische Bot-Antworten zu setzen,
verfügt Rusty über einen klar definierten Charakter – frech, direkt und loyal
gegenüber seinem Betreiber. Technisch basiert er auf der Google Gemini API
und läuft als dauerhafter Dienst auf einem selbstgehosteten Server.

## Wie zu nutzen?

Im Code könnt ihr wo xxx steht euren eigenen Namen eintragen sodas der Bot auch Richtig antwortet.
In der env Datei müsst ihr euren Discord Token, Gemini API und Discord ID eingeben

## Technischer Überblick

| Komponente        | Details                  |
|-------------------|--------------------------|
| Sprache           | Python                   |
| KI-Backend        | Google Gemini API        |
| Hosting           | Selbstgehostet           |
| Prozessverwaltung | systemd                  |
| Plattform         | Discord                  |

## Momentane Hardware für den Betrieb

| Komponente        |
|-------------------|
| 8 GB DDR 3 RAM    |
| N3350 Celeron®    |
| 32 GB SSD         |
| 250 MBit/s LAN    |

## Minimale Hardware

| Komponent  | Minimum              |
|------------|----------------------|
| CPU        | Single-core ~500 MHz |
| RAM        | 128 MB               |
| Speicher   | 50mb bis 5GB         |
| Verbindung | ~1 Mbit/s            |
| Python     | 3.10+                |
| OS         | Jedes Linux terminal |

## Features

KI-Antworten via Gemini 2.5 Flash Lite
Whitelist-System – nur freigeschaltete User können /ask nutzen
Nutzungsstatistiken mit Top-User-Rangliste
System-Infos (CPU, RAM, GPU, Uptime)
Logging – jede Frage & Antwort wird pro User gespeichert

## Commands

| Command | Beschreibung                  | Zugang|
|---------|-------------------------------|-----------|
| /ask    |Stelle Rusty eine Frage        | Whitelist |
| /ping   |Zeigt den aktuellen Ping       | Alle      |
| /uptime |Wie lange Rusty schon läuft    | Owner     |
| /info   |System-Infos des Servers       | Owner     |
| /stats  |Nutzungsstatistiken & Top-User | Owner     |
