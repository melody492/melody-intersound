#!/usr/bin/env python3
"""Täglich in der Cloud (GitHub Actions): Aufrufzahlen aller Videos in daten/videos.js von YouTube holen.
Nur Zahlen, Gesamtsumme und Stand werden geändert – Videos, Bilder und Referenzen pflegt weiterhin
homepage_hochladen.sh vom Mac aus. Schlägt die Abfrage bei zu vielen Videos fehl, bleibt die Datei unverändert."""
import json, re, sys, time, urllib.request, datetime, zoneinfo

PFAD = "daten/videos.js"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
      "Accept-Language": "de-DE,de;q=0.9", "Cookie": "CONSENT=YES+1; SOCS=CAI"}

text = open(PFAD, encoding="utf-8").read()
kopf = text[:text.index("window.MI_DATEN")]
daten = json.loads(text[text.index("{"):text.rindex("}") + 1])

ok = 0
for v in daten["videos"]:
    try:
        req = urllib.request.Request("https://www.youtube.com/watch?v=" + v["id"], headers=UA)
        h = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "ignore")
        m = re.search(r'"viewCount":\{"simpleText":"([\d\.\s,]+)', h) or re.search(r'"viewCount":"(\d+)"', h)
        if m:
            neu = int(re.sub(r"\D", "", m.group(1)))
            if neu >= v["views"] * 0.9:          # Plausibilität: YouTube korrigiert nur minimal nach unten
                v["views"] = neu; ok += 1
            else:
                print("unplausibel, behalten:", v["id"], v["views"], "->", neu)
        else:
            print("keine Zahl gefunden:", v["id"])
    except Exception as e:
        print("Fehler:", v["id"], str(e)[:80])
    time.sleep(1)

anzahl = len(daten["videos"])
print(f"{ok}/{anzahl} Videos aktualisiert")
if ok < anzahl * 0.8:
    print("Zu viele Fehler – Datei bleibt unverändert."); sys.exit(1)

daten["gesamt"] = sum(v["views"] for v in daten["videos"])
daten["stand"] = datetime.datetime.now(zoneinfo.ZoneInfo("Europe/Vienna")).strftime("%d.%m.%Y")
open(PFAD, "w", encoding="utf-8").write(kopf + "window.MI_DATEN = " + json.dumps(daten, ensure_ascii=False, indent=1) + ";\n")
print("Gesamt:", f"{daten['gesamt']:,}".replace(",", "."))
