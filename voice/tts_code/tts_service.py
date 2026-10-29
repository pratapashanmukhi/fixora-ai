import pyttsx3


class TTSService:
    """Text-to-Speech service using the local pyttsx3 system engine."""

    def __init__(
        self,
        rate: int = 150,
        volume: float = 1.0,
        voice_gender: str = "female",
    ):
        self.engine = None
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", rate)
            self.engine.setProperty("volume", volume)

            voices = self.engine.getProperty("voices")
            if voices:
                preferred = [
                    voice for voice in voices
                    if voice_gender.lower() in (voice.name + voice.id).lower()
                ]
                selected = preferred[0] if preferred else voices[0]
                self.engine.setProperty("voice", selected.id)
        except Exception as error:
            print(f"[TTSService] Text-to-speech is unavailable: {error}")

    def speak(self, text: str) -> None:
        print(f"FIXORA: {text}")
        if self.engine is None:
            return
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as error:
            print(f"[TTSService] Could not play speech: {error}")

    def stop(self) -> None:
        if self.engine is not None:
            self.engine.stop()


if __name__ == "__main__":
    TTSService().speak("Hello. This is a FIXORA text-to-speech test.")