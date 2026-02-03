# Home Assistant Integration: FF-Agent Connector

**FF-Agent Connector** ist eine benutzerdefinierte Integration für [Home Assistant](https://www.home-assistant.io/), die es ermöglicht, Alarme und Statusinformationen aus der App [FF-Agent](https://www.ff-agent.com/) in Home Assistant zu empfangen und weiterzuverarbeiten – z. B. für Automation, Dashboard-Anzeigen oder Benachrichtigungen.

> ⚠️ Hinweis: Diese Integration befindet sich aktuell in der Entwicklung. Feedback und Pull-Requests sind willkommen!

---

## 🔥 Funktionen

- Empfangen von Alarmierungen aus FF-Agent
- Anzeige von Einsatzdetails in Home Assistant Dashboards
- Automationen bei neuen Alarmen auslösen (z. B. Licht einschalten, Sirene aktivieren)
- Speicherung von Einsatzdaten als Verlauf / Statistik

---

## 🛠️ Installation (über HACS)

1. Stelle sicher, dass [HACS](https://hacs.xyz/) in deinem Home Assistant installiert ist.
2. Öffne HACS → **Integrationen** → Menü (oben rechts) → **Benutzerdefiniertes Repository hinzufügen**.
3. Gib folgendes GitHub-Repository ein: [https://github.com/KoblerS/ff-agent-hacs](https://github.com/KoblerS/ff-agent-hacs) wähle als Typ: **Integration**
4. Suche nach "FF-Agent Connector" und installiere die Integration.
5. Starte Home Assistant neu.

---

## ⚙️ Konfiguration

Nach der Installation kannst du die Integration über die Benutzeroberfläche hinzufügen:

1. Gehe zu **Einstellungen** → **Geräte & Dienste** → **Integration hinzufügen**.
2. Suche nach „FF-Agent Connector“ und folge den Einrichtungsschritten.

## Bekannte Probleme

- **Push Token:** Da diese Integration keinen gültigen Firebase Push-Token erzeugt, kann es vorkommen, dass E-Mails über fehlerhafte Push-Nachrichten generiert werden. Dieses Verhalten ist bekannt und lässt sich ohne die direkte Registrierung neuer Push-Tokens in Firebase derzeit nicht vermeiden.

## ℹ️ Disclaimer

Diese Home Assistant Integration wurde unabhängig entwickelt und steht in keinerlei Verbindung zu FF-Agent oder deren Entwicklern.
Alle Marken, Namen, Logos und Inhalte der App FF-Agent sind Eigentum der jeweiligen Rechteinhaber.
Diese Integration dient ausschließlich der technischen Erweiterung im Open-Source-Kontext und wird ohne kommerziellen Hintergrund bereitgestellt.
Für Support oder Fragen zur FF-Agent-App wende dich bitte direkt an den offiziellen Anbieter.

## 📄 Lizenz

Dieses Projekt steht unter der MIT License.

## 🤝 Mitwirken

Beiträge, Bug-Reports und Feature-Wünsche sind herzlich willkommen!
Erstelle gerne ein Issue oder sende einen Pull Request.