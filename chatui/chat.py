from openai import AsyncOpenAI
from chatui import settings

class Conversation:
    """ChatGPT-Konversationsmanager für die Verwaltung von Chatverläufen und API-Anfragen."""

    # Standard-Modell für die Anfragen an die API
    model: str = "gpt-4o"

    def __init__(self) -> None:
        # Initialisierung der Nachrichtenliste, die den gesamten Chatverlauf enthält
        # Jede Nachricht ist ein Dictionary mit 'role' (Rolle: user oder assistant) und 'content' (Inhalt)
        self.messages: list[dict] = []
        # Asynchronen Client einmalig erstellen
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def send(self, message: str) -> list[str]:
        """
        Sendet eine Benutzernachricht an die ChatGPT-API und gibt mögliche Antworten zurück.
        
        Args:
            message: Die zu sendende Textnachricht des Benutzers
            
        Returns:
            Eine Liste von möglichen Antworten von der KI
        """
        # Fügt die Benutzernachricht dem Chatverlauf hinzu
        self.messages.append({"role": "user", "content": message})
        
        # Sendet eine asynchrone Anfrage an die OpenAI-API mit dem aktuellen Chatverlauf
        # Hier ist await korrekt, da die .create()-Methode von AsyncOpenAI ein Coroutine zurückgibt
        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
        )
        
        # Die API gibt ein Objekt zurück, dessen Eigenschaften wir mit Punktnotation ansprechen
        return [choice.message.content for choice in completion.choices]

    def pick_response(self, choice: str) -> None:
        """
        Wählt eine einzelne Antwort aus den verfügbaren Optionen und 
        fügt sie dem Chatverlauf als Assistentenantwort hinzu.
        
        Args:
            choice: Der ausgewählte Antworttext
        """
        self.messages.append({"role": "assistant", "content": choice})

    def clear(self) -> None:
        """
        Löscht den aktuellen Chatverlauf durch Zurücksetzen der Nachrichtenliste.
        Nützlich, um eine neue Konversation zu beginnen.
        """
        self.messages = []