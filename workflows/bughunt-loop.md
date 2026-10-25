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
4. **Rot-Grün-Zyklus, ohne den es keinen Fix gibt.** Regel des Nutzers (2026-10-17): Funde werden gefixt
   und committet, **aber nur, wenn es einen Test gibt**, der den Fehler zeigt (rot ohne Fix, grün mit Fix).
   Ohne einen solchen Test wird kein Produktionscode geändert und kein Fix committet; der Fund steht dann nur
   im Buch („nur beschrieben“ bzw. „nur Test“). Das gilt auch für reine Doku-Abweichungen wie F35.
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
7. **Commit und Push.** Ein Fund ist ein Commit mit Test, Fix und Buchzeilen (kein Fix-Commit ohne Test, siehe Schritt 4), mit klarer Nachricht und den
   Trailern dieser Session. Danach den Commit-Hash im Eintrag nachtragen, als eigener kleiner Commit
   „Record the commit of Fnn in the bug-hunt ledger“. Nach jedem Commit
   `git push origin ccr-90fc5f6a-vs4s0f`, bei Netzwerkfehlern bis zu 4 Wiederholungen mit 2, 4, 8 und
   16 s Pause. Niemals force-push, keine Modell-Bezeichnungen in Commits.
8. **Keine PRs.** Ein Push startet keine Pipeline, ein PR schon, und die dauert lange. Braucht ein Fund
   unbedingt CI (etwa einen Test, der nur dort laufen kann), wird das im Eintrag unter **CI-Bedarf**
   notiert und weitergemacht. CI macht der Nutzer am Schluss gemeinsam mit dir. Ebenso tabu: GitHub-
   Kommentare und Änderungen an Dateien, die Vorlagen von bernardladenthin/actions sind (Abschnitt
   `templates` in `.github/actions-config.json`), und am Repository bernardladenthin/actions selbst.
9. **Selbst verbessern.** Hat die Runde etwas gezeigt, das künftige Runden schneller oder sicherer macht
   (eine Falle, ein Gate, das fehlte, ein Werkzeug, das nicht erreichbar ist), ergänze es unten unter
   „Erkenntnisse“: eine Zeile mit Datum und Begründung, committet und gepusht im Repo `workspace` auf
   `ccr-90fc5f6a-vs4s0f`. Der Loop darf Regeln schärfen und präzisieren, aber nie lockern: Rot-Grün-
   Zyklus, Gates, „keine PRs“, „kein force-push“, „keine Vorlagen-Dateien“ und die Zielgrenzen bleiben.
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
  `@ToString` trägt. Eine Exception im Konstruktor meldet `CT_CONSTRUCTOR_THROW`: die Prüfung in eine statische
  Methode im `super(...)`-Argument verlegen (F51), statt eine weitere Ausnahme einzutragen.
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
- 2026-10-17: Jackson `ObjectMapper.readTree("")` wirft nicht, sondern liefert `MissingNode` (serialisiert als
  `null`). Code, der „unparsebar → Fallback“ nur über `catch (IOException)` regelt, verfehlt leere Eingaben
  (F37). Bei jedem `readTree` auf Fremdtext prüfen, ob danach `isMissingNode()`/der erwartete Typ geprüft wird.
- 2026-10-17: Nach einem Fund, der auf einem allgemeinen Muster beruht (falsche Annahme über eine Bibliothek,
  ein Idiom), in der nächsten Runde alle Ziele per `grep` nach demselben Muster absuchen, bevor zufällig
  weitergewählt wird. Die `readTree`-Durchsicht nach F37 fand so F38 und F39.
- 2026-10-17: `mvn -q` gibt bei Erfolg nichts aus, und `$?` nach einer Pipe ist der Status von `grep`/`tail`,
  nicht von Maven. Grün daher am Surefire-XML ablesen (`tests`, `failures`, `skipped`) und den
  Maven-Status über `${PIPESTATUS[0]}` prüfen. Rot-Grün-Läufe, die länger als 2 Minuten brauchen, mit
  `run_in_background` starten statt mit Vordergrund-Timeout.
- 2026-10-17: Dateien, die Nutzer selbst anlegen (Secrets, Adresslisten, Prompts, Konfiguration), auf eine
  UTF-8-BOM am Anfang prüfen: Windows-Editoren schreiben sie, und Java entfernt sie beim Dekodieren nicht
  (F42). Durchsicht erledigt (F43 Adressimport, F44 JSON-Konfiguration); java-llama.cpp und streambuffer
  lesen keine Nutzer-Textdateien (nur Binärdaten in `ContentPart`, generierte Listen im Loader). Jacksons
  YAML-Parser überspringt eine BOM, der JSON-Parser nicht.
