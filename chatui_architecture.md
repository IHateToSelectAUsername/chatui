# Chatui Architektur und Kommunikationsfluss

Dieses Dokument beschreibt die Architektur und den Kommunikationsfluss der chatui-Anwendung, einschließlich der Startsequenz, der Nachrichtenverarbeitung und der API-Kommunikation.

## Inhaltsverzeichnis

- [Übersicht](#übersicht)
- [Komponenten](#komponenten)
- [Sequenzdiagramm: Vollständiger Kommunikationsfluss](#sequenzdiagramm-vollständiger-kommunikationsfluss)
- [Klassendiagramm: Anwendungsstruktur](#klassendiagramm-anwendungsstruktur)
- [Ablaufdiagramm: Nachrichtenverarbeitung](#ablaufdiagramm-nachrichtenverarbeitung)
- [Detaillierter Ablaufplan](#detaillierter-ablaufplan)

## Übersicht

Die chatui-Anwendung ist eine Terminal-basierte Benutzerschnittstelle (TUI) für Konversationen mit der OpenAI API. Sie nutzt das Textual-Framework für die Benutzeroberfläche und kommuniziert asynchron mit der OpenAI API.

## Komponenten

Die Anwendung besteht aus mehreren Hauptkomponenten:

```mermaid
flowchart TB
    subgraph "Einstiegspunkte"
        run["run.py\n(Einstiegspunkt im Wurzelverzeichnis)"]
        main_module["python -m chatui.main\n(Modulbasierter Einstiegspunkt)"]
    end
    
    subgraph "Anwendungskern"
        main["main.py\n(Hauptmodul)"]
        tui["tui.py\n(ChatApp - Textual UI)"]
        chat["chat.py\n(Conversation - API-Kommunikation)"]
    end
    
    subgraph "Externe Abhängigkeiten"
        textual["Textual Framework"]
        openai["OpenAI API"]
        settings["settings.py\n(Konfiguration)"]
    end
    
    run --> main
    main_module --> main
    main --> tui
    tui --> textual
    tui --> chat
    chat --> openai
    chat --> settings
```

## Sequenzdiagramm: Vollständiger Kommunikationsfluss

Das folgende Sequenzdiagramm zeigt den vollständigen Kommunikationsfluss von der Anwendungsinitialisierung bis zur Antwortanzeige:

```mermaid
sequenceDiagram
    autonumber
    participant User as Benutzer
    participant Run as run.py
    participant Main as main.py
    participant TUI as tui.py (ChatApp)
    participant Conv as chat.py (Conversation)
    participant API as OpenAI API
    participant UI as Textual Interface

    %% Startprozess
    User->>Run: Startet Anwendung
    Note over Run: python run.py oder<br/>python -m chatui.main
    Run->>Main: Ausführung beginnt
    Main->>TUI: Erstellt ChatApp()
    TUI->>UI: compose() UI-Komponenten erstellen
    Note over UI: Header, Konversationsbereich,<br/>Eingabefeld, Button, Footer
    TUI->>Conv: on_mount() erstellt Conversation
    Conv-->>TUI: Conversation initialisiert
    TUI->>UI: Fokus auf Eingabefeld setzen

    %% Kommunikationszyklus - Senden einer Nachricht
    User->>UI: Gibt Nachricht ein
    User->>UI: Drückt Enter/klickt Send
    UI->>TUI: Event: on_input_submitted/on_button_pressed
    TUI->>TUI: process_conversation()
    TUI->>UI: UI-Elemente deaktivieren (Feedback)
    TUI->>UI: Benutzernachricht als MessageBox anzeigen
    TUI->>UI: Scrollen zum Konversationsende
    TUI->>Conv: send(message)
    Conv->>Conv: Fügt Nachricht zu messages hinzu
    Conv->>API: Asynchroner API-Aufruf mit Chatverlauf
    Note over API: model: gpt-4o<br/>messages: kompletter Chatverlauf

    %% Kommunikationszyklus - Empfangen einer Antwort
    API-->>Conv: Gibt completion-Objekt zurück
    Conv-->>TUI: Gibt Liste von Antworten zurück
    TUI->>Conv: pick_response(choices[0])
    Conv->>Conv: Fügt Antwort zu messages hinzu
    TUI->>UI: Antwort als MessageBox anzeigen
    TUI->>UI: Scrollen zum Konversationsende
    TUI->>UI: UI-Elemente aktivieren
    
    %% Bereit für die nächste Eingabe
    UI-->>User: Zeigt Antwort, bereit für neue Eingabe

    %% Zusätzliche Funktionen
    rect rgb(240, 240, 240)
        Note right of User: Zusätzliche Funktionen

        User->>UI: Drückt Strg+X (clear)
        UI->>TUI: action_clear()
        TUI->>Conv: clear()
        Conv->>Conv: Löscht messages
        TUI->>UI: Konversationsbereich zurücksetzen

        User->>UI: Drückt Q/Strg+C (quit)
        UI->>TUI: action_quit()
        TUI->>Main: Beendet Anwendung
        Main-->>User: Programm beendet
    end
```

## Klassendiagramm: Anwendungsstruktur

Das folgende Klassendiagramm zeigt die wichtigsten Klassen der Anwendung und ihre Beziehungen:

```mermaid
classDiagram
    class App {
        <<Textual>>
    }
    
    class Widget {
        <<Textual>>
    }
    
    class Container {
        <<Textual>>
    }
    
    class ChatApp {
        -Conversation conversation
        +TITLE: str
        +SUB_TITLE: str
        +CSS_PATH: str
        +BINDINGS: list
        +compose() ComposeResult
        +on_mount() void
        +action_clear() void
        +on_button_pressed() async void
        +on_input_submitted() async void
        +process_conversation() async void
        +toggle_widgets(*widgets) void
    }
    
    class FocusableContainer {
        <<can_focus=True>>
    }
    
    class MessageBox {
        -str text
        -str role
        +__init__(text, role) void
        +compose() ComposeResult
    }
    
    class Conversation {
        -list messages
        -AsyncOpenAI client
        +model: str
        +__init__() void
        +send(message) async list[str]
        +pick_response(choice) void
        +clear() void
    }
    
    App <|-- ChatApp
    Container <|-- FocusableContainer
    Widget <|-- MessageBox
    ChatApp o-- Conversation
    ChatApp o-- FocusableContainer
    ChatApp o-- MessageBox
```

## Ablaufdiagramm: Nachrichtenverarbeitung

Dieses Diagramm zeigt den Ablauf der Nachrichtenverarbeitung in der Anwendung:

```mermaid
flowchart TD
    Start([Benutzereingabe]) --> InputCheck{Eingabe leer?}
    InputCheck -->|Ja| End([Ende])
    InputCheck -->|Nein| DisableUI[UI-Elemente deaktivieren]
    DisableUI --> ShowQuestion[Benutzernachricht anzeigen]
    ShowQuestion --> ClearInput[Eingabefeld leeren]
    ClearInput --> SendToAPI[Sende Nachricht an API]
    SendToAPI --> WaitForResponse[Warte auf API-Antwort]
    WaitForResponse --> ProcessResponse[Verarbeite API-Antwort]
    ProcessResponse --> SelectFirst[Wähle erste Antwort]
    SelectFirst --> AddToHistory[Füge Antwort zum Chatverlauf hinzu]
    AddToHistory --> ShowAnswer[Zeige Antwort im UI]
    ShowAnswer --> EnableUI[UI-Elemente aktivieren]
    EnableUI --> Scroll[Scrolle zum Ende]
    Scroll --> End
```

## Detaillierter Ablaufplan

### Startprozess der Anwendung

1. **Ausführung von run.py** oder **python -m chatui.main**
   - Python lädt das chatui-Paket und dessen Abhängigkeiten
   - Die `main.py` wird ausgeführt und erstellt eine Instanz von `ChatApp`

2. **Initialisierung der ChatApp** (`main.py` → `tui.py`)
   - Die `ChatApp`-Klasse erbt von Textual's `App`
   - Die Methode `compose()` wird aufgerufen, um die UI-Komponenten zu erstellen:
     - Header
     - Konversationsbereich (FocusableContainer)
     - Eingabebereich (Input und Send-Button)
     - Footer mit Tastenkombinationen

3. **Initialisierung der Konversation** (`on_mount` in `tui.py`)
   - Ein `Conversation`-Objekt wird erstellt
   - Der OpenAI-Client wird mit dem API-Schlüssel aus den Einstellungen initialisiert
   - Die Eingabe erhält den Fokus

### Kommunikationszyklus: Senden einer Nachricht

4. **Benutzereingabe**
   - Benutzer gibt Text in das Eingabefeld ein
   - Benutzer drückt Enter oder klickt auf den "Send"-Button

5. **Event-Handling** (`on_button_pressed` oder `on_input_submitted` in `tui.py`)
   - Beide Events leiten zur `process_conversation`-Methode weiter
   - Die Methode prüft, ob die Eingabe nicht leer ist
   - Das Eingabefeld und der Button werden deaktiviert (UI-Feedback)

6. **Anzeigen der Benutzernachricht**
   - Die Benutzernachricht wird als `MessageBox` mit der Rolle "question" erstellt
   - Die MessageBox wird im Konversationsbereich angezeigt
   - Die Scrollposition wird zum Ende des Konversationsbereichs gesetzt
   - Das Eingabefeld wird geleert

7. **Senden der Nachricht an die API** (`process_conversation` in `tui.py` → `send` in `chat.py`)
   - Die Nachricht wird an die `send`-Methode der Conversation-Klasse übergeben
   - Die Nachricht wird dem internen Nachrichtenverlauf (`self.messages`) als Nutzer-Rolle hinzugefügt
   - Ein asynchroner API-Aufruf an OpenAI wird vorbereitet:
     - Das aktuelle Modell wird spezifiziert (gpt-4o)
     - Der gesamte Chatverlauf wird als `messages` mitgesendet
   - Der API-Aufruf wird mit `await` abgewartet

### Kommunikationszyklus: Empfangen einer Antwort

8. **Verarbeitung der API-Antwort** (`send` in `chat.py`)
   - Die API gibt ein `completion`-Objekt zurück
   - Die Methode extrahiert den Textinhalt jeder choice aus dem completion-Objekt
   - Eine Liste von Antworten wird zurückgegeben

9. **Auswahl und Verarbeitung der Antwort** (`process_conversation` in `tui.py`)
   - Die erste Antwort wird automatisch ausgewählt (`choices[0]`)
   - Die ausgewählte Antwort wird an die `pick_response`-Methode der Conversation übergeben
   - `pick_response` fügt die Antwort zum internen Chatverlauf als Assistant-Rolle hinzu

10. **Anzeigen der Antwort**
    - Eine neue `MessageBox` mit der Rolle "answer" wird erstellt
    - Diese Box wird im Konversationsbereich angezeigt
    - Die Scrollposition wird erneut zum Ende gesetzt
    - Das Eingabefeld und der Button werden wieder aktiviert

11. **Bereit für die nächste Eingabe**
    - Der Benutzer kann eine neue Nachricht eingeben
    - Der gesamte Verlauf bleibt erhalten und wird bei zukünftigen API-Aufrufen mitgesendet

### Zusätzliche Funktionen

12. **Konversation löschen** (über die "clear"-Aktion mit Strg+X)
    - Die `clear`-Methode der Conversation wird aufgerufen
    - Die interne Nachrichtenliste wird zurückgesetzt
    - Der Konversationsbereich wird geleert und neu erstellt

13. **Beenden der Anwendung** (über die "quit"-Aktion mit Q oder Strg+C)
    - Die Anwendung wird ordnungsgemäß beendet
    - Alle Ressourcen werden freigegeben