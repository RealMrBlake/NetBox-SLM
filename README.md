# NetBox SLM

NetBox SLM erweitert NetBox um die Verwaltung von Softwareprodukten, Versionen, Installationen und Lizenzen.
Lizenzen können optional einer NetBox-Mandantengruppe und einem Mandanten zugeordnet werden.

Diese Variante ist für **NetBox 4.6.5** vorgesehen.

Die Oberfläche ist auf Englisch und Deutsch verfügbar. Die Sprache richtet sich nach der in NetBox für den
Benutzer ausgewählten Sprache.

## Funktionen

- Softwareprodukte und Hersteller verwalten
- Versionen, Release-Typen und Supportzeiträume erfassen
- Installationen Geräten, virtuellen Maschinen oder Clustern zuordnen
- Softwarelizenzen einschließlich Laufzeit, Umfang und Ablageort verwalten
- Lifetime-Lizenzen oder Erneuerungsintervalle in Tagen, Monaten oder Jahren erfassen
- Lizenzdateien, Lizenzschlüssel und Links zum Anbieterportal hinterlegen
- Ablaufwarnungen standardmäßig einen Monat und eine Woche vor Lizenzende
- Zusätzliche eigene Vorwarnzeit in Tagen, Wochen oder Monaten
- NetBox-Benachrichtigungen und optionaler E-Mail-Versand über die NetBox-SMTP-Konfiguration
- Lizenzen Mandantengruppen und Mandanten zuordnen
- Bedienung über die NetBox-Oberfläche und REST-API
- Filter, Bulk-Import und Bulk-Bearbeitung

> **Hinweis:** Lizenzschlüssel werden in der NetBox-Datenbank und Lizenzdateien im konfigurierten NetBox-
> Medienverzeichnis gespeichert. Der Zugriff auf Datenbank, REST-API und Medienverzeichnis sollte entsprechend
> geschützt und gesichert werden.

## Installation

NetBox installiert lokale Erweiterungen aus `/opt/netbox/local_requirements.txt`. Die Git-URL muss dort dauerhaft
eingetragen werden, damit das Plugin bei einem späteren NetBox-Upgrade erneut installiert wird.

### 1. Git-Repository als lokale Anforderung eintragen

```bash
echo "git+https://git.mrblake.cc/MrBlake/NetBox-SLM.git" >> /opt/netbox/local_requirements.txt
```

Vorher kann geprüft werden, ob der Eintrag bereits vorhanden ist:

```bash
grep -qxF "git+https://git.mrblake.cc/MrBlake/NetBox-SLM.git" /opt/netbox/local_requirements.txt || \
  echo "git+https://git.mrblake.cc/MrBlake/NetBox-SLM.git" >> /opt/netbox/local_requirements.txt
```

### 2. Plugin mit Pip installieren

Die Installation muss im Python-Virtual-Environment von NetBox erfolgen:

```bash
/opt/netbox/venv/bin/pip install --upgrade --force-reinstall \
  "git+https://git.mrblake.cc/MrBlake/NetBox-SLM.git"
```

Alternativ können alle lokalen Anforderungen installiert werden:

```bash
/opt/netbox/venv/bin/pip install -r /opt/netbox/local_requirements.txt
```

Die installierte Version kann anschließend geprüft werden:

```bash
/opt/netbox/venv/bin/pip show netbox-slm
```

Für diese Variante muss dort mindestens Version `1.12.0` stehen.

## Ablaufbenachrichtigungen

Für Lizenzen mit Ablaufdatum sind Benachrichtigungen standardmäßig aktiviert. Die Standardtermine liegen einen
Monat und eine Woche vor dem Ablaufdatum. Pro Lizenz kann zusätzlich eine eigene Vorwarnzeit festgelegt oder die
Standardtermine deaktiviert werden.

Empfänger entscheiden selbst, ob sie informiert werden: Vertrieb, zuständiger Techniker oder andere Benutzer öffnen
die Lizenz und wählen die NetBox-Aktion **Abonnieren**. Mit **Abonnement beenden** können sie die Meldungen wieder
abschalten. Ohne Abonnenten wird keine Nachricht versendet.

Die NetBox-Nachricht wird immer erzeugt. Wird an der Lizenz zusätzlich **E-Mail-Benachrichtigungen** aktiviert, sendet
das Plugin auch eine E-Mail an die im Benutzerkonto hinterlegte Adresse. Dafür muss der SMTP-Versand in NetBox
konfiguriert sein.

Die Aktivierung des E-Mail-Versands darf nur durch Administratoren oder Benutzer mit der Berechtigung
`netbox_slm.manage_softwarelicense_email_notifications` geändert werden. Die eigentlichen SMTP-Zugangsdaten werden
ausschließlich in der NetBox-Serverkonfiguration gepflegt und sind im Plugin nicht einsehbar.

Die Prüfung läuft einmal täglich als NetBox-Systemjob. Der NetBox-RQ-Worker muss daher mit Scheduler-Unterstützung
laufen; dies ist bei der regulären NetBox-Installation mit `rqworker` standardmäßig der Fall. Das interne
Versandprotokoll verhindert doppelte Nachrichten.

### 3. Plugin in NetBox aktivieren

In `/opt/netbox/netbox/netbox/configuration.py` ergänzen:

```python
PLUGINS = [
    "netbox_slm",
]
```

Falls bereits andere Plugins eingetragen sind, wird `"netbox_slm"` lediglich zur vorhandenen Liste hinzugefügt.
Eine zusätzliche `PLUGINS_CONFIG`-Konfiguration ist für den Standardbetrieb nicht erforderlich.

### 4. Datenbank migrieren und statische Dateien aktualisieren

```bash
cd /opt/netbox/netbox
/opt/netbox/venv/bin/python manage.py migrate
/opt/netbox/venv/bin/python manage.py collectstatic --no-input
```

### 5. NetBox-Dienste neu starten

Bei einer üblichen systemd-Installation:

```bash
sudo systemctl restart netbox netbox-rq
```

Je nach Installation können die Namen der Dienste abweichen.

## Aktualisierung

```bash
/opt/netbox/venv/bin/pip install --upgrade --force-reinstall \
  "git+https://git.mrblake.cc/MrBlake/NetBox-SLM.git"
cd /opt/netbox/netbox
/opt/netbox/venv/bin/python manage.py migrate
/opt/netbox/venv/bin/python manage.py collectstatic --no-input
sudo systemctl restart netbox netbox-rq
```

Der Eintrag in `/opt/netbox/local_requirements.txt` bleibt dabei bestehen.

## Deinstallation

1. `"netbox_slm"` aus der `PLUGINS`-Liste entfernen.
2. Die Git-Zeile aus `/opt/netbox/local_requirements.txt` entfernen.
3. Das Python-Paket deinstallieren:

```bash
/opt/netbox/venv/bin/pip uninstall netbox-slm
```

Die Plugin-Tabellen werden dabei nicht automatisch aus der Datenbank gelöscht.

## Ursprung und Lizenz

Dieses Repository basiert auf dem ursprünglichen Projekt
[ICTU/netbox_slm](https://github.com/ICTU/netbox_slm). **ICTU** ist der ursprüngliche Autor und Herausgeber.
[Mart Visser](https://github.com/MartVisser) wird im Originalprojekt als Ansprechpartner genannt.

Die Anpassungen in diesem Fork werden unter
[git.mrblake.cc/MrBlake/NetBox-SLM](https://git.mrblake.cc/MrBlake/NetBox-SLM) gepflegt.

Das Projekt steht unter der [Apache License 2.0](LICENSE). Die Hinweise auf die ursprünglichen Urheber bleiben
erhalten.