- 2026-10-17: Buchtext mit Backslashes nicht per `echo "…\\n…"` schreiben, das landet doppelt maskiert in der
  Datei; Python-Heredoc mit `'EOF'` verwenden und das Ergebnis mit `grep -o` gegenlesen.
- 2026-10-17: Ein Test, der ein Verhalten festschreibt, macht es noch nicht zur Designentscheidung. Widerspricht
  er einer Spezifikation und lässt sich ein Absturz zeigen, ist es ein Fund, und der festschreibende Test wird
  mit dem Fix korrigiert (F45: n galt per Test als gültiger Schlüssel). Designentscheidung bleibt, was
  spezifikationskonform ist und nur eine Abwägung trifft (Teilbatch am Bereichsende). Bei `MAX_*`/`*_END`-
  Konstanten immer prüfen, ob die Grenze inklusiv oder exklusiv gemeint ist und so verwendet wird.
- 2026-10-17: Abbrechbare Befehle und Producer (`shouldRun`/`interrupt()`) melden nach der Schleife gern
  „done“/„finished“, auch wenn das Flag sie beendet hat (F46–F49: Export, Import, Delta, Secrets-Dateien).
  Bei jeder abbrechbaren Arbeit prüfen, ob die Fertigmeldung das Flag berücksichtigt. Test: vor dem Lauf
  `interrupt()` aufrufen (oder ein Consumer ruft es nach dem ersten Element) und mit LogCaptor prüfen.
- 2026-10-17: „Flag prüfen, dann laufende Arbeit registrieren“ ist ein Race, wenn `interrupt()` nur die
  registrierte Arbeit stoppt (F50). Nach dem Registrieren das Flag erneut prüfen. Testbar wird das mit einer
  paketinternen Fabrikmethode als Naht (`createSecretsFile`), in deren Test-Override `interrupt()` aufgerufen
  wird – deterministisch, ohne Threads. Nächste Runde: weitere `current…`-Referenzen, die `interrupt()` liest,
  nach demselben Muster absuchen.
- 2026-10-17: Teardown-Schleifen über mehrere Ressourcen (Producer, Broadcaster, Dateien) brechen beim ersten
  Fehler ab und lassen den Rest laufen (F52). Jeden Schritt einzeln absichern, die erste Exception nach der
  Schleife unverändert werfen. BAF unterdrückt `THROWS_METHOD_THROWS_RUNTIMEEXCEPTION` dafür methodengenau in
  `spotbugs-exclude.xml` (mit Begründung gegen Verpacken); dort eintragen, nicht verpacken. Nächste Runde:
  `Finder.interrupt()`/`shutdownAndAwaitTermination` und andere Freigabe-Schleifen nach demselben Muster prüfen.
- 2026-10-17: Die `readTree`-Durchsicht nach F37 hat `ChatStreamChunkParser` übersehen (F53): dort ist der
  `catch`-Zweig ein Abbruchsignal, kein Ersatzwert, und die Javadoc verspricht genau das für jede unparsbare
  Eingabe. Eine Musterdurchsicht ist erst fertig, wenn jede Fundstelle mit dem konkreten Grenzwert (hier `""`)
  durchgedacht ist, nicht nur nach der Form des Codes. Nächste Runde: alle `readTree`-Aufrufe in den Zielen
  erneut, jeweils mit der Frage „was passiert bei `""`?“.
