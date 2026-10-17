# Bug-Hunt-Loop (selbstverbessernd)

Diese Datei ist die Anweisung für den endlosen Fehlersuch-Loop auf den Arbeitsbranches. Aufgerufen wird
sie mit:

```
/loop Lies /home/user/workspace/workflows/bughunt-loop.md vollständig und führe genau eine Runde danach aus.
```

Jede Runde liest diese Datei neu. Was der Loop in Abschnitt „Erkenntnisse“ ergänzt, gilt also ab der
nächsten Runde. Der Loop läuft, bis der Nutzer ihn stoppt; es gibt keine Endzeit.

## Ziele und Arbeitsstand

- Repos: `/home/user/streambuffer`, `/home/user/BitcoinAddressFinder` und der Java-Teil von
  `/home/user/java-llama.cpp` (nur `llama/src/main/java` sowie die Module `llama-langchain4j`,
  `llama-kotlin` und `llama-ffm`; kein C++, kein CMake, keine Workflows).
- In jedem Repo ist der Branch `ccr-90fc5f6a-vs4s0f` der Stand, auf dem gesucht wird. Jede Runde baut
  auf dem verbesserten Stand der vorigen auf. Nie den Branch wechseln.
- Buchdateien im Wurzelverzeichnis jedes Repos:
  - `BUGHUNT-FOUND.md`: Funde, je mit globaler ID `Fnn` (über alle drei Repos eindeutig), dazu oben
    eine Übersicht und unten „Offene Verdachte ohne Fund-ID“.
  - `BUGHUNT-CHECKED.md`: eine Zeile je gründlich gelesener Datei,
    `` - `Pfad` · `Blob-Hash` · Datum · Ergebnis — Notiz ``.

## Ablauf einer Runde

1. **Stand holen.** In jedem der drei Repos `git pull --ff-only origin ccr-90fc5f6a-vs4s0f`. Gibt es
   außer den beiden Buchdateien uncommittete Änderungen, schließe zuerst die Arbeit daran ab (oder
   verwirf sie, wenn sie unvollständig und nicht beweisbar ist). Gibt es nur Buchänderungen, committe
   und pushe sie als „Update the bug-hunt ledger“. Eine Runde ohne Fund committet und pusht ihre
   Buchzeile ebenso sofort am Ende der Runde: ein Push kostet nichts, und nichts bleibt uncommittet.
2. **Ziel wählen**, in dieser Reihenfolge:
   1. Offene Einträge zuerst: ein Fund mit Status „nur beschrieben“ oder „unsicher“ oder ein offener
      Verdacht, dessen Blocker nicht mehr besteht. Ausgenommen sind Designentscheidungen, die im
      Eintrag als solche markiert sind (z. B. F03); diese fasst du nicht an.
   2. Sonst zufällig ein Repo und darin eine Produktionsklasse (`*.java`/`*.kt` unter `src/main`, ohne
      `module-info`/`package-info`), die in `BUGHUNT-CHECKED.md` fehlt oder deren aktueller Blob-Hash
      (`git rev-parse --short HEAD:<Pfad>`) vom notierten abweicht.
   3. Sind alle geprüft und unverändert: eine Zusammenarbeit zweier Klassen (Aufrufer und
      Aufgerufener, Producer und Consumer, Java-Seite und C-API-Vertrag in `jllama_api.h`), mit Fokus
      auf die Schnittstelle.
3. **Lesen und suchen.** Die Klasse und ihre direkten Aufrufer gründlich lesen. Echte Fehler suchen:
   Grenzfälle, Off-by-one, Überläufe, Nebenläufigkeit und Races, Ressourcenlecks, falsche
   Fehlerbehandlung, Null-Pfade, falsche `equals`/`hashCode`, Encoding und Endianness, Pfad- und
   Dateisystemfälle, Abweichungen zwischen Javadoc und Code. Stil-Nits zählen nicht. Vorher
   `BUGHUNT-FOUND.md` aller drei Repos lesen, damit nichts doppelt gemeldet wird.
4. **Rot-Grün-Zyklus, ohne den es keinen Fix gibt.**
   1. Zuerst einen kleinen Test im passenden Testverzeichnis schreiben (Konventionen nach `CLAUDE.md`
      und den TEST_WRITING_GUIDEs), der genau den Fehler zeigt. Gegen den unveränderten
      Produktionscode muss er ROT sein, aus dem erwarteten Grund: eine Assertion oder eine erwartete
      Exception, nicht ein Compile-, Setup- oder Umgebungsfehler und kein Selbst-Überspringen. Die
      Fehlermeldung notieren. Braucht der Test eine Naht, die es noch nicht gibt, zieht man sie zuerst
      verhaltensneutral ein und zeigt Rot gegen genau diesen Stand.
   2. Dann der Fix, minimal und im Stil des umgebenden Codes. `mvn spotless:apply`; derselbe Test muss
      GRÜN sein, ebenso die übrigen Tests seiner Klasse.
   3. Gegenprobe: Fix per `git stash push <Produktionsdatei>` zurücknehmen → wieder rot;
      `git stash pop` → wieder grün.
   4. Eng testen: `mvn -q test -Dtest=<Klasse>Test` (bei java-llama.cpp mit `-f llama/pom.xml`), nie die
      ganze Suite. Im Surefire-Report prüfen, dass der Test wirklich lief (`tests>0`, `skipped=0` für
      den neuen Test).
   5. Lässt sich der Fehler nicht durch einen lauffähigen Test zeigen (native Bibliothek, GPU, Modell,
      fehlende Toolchain), wird er nur beschrieben und der Code bleibt unverändert. Ein roter Test
      ohne Fix ist erlaubt, Status „nur Test“. Bestätigt sich der Verdacht nicht: „widerlegt“ mit
      Begründung.
5. **Gates vor jedem Push.** Für jedes Modul, dessen Produktionscode sich geändert hat, laufen vor dem
   Push und müssen grün sein:
   - `mvn spotless:apply`, danach kein Diff außer dem beabsichtigten;
   - `mvn -B -q -DskipTests -Denforcer.skip=true compile spotbugs:check` (bei java-llama.cpp mit
     `-f llama/pom.xml`; SpotBugs bindet an `verify`, `mvn test` sieht es nicht);
   - die Architekturtests (`BitcoinAddressFinderArchitectureTest`, `LlamaArchitectureTest`);
   - bei geänderten Ausgabeformaten die Tests, die die Zeichenkette erwarten, und die README-Stellen.

   Ein Push, der an einem Gate vorbeigeht, ist ein Fehler. Passiert er doch, wird sofort nachgezogen.
6. **Buch führen.** Bei einem Fund: neue ID = höchste `Fnn` über alle drei `BUGHUNT-FOUND.md` plus eins.
   Eintrag anhängen (vor „Offene Verdachte“):
   `<a id="fnn"></a>`, `### Fnn – <Repo>: <Titel>`, dann die Zeilen **Zeit** (UTC), **Datei** (Pfad:Zeile),
   **Schwere** (hoch/mittel/niedrig), **Beschreibung**, **Fix**, **Reproduktion** (Testname),
   **Rot-Grün-Nachweis** (rote Meldung ohne Fix, grün mit Fix samt Testanzahl, Gegenprobe), **Status**
   (gefixt/nur Test/nur beschrieben/unsicher) und **Commit**. Dazu die Übersichtszeile oben ergänzen.
   „gefixt“ nur mit bestandenem Zyklus. In jedem Fall die Zeile der Datei in `BUGHUNT-CHECKED.md`
   ersetzen oder ergänzen: aktueller Blob-Hash (`git hash-object <Pfad>`, sieben Zeichen), Datum,
   Ergebnis, kurze Notiz, was geprüft wurde.
7. **Commit und Push.** Ein Fund ist ein Commit mit Test, Fix und Buchzeilen, mit klarer Nachricht und den
   Trailern dieser Session. Danach den Commit-Hash im Eintrag nachtragen, als eigener kleiner Commit
   „Record the commit of Fnn in the bug-hunt ledger“. Nach jedem Commit
   `git push origin ccr-90fc5f6a-vs4s0f`, bei Netzwerkfehlern bis zu 4 Wiederholungen mit 2, 4, 8 und
   16 s Pause. Niemals force-push, keine Modell-Bezeichnungen in Commits.
8. **Keine PRs.** Ein Push startet keine Pipeline, ein PR schon, und die dauert lange. Braucht ein Fund
   unbedingt CI (etwa einen Test, der nur dort laufen kann), wird das im Eintrag unter **CI-Bedarf**
   notiert und weitergemacht. CI macht der Nutzer am Schluss gemeinsam mit dir. Ebenso tabu: GitHub-
   Kommentare und Änderungen an Dateien aus `.github/shared-files.sha256`.
9. **Selbst verbessern.** Hat die Runde etwas gezeigt, das künftige Runden schneller oder sicherer macht
   (eine Falle, ein Gate, das fehlte, ein Werkzeug, das nicht erreichbar ist), ergänze es unten unter
   „Erkenntnisse“: eine Zeile mit Datum und Begründung, committet und gepusht im Repo `workspace` auf
   `ccr-90fc5f6a-vs4s0f`. Der Loop darf Regeln schärfen und präzisieren, aber nie lockern: Rot-Grün-
   Zyklus, Gates, „keine PRs“, „kein force-push“, „keine shared-files“ und die Zielgrenzen bleiben.
   Größere Umbauten dieser Datei gehören in eine Notiz an den Nutzer, nicht in einen stillen Edit.
10. **Kurz berichten und weiter.** Eine kurze sichtbare Zeile, was die Runde gefunden oder geprüft hat.
    Dann `ScheduleWakeup` mit 60 s und genau dem Aufruf oben als `prompt`.

## Erkenntnisse

- 2026-10-17: `spotbugs:check` bindet an `verify` und läuft bei `mvn test` nicht mit. Ohne das Gate
  landeten in BAF sieben SpotBugs-Funde aus den Fixes der Nacht auf dem Branch (F14, F20, F21, F31),
  in java-llama.cpp einer (F01). Deshalb ist Schritt 5 Pflicht.
- 2026-10-17: SpotBugs (fb-contrib) meldet hier regelmäßig `WEM_WEAK_EXCEPTION_MESSAGING` (statische
  Exception-Meldung: einen Wert einbauen), `IMC_IMMATURE_CLASS_WRONG_FIELD_ORDER` (statische Felder
  vor Instanzfeldern), `HES_LOCAL_EXECUTOR_SERVICE` (Executor als lokale Variable) und
  `EXS_EXCEPTION_SOFTENING_NO_CONSTRAINTS` (checked → unchecked nur in einer an ein Interface gebundenen
  Methode wie `run()`, Helfer deklarieren die checked Exception). `synchronized`-Methoden scheitern an
  `USO_UNSAFE_METHOD_SYNCHRONIZATION`: privates Lock-Objekt, mit `@ToString.Exclude`, wenn die Klasse
  `@ToString` trägt.
- 2026-10-17: Races werden deterministisch, indem ein Fake im „nativen“ Aufruf festgehalten wird (Latch)
  und der zweite Thread bis `Thread.State.BLOCKED` oder Ende abgewartet wird. Native Aufrufe bekommen
  dafür eine paketinterne Naht (`Backend`-Interface, Muster `RpcServer.Backend`); die JNI-Methoden
  bleiben in ihrer Klasse, sonst ändern sich die Symbolnamen.
- 2026-10-17: In dieser Sandbox gibt es kein JDK 22+; GitHub-Releases und api.adoptium.net sind
  gesperrt. Funde in `llama-ffm` lassen sich hier nicht beweisen, sie bleiben „nur beschrieben“ mit
  CI-Bedarf.
- 2026-10-17: Die Drop-Checks der llama.cpp-Patches und alles unter `llama/patches/` gehören nicht zum
  Ziel (kein C++).
- 2026-10-17: Buchzeilen ohne Fund werden sofort committet und gepusht, nicht erst nach 60 Minuten (Schritt 1):
  liegen sie uncommittet herum, meldet der Stop-Hook jede Runde „uncommitted changes“.
- 2026-10-17: Kandidaten mit `grep -F -e "- \`<Pfad>\` · "` in `BUGHUNT-CHECKED.md` suchen: ohne `-e` hält
  grep das Muster wegen des führenden `-` für eine Option. Blob-Hashes immer mit
  `git rev-parse --short=7 HEAD:<Pfad>` bzw. den ersten sieben Zeichen von `git hash-object` vergleichen.
- 2026-10-17: Bei der Zufallswahl Klassen mit mindestens 80 Zeilen bevorzugen (`wc -l`), Konfigurations-,
  Konstanten- und Wertklassen (`/configuration/`, `/constants/`, `/value/`, `/args/`) zuletzt: Die
  kleinen Picks (ein Interface, ein 53-Zeilen-Helfer) brachten zwei Runden ohne Verhaltensbefund.
- 2026-10-17: Ein verschlucktes `InterruptedException` ist nur dann ein Fund, wenn ein Pfad den Thread
  wirklich unterbricht (`Thread.interrupt()`, `shutdownNow()`, `Future.cancel(true)`); in BAF setzt
  `interrupt()` der Producer und Key-Producer nur ein Flag.
- 2026-10-17: Die Größe für die Zufallswahl in Codezeilen messen, nicht in Dateizeilen:
  `grep -cvE '^\s*(\*|/\*\*|//|$)' <Datei>`. Eine 100-Zeilen-Exception war fast nur Javadoc. Stand
  heute haben nur noch wenige ungeprüfte Klassen 60+ Codezeilen; danach Schritt 2.3 (Schnittstellen
  zwischen Klassen) gleichrangig zu den kleinen Klassen behandeln.