- 2026-10-17: `Paths.get`/`Path.of` auf Fremdtext wirft `InvalidPathException` (eine `IllegalArgumentException`) bei NUL und unter Windows bei `?*<>|"`. Ein Fund nur, wo die Javadoc eine andere, typisierte Ausnahme verspricht (F56 `OfflineModelGuard`). Durchsicht erledigt: BAF (`Main`, `LMDBDelta`) und `RpcServer --cache` werfen sie bei der Argumentprüfung, wo eine IAE passt; streambuffer hat keine Pfade.
- 2026-10-17: Vor dem Rot-Test für einen paketinternen Helfer (`@VisibleForTesting static`) erst jeden Produktionsaufrufer lesen: Kann er die schädliche Eingabe überhaupt liefern? `TuneConfiguration.templatesForDevices` ließ sich mit GPU-Maske rot testen, der einzige Aufrufer übergibt aber immer `CL_DEVICE_TYPE_ALL` – unerreichbar, also kein Fund, nur ein offener Verdacht. Das spart einen Fix ohne Nutzen.
- 2026-10-17: `new BigInteger(s, radix)`, `Integer.parseInt` und `Long.parseLong` akzeptieren ein führendes `-`/`+`. Ein Fund nur, wo der geparste Wert ohne Bereichsprüfung als Bytes weiterlebt (F58 `Base36Decoder`: Zweierkomplement als Hash importiert). Durchsicht erledigt: BAF-Geheimnisse (`SecretsFile` SHA256/BIG_INTEGER, Inkrement-Start/-Ende) laufen durch `PrivateKeyValidator` (negative Werte gelten als außerhalb des Bereichs); java-llama.cpp `RpcServer.requireIpv4Literal` prüft vorher auf Ziffern.
- 2026-10-17: Stand: alle Produktionsklassen der drei Repos haben eine Zeile in `BUGHUNT-CHECKED.md` mit aktuellem Blob-Hash. Ab jetzt gilt Schritt 2.3 (Zusammenarbeit zweier Klassen), bis sich eine Datei ändert. Gute Kandidaten: Producer → Consumer-Warteschlange (BAF), `LlamaModel` ↔ `jllama_api.h`, `OpenAiCompatServer` ↔ Backend, `StreamBuffer` Input- ↔ Output-Stream.
- 2026-10-17: Ein `rm` innerhalb von `nohup bash -c "…"` blockt die Sicherheitsprüfung der Umgebung (sie kann das Skript nicht lesen), und dann läuft der **ganze** Befehl nicht – auch der Fix davor. Lange Prüfketten als Skriptdatei im Scratchpad schreiben und starten, ohne `rm`; Berichte gezielt per Name lesen statt das Verzeichnis zu leeren.
- 2026-10-17: Übersetzungsschichten (Anthropic, Ollama, Responses → OpenAI) gegen upstreams eigene Umsetzung derselben Route lesen (`tools/server/server-chat.cpp`, `common/chat.cpp` am Pin): F60 fiel nur im direkten Vergleich auf (Textblöcke ohne Trenner, upstream mit `\n`). Nächste Runde: `ResponsesApiSupport` auf dieselbe Weise.
- 2026-10-17: Bei Übersetzungsschichten jede `throw std::invalid_argument(...)`-Stelle des upstream-Parsers (`common_chat_msgs_parse_oaicompat` in `common/chat.cpp`, `server-chat.cpp`) gegen die erzeugte Nachricht halten: ein Pflichtfeld, das das Quellprotokoll nicht kennt, wird sonst zu einer 400 erst in der zweiten Gesprächsrunde (F64: Ollama-Werkzeugaufrufe ohne `type`). Bestehende Tests prüfen oft nur das umgewandelte Feld, nicht ob upstream die ganze Nachricht annimmt.
- 2026-10-17: Eine upstream-Funktion als Maßstab zitieren heißt auch prüfen, **wann** sie läuft. `concat_content_parts` verbindet mit `\n`, wird aber nur für Vorlagen ohne typisierten Inhalt aufgerufen; F60/F61 nannten sie zunächst als allgemeines Verhalten und wurden nachträglich präzisiert. Vor dem Eintrag den Aufrufer der zitierten Funktion lesen.
- 2026-10-17: `awaitTermination(timeout)` gefolgt von `close()` einer geteilten Ressource gibt die Ressource frei, während Worker noch laufen; ist die Ressource gegen Nutzung nach dem Schließen „sicher“ gemacht (liefert leer/absent), wird daraus stilles Falschergebnis (F66: Batches als „geprüft, leer“ gemeldet). Test: Listener/Fake hält den Worker im ersten Element fest, kurze Wartezeit, nach `interrupt()` freigeben und auf `runningConsumerCount() == 0` warten. Nächste Runde: weitere `awaitTermination`-Stellen (Producer, OpenCL-Kontext, Broadcaster, java-llama.cpp-Server) auf dasselbe Muster prüfen.
- 2026-10-18: Text, der über JNI geht, auf Modified UTF-8 prüfen: `GetStringUTFChars`/`NewStringUTF` kodieren Zeichen außerhalb der BMP als zwei 3-Byte-Surrogate, und nlohmann lehnt das als „ill-formed UTF-8“ ab (F71, Trainer). Belegbar ohne native Bibliothek: vendortes `json.hpp` vom Pin holen und mit `g++` einen Zweizeiler gegen CESU-8 laufen lassen. Ein Fix auf der Java-Seite (nur ASCII senden) ist mit einem reinen Java-Test rot-grün beweisbar.
- 2026-10-18: `\u` steht in Java auch in Kommentaren für ein Unicode-Escape; `\u escape` im Kommentar ist ein Compile-Fehler. In Kommentaren „backslash-u“ schreiben. Und `ObjectNode.toString()` nutzt Jacksons internen Mapper, nicht die Einstellungen eines eigenen `ObjectMapper`.
- 2026-10-18: Ein `volatile` Feld, das ohne Lock zweimal gelesen wird (Bedingung, dann Rückgabe), gegen **jeden** Schreiber halten, auch interne Wartung unter dem Lock: `trim()` leerte den Puffer über den eigenen Stream und machte den Zwischenstand von `availableBytes` sichtbar (F73, `read()` meldete EOF eines offenen Streams). Ohne Naht ist ein Stresstest zulässig, wenn er mit Fix deterministisch grün ist (hier: ohne Leser sinkt der Zähler nie) und ohne Fix in mehreren Läufen rot wird. streambuffer hat PIT-Schwelle 100: bei Änderungen an `StreamBuffer` PIT lokal laufen lassen (`mvn -q test-compile org.pitest:pitest-maven:mutationCoverage`, rund 10 Minuten, im Hintergrund). Nächste Runde: dasselbe Muster (Lock-freie Doppellesung) in BAF (`Statistics`, Consumer-Zähler) und java-llama.cpp suchen.
- 2026-10-18: Zwei Übersetzer derselben Quellanfrage nebeneinanderlegen und die übernommenen Optionen vergleichen: Ollama-`/api/generate` übernahm ohne `suffix` sechs Sampling-Optionen, mit `suffix` (FIM) nur zwei (F74, `stop` fehlte). Nächste Runde: die Optionsmengen von `OpenAiRequestMapper`, `AnthropicApiSupport`, `ResponsesApiSupport` und `OllamaApiSupport` (`/api/chat`) gegeneinander und gegen die Felder des upstream-Schemas halten.
- 2026-10-18: Ein Fix in einer Übersetzungsschicht ist erst fertig, wenn das erzeugte Feld bis zur nativen Seite verfolgt ist: F75/F76 setzten `reasoning_effort`/`thinking_budget_tokens` korrekt, der nachgeschaltete `OpenAiRequestMapper` baute `InferenceParameters` aber aus einer festen Feldliste und verwarf beide (F77). Vor dem Eintrag den ganzen Weg lesen (Übersetzer → `LlamaModelBackend` → Mapper → `InferenceParameters.toJson()`), und einen Kettentest schreiben, der Übersetzer und Mapper zusammen aufruft.
- 2026-10-18: In Übersetzern den `default`-Zweig jeder Typ-Weiche prüfen: Was passiert mit einem Item-Typ, den der Code nicht kennt? `ResponsesApiSupport` las ein rollenloses `reasoning`-Item als Nachricht und machte daraus `role: "user"` (F85) – schlimmer als Verwerfen. Mit upstreams Liste der Item-Typen vergleichen (`convert_responses_to_chatcmpl`, `convert_anthropic_to_oai`) und für jeden fremden Typ einen Test schreiben.
- 2026-10-18: Upstreams Umsetzer einer Route einmal ganz von oben bis unten lesen, auch die Hilfsfunktionen davor: `normalize_anthropic_billing_header` steht vor `server_chat_convert_anthropic_to_oai` und tauchte in keiner Typ-Weiche auf (F90, ohne sie trifft der Prefix-Cache bei Claude Code nie). Danach `git log -S` bzw. die PR-Nummer im Kommentar lesen: solche Sonderfälle stammen aus Fehlerberichten echter Clients.
- 2026-10-18: Bei einem Fund in einem Adaptermodul den blockierenden und den gestreamten Pfad Feld für Feld vergleichen (F92: `thinking()` nur im Stream). Und vor dem Gate-Lauf prüfen, welche Plugins das Modul deklariert: `llama-langchain4j` hat weder Spotless noch SpotBugs, „No plugin found for prefix“ ist dort kein Fehler, sondern das Fehlen des Gates.
- 2026-10-18: Musterdurchsichten auch auf die Adaptermodule ausdehnen, nicht nur auf `llama/src/main/java/.../server`: Das F60/F61-Muster (Textteile ohne Trenner verbunden) steckte auch in `llama-langchain4j` (F94) und war dort durch einen Test verdeckt, dessen Eingabe zufällig ein Leerzeichen am Ende trug. Festschreibende Tests mit einer Eingabe ohne Leer- oder Satzzeichen an der Naht gegenprüfen.
- 2026-10-18: Einen offenen Verdacht, der „braucht einen API-Umbau“ als Blocker nennt, vor dem Überspringen in seine Teile zerlegen: Bei F95 hatten fast alle verworfenen Felder schon einen Setter, nur ein Rest (`logit_bias`, `n`) braucht wirklich Neues. Ein Teilfix mit Rot-Grün ist erlaubt, der Verdacht bleibt mit Nachtrag für den Rest stehen. SpotBugs dazu: viele `JsonNode`-Aufrufe in einer Methode melden `CE_CLASS_ENVY`, eine Map, die nur iteriert wird, `DMC_DUBIOUS_MAP_COLLECTION`; ein kleiner statischer Helfer je Feldtyp (`withFloat(params, request, "min_p", InferenceParameters::withMinP)`) besteht beide.
- 2026-10-18: Ein Fix, der mehrere Richtungen oder Felder ändert (Antwort, Stream, Verlauf), bekommt einen Test je Richtung: In einem Sammeltest zeigt die Gegenprobe nur das Rot der ersten Assertion, die übrigen sind ungeprüft (F96, F97 haben das nur notiert). Ab jetzt je Richtung eine eigene `@Test`-Methode.
- 2026-10-18: Prüfskripte nicht per `sed` aus dem der vorigen Runde ableiten, ohne die breite Testliste gegenzulesen: Das Ersetzen der Zielklasse traf auch deren Eintrag in der breiten Liste, und `OpenAiCompatServerHttpTest` fiel bei F99 still heraus (nachgeholt, 47/47). Die breite Liste als eigene, unveränderte Zeile führen und nach dem Ableiten mit `grep` prüfen, dass alle Klassen darin stehen.
- 2026-10-18: Eine Exception in einem per `submit(...)` gestarteten Runnable landet im `Future`; liest ihn niemand (`get()`), erscheint sie nirgends (F100, F101: Socket-Reader). Nächste Runde: alle `submit(`-Aufrufe in den Zielen suchen, deren `Future` verworfen oder nur für `cancel` gehalten wird, und prüfen, ob eine Ausnahme darin geloggt oder sonst sichtbar wird. `execute(...)` meldet sie dagegen über den Uncaught-Handler.
- 2026-10-18: Bei jeder Übernahme eines Felds in einen Mapper die Sonderwerte des Empfängers prüfen, nicht nur den Typ: upstreams `-1` (Standard, F102 `id_slot`) und `0` (eigene Bedeutung, F103 `max_tokens` = nur Cache füllen) wurden von `> 0`/`>= 0`-Prüfungen und strengen Settern falsch behandelt. Quelle der Sonderwerte: `set_desc`, `set_hard_limits` und `json_value(data, "...", <Standard>)` in upstreams `server-schema.cpp`/`server-context.cpp`.
- 2026-10-18: Ein Fix, der eine ganze Feldmenge übernimmt, bekommt einen parametrisierten Test mit einem Fall je Feld (`@ParameterizedTest` + `@CsvSource(delimiter = '|')`, Feldname und JSON-Wert): so zeigt jedes Feld sein eigenes Rot (F106: 27 Fälle, 27 Fehlschläge ohne Fix), nicht nur das erste wie in einem Sammeltest.
- 2026-10-18: Ändert ein Fix, *wie* eine Methode arbeitet (F73: `trim()` liest nicht mehr über den eigenen Stream), vor dem Commit alle Kommentare und Javadocs der Datei nach dem alten Ablauf durchsuchen (`grep -n "trim()" <Datei>`); sonst bleibt eine Beschreibung stehen, die nur noch der alte Code erfüllt (F110), und eine reine Doku-Abweichung lässt sich danach nicht mehr mit Rot-Grün beheben.
- 2026-10-18: Braucht ein Fix eine neue Naht, ist die `git stash`-Gegenprobe wertlos: der Stand ohne Fix hat auch keine Naht, der Test kompiliert nicht, und Surefire lässt den **alten** Bericht liegen, der dann wie Grün aussieht (F111). Gegenprobe stattdessen gegen den Naht-Stand (HEAD-Datei plus neutrale Naht) laufen lassen und den Bericht vor jedem Lauf löschen (`rm -f llama/target/surefire-reports/TEST-*.<Klasse>.xml`), damit ein Kompilierfehler nicht als Ergebnis gelesen wird.
- 2026-10-18: Bei einem HTTP-Server die Routenliste als Ganzes gegen upstream halten (`grep -o 'ctx_http\.[a-z]*( *"[^"]*"' tools/server/server.cpp`) und die Zuordnungsregel der verwendeten Bibliothek prüfen: `com.sun.net.httpserver` ordnet nach dem längsten Präfix zu, nicht exakt (F112: `/v1/messages/count_tokens` lief als ganze Generierung). Routen-Aliase, die nur über ein Präfix funktionierten (`/v1/reranking`), dabei ausdrücklich registrieren.
- 2026-10-18: Nennen CLAUDE.md oder Javadoc einen bestimmten Client als Ziel (Copilots Ollama-Anbieter, Claude Code, Continue), dessen Quelltext lesen statt zu raten (`curl` auf raw.githubusercontent.com geht durch den Proxy): F114 fiel nur dort auf (`MINIMUM_OLLAMA_VERSION = '0.6.4'`), die Javadoc behauptete das Gegenteil. Nächste Runde: den Rest von `ollamaProvider.ts` (welche Felder aus `/api/show` und `/api/tags` gelesen werden) gegen unsere Antworten halten.
- 2026-10-18: Bei Übersetzern die Fehlerzweige der Streaming-Routen gegen den echten Client lesen, nicht nur die Erfolgsfolge: Codex verwirft ein Ereignis ohne `type` stillschweigend und liest Fehler nur aus `response.failed` (F117) – die Erfolgsfolge war längst geprüft, der Fehlerweg nie.
- 2026-10-18: Jeder Fund-Eintrag beginnt mit `<a id="fnn"></a>` direkt über der Überschrift (Schritt 6): GitHub leitet aus `### Fnn – …` einen langen Anker ab, die Übersichtslinks `#fnn` liefen bei 28 Einträgen ins Leere, weil die Zeile beim Schreiben weggelassen wurde. Nach jedem Eintrag prüfen: `grep -c "^### F" ` gleich `grep -c "^<a id=\"f"`.
- 2026-10-18: „Zustand lesen, dann Teilnehmer registrieren“ gegen „Zustand setzen, dann an alle Registrierten senden“ verliert eine Nachricht, wenn das Setzen dazwischen fällt (F119, Gruß im Socket-Broadcaster). Beide Paare unter ein Lock legen. Testbar mit einer Naht genau zwischen Lesen und Registrieren, in der ein zweiter Thread das Setzen ausführt, bis er endet oder `BLOCKED` ist; die Gegenprobe läuft gegen eine Kopie des Naht-Stands (F111). Nächste Runde: weitere Gruß-/Snapshot-plus-Abo-Stellen (Listener-Listen, `CopyOnWrite`-Mengen mit Begrüßung) nach demselben Muster absuchen.
- 2026-10-18: Prüfzeilen ohne eigene Notiz („gelesen, keine Notiz“) oder mit der Notiz einer anderen Datei verraten eine flache Durchsicht: Die Zeile von `LlamaModel.java` trug seit dem 17. die Notiz von `EmbeddingResponseParser`, die Klasse war nie Methode für Methode gelesen (Batch-Methoden auf dem gemeinsamen `ForkJoinPool`, als Verdacht notiert). Sind alle Dateien aktuell, solche Zeilen vor Schritt 2.3 erneut gründlich prüfen; Kandidaten mit `grep -n "gelesen, keine Notiz" BUGHUNT-CHECKED.md`.
- 2026-10-18: Ein Test, der seine Eingabe selbst vorbereitet (normalisiert, trimmt, umkodiert), bevor er die Bibliothek aufruft, beweist nur die Bibliothek, nicht den Produktionspfad: `bip39Vector_…ForLanguage` normalisierte NFKD selbst, `BIP39KeyProducer` tat es nicht, 142 Vektoren lieferten falsche Schlüssel (F120). Bei Testvektoren immer prüfen, ob der Produktionseinstieg sie roh bekommt; `grep -n "Normalizer\|trim()\|strip()" src/test` zeigt Kandidaten. Für Fremdbibliotheken mit `javap -c -p` nachsehen, was sie wirklich tun.
- 2026-10-18: Parser für Fremdformate (Adressen, Mnemonics) mit einer kleinen Probe-Klasse gegen viele Schreibweisen einer gültigen Eingabe laufen lassen, bevor man Code liest: `mvn dependency:build-classpath`, eine `main` im Scratchpad, `javac`/`java` gegen `target/classes`. So fiel F121 in einem Lauf auf (CashAddr groß: einmal abgelehnt, einmal still ein falscher hash160). Varianten: Groß/Klein, mit/ohne Präfix, NFC/NFKD, Leerraum, BOM.
- 2026-10-18: Den Surefire-Bericht vor **jedem** Lauf löschen, auch vor dem Grün-Lauf, nicht nur vor der Gegenprobe: bei F123 scheiterte der Grün-Lauf am Compiler (`-Werror`, `NotJavadoc`), und der liegengebliebene rote Bericht sah wie „Fix wirkt nicht“ aus. Steht im Skript ein Maven-Status ≠ 0 neben unveränderten Zahlen, zuerst `mvn -o compile` ohne `-q` laufen lassen. Und Konstanten nie direkt unter eine vorhandene Javadoc einfügen (F108, F123): den Anker auf die Javadoc-Zeile legen, nicht auf die Deklaration.
- 2026-10-18: Ein `interrupt()` aus dem Shutdown-Hook kann mitten in einer mehrstufigen Startsequenz landen (`Main.run`: Key-Producer → Consumer/LMDB → Producer); gibt es frei und leert Listen, scheitert der nächste Startschritt an fehlenden Einträgen und meldet einen falschen Fehler (F124: „Key producer id is unknown“). Bei jeder Startsequenz prüfen, ob die Schritte nach einem `interrupt()` noch laufen; Test: `interrupt()` zwischen zwei Schritten aufrufen und den nächsten mit `assertDoesNotThrow` ausführen.
- 2026-10-18: CLI-Parser darauf prüfen, ob ein syntaktisch gültiger, aber unzulässiger Wert (Port außerhalb 0..65535, negative Anzahl) erst nach einem teuren Schritt scheitert (F125: Modell-Laden vor dem Binden). Für jedes Flag fragen: Welche Funktion verbraucht den Wert zuerst, und läuft vorher etwas Langes?
- 2026-10-18: Mitgelieferte Beispielkonfigurationen nicht für geprüft halten, nur weil ein Test „dieselbe“ Datei startet: `MainTest` nutzt eine eigene Kopie unter `src/test/resources/testRoundtrip/`, die einen Platzhalter-Key-Producer trägt; das Beispiel in `examples/` scheiterte (F127). `ConfigFixturesParseTest` prüft nur das Parsen. Beispiel und Testkopie mit `diff` über normalisiertes JSON vergleichen und die semantischen Prüfungen (IDs, Bereiche) per Skript über alle Beispiele laufen lassen.
- 2026-10-18: Werte, die an eine Fremdbibliothek gehen, gegen deren Vorbedingungen halten, nicht nur gegen die eigene Javadoc: langchain4js `PartialToolCall` verlangt nicht leere Argumente und einen Namen (`ensureNotEmpty`/`ensureNotBlank`, per `javap -c` am Jar sichtbar), upstreams Diff-Writer liefert beides leer (F128). Bei jedem `*.builder()...build()` einer Fremdklasse auf Fremddaten die `ensure*`-Aufrufe im Konstruktor nachsehen.
- 2026-10-18: In dieser Sandbox lässt sich eine OpenCL-Laufzeit nachinstallieren (`apt-get update && apt-get install -y pocl-opencl-icd`, wenige Minuten); danach laufen BAFs `@OpenCLTest`s und `producerOpenCL` lokal. Den GPU-Pfad Ende zu Ende gegen den CPU-Pfad halten (gleiche Datenbank, gleicher Bereich, Treffermengen vergleichen) und die Kernel-Parameter variieren (`keysPerWorkItem`, Filtermodus): so fiel F129 auf, das in keinem Test sichtbar war, weil alle mit `keysPerWorkItem` 1 oder ohne Basis 0 rechnen.
- 2026-10-18: Jede Behauptung eines Eintrags messen, bevor sie im Buch steht, auch die Nebenbehauptung: F129 nannte zusätzlich ein Problem am oberen Ende (nahe n), aus dem Kernel-Kommentar abgeleitet; gemessen weist der Host solche Raster vorher ab, die Behauptung war falsch und musste nachgetragen werden. Bei Grenzfällen nahe n außerdem die Teilbatch-Regel bedenken: n mod 256 = 65, das oberste Raster reicht bei Standardgrenzen immer über das Ende und wird auf keinem Pfad gescannt.
- 2026-10-18: Auf pocl (siehe oben) mit großen Rastern (`batchSizeInBits` 18) und `keysPerWorkItem` ≤ 16 stirbt die JVM mit SIGSEGV im Kernel: pocl wählt ohne Vorgabe eine Work-Group von 4096 und überläuft seinen 8-MB-Thread-Stack. Für solche Läufe `POCL_MAX_WORK_GROUP_SIZE=256` setzen; ein Absturz dort ist zuerst als Umgebungsgrenze zu prüfen (hs_err: `si_addr` an der Stack-Guard-Page), bevor er als Fund gilt.
- 2026-10-18: Ausgabekanäle (Broadcaster, Log-Senken, Dateien) über einen ganzen echten Lauf prüfen und am Ende zählen, was angekommen ist: die Unit-Tests der Broadcaster schickten je ein, zwei Nachrichten und warteten auf sie, keiner schloss mit gefüllter Warteschlange – so blieben F130 (`close()` verwirft) und F131 (Finder schließt vor dem Consumer-Drain) verborgen. Bei Funden dieser Art die Zeitstempel im Log gegeneinander halten (`interrupt called` gegen den letzten Treffer): sie trennen zwei Ursachen, die dasselbe Symptom haben.
- 2026-10-18: Ist pocl installiert, laufen BAFs `@OpenCLTest`s mit, auch in breiten Listen: `MainTest` stirbt dann ohne `POCL_MAX_WORK_GROUP_SIZE=256` an seiner OpenCL-Roundtrip-Fork (auch gegen den unveränderten Stand). Breite Läufe mit der Variable starten; fehlt ein Surefire-Bericht, zuerst die Klasse einzeln und gegen `git stash` laufen lassen, bevor der Fix verdächtigt wird. Und bei Reihenfolge-Fixes im Shutdown jeden Test der Klasse laufen lassen, nicht nur den neuen: der erste F131-Versuch brach einen bestehenden Test mit absichtlich nicht endenden Producern.
- 2026-10-18: Ein Kommando, das ein Zielverzeichnis „ersetzt“, mit einem Ziel prüfen, das ein *anderes* Werkzeug hinterlassen hat (hier eine beschreibbar geöffnete LMDB mit `lock.mdb`), nicht nur mit dem eigenen vorigen Ergebnis – der eigene zweite Lauf war grün, weil die read-only Prüföffnung mit `MDB_NOLOCK` keine Lock-Datei anlegt (F132).
- 2026-10-18: Nennt ein Fix-Eintrag eine andere Stelle als Vorbild („wie `setPoolingType`“), diese Stelle nachprüfen: F13 berief sich auf `setPoolingType`, das `UNSPECIFIED` gerade nicht entfernte (F133). Bei Buildern mit Wächterwerten (`UNSPECIFIED`, `NONE`, `null`) immer `set(A).set(Wächter)` testen, nicht nur `set(Wächter)` auf einem frischen Objekt.
- 2026-10-18: Die Muster-Suche nach F133 traf in derselben Runde F134: `grep -n "null clears\|clears" ` über die Javadoc der Builder und dann je Treffer `set(x).set(null)` testen. Ein Basishelfer mit „`null` = no-op“ widerspricht stillschweigend jedem Aufrufer, der „`null` clears“ verspricht – den Helfer gegen die Javadoc *aller* Aufrufer halten. Liegt der Helfer auf dem PIT-Gate, PIT gezielt mit `-DtargetClasses=<Klasse>` laufen lassen (hier unter einer Minute).
- 2026-10-18: `TuneConfiguration` läuft auf pocl in Sekunden, wenn man die Listen klein macht (`batchSizeInBitsCandidates` [8, 10], `secondsPerArm` 2, `targetDatabaseEntries` 10000, kein `lmdbDirectory`); so lassen sich Entscheidungslogiken wie die Rand-Erweiterung Ende zu Ende prüfen (F135). Die Durchsätze auf pocl schwanken aber um den Faktor 2 zwischen zwei Läufen desselben Arms – nie eine Beschleunigung daraus ableiten, nur den Ablauf (welche Arme gemessen werden).
- 2026-10-18: Ist ein Fehler in einer Klasse einmal behoben worden (hier: „jedes Gerät behält seinen eigenen Gewinner“, `applyWinnerTo`), jede *weitere* Stelle suchen, die denselben Wert nimmt: `grep -n "winner"` zeigte, dass die Filterstufe noch den globalen `winner` nahm und ihn über `runArm` in den Producer schrieb (F136). Methoden, die ein geteiltes Objekt „in place“ verändern, sind der Ort, an dem so ein Rest wieder durchschlägt.
- 2026-10-18: Builder-Werte bis zu ihrem Verbraucher verfolgen und dort nach Vorbedingungen der JDK-API suchen (`scheduleAtFixedRate` Periode > 0, `new InetSocketAddress` Port 0..65535, `Semaphore`/`ArrayBlockingQueue` Kapazität > 0): F138 – die `IllegalArgumentException` aus der JDK-Methode fiel in einen `catch (IllegalArgumentException …)`, der Fehler der Anfrage meint. Besonders gefährlich, wo ein Handler IAE als Client-Fehler übersetzt. Das Symptom zuerst mit einer nicht committeten Probe im vorhandenen modellfreien Test messen.
- 2026-10-18: Startfehler nicht nur auf die Meldung prüfen, sondern darauf, ob der Prozess danach *endet*: `timeout 60 java … Main <config>` und Exit-Code 124 bedeutet „hängt“ (F139: Consumer-Threads überlebten den Fehlerpfad, weil `interrupt()` nur einen Teil freigibt). Jeder Schritt einer Startsequenz, der Nicht-Daemon-Threads startet, braucht einen Fehlerpfad, der sie wieder stoppt; testbar mit dem Muster aus F21 (Menge der lebenden Nicht-Daemon-Threads vorher/nachher).
- 2026-10-18: Ein Fix, der eine Prüfung *früher* wirft (F126: Key-Producer-IDs in `startKeyProducer`), verschiebt den Fehler in jeden Aufrufer dieser Methode – nach einem solchen Fix alle Aufrufer suchen (`grep -rn startKeyProducer src/main`) und prüfen, ob der Fehler dort noch in einem `try` mit Aufräumen landet. `TuneConfiguration` rief sie vor ihrem `try` auf und hing danach (F140).
