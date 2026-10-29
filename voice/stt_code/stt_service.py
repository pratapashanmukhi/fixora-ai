import speech_recognition as sr


class STTService:
    """Speech-to-Text service using SpeechRecognition and Google Web Speech."""

    def __init__(self, ambient_noise_duration: float = 1.0):
        self.recognizer = sr.Recognizer()
        self.ambient_noise_duration = ambient_noise_duration
        self.available = True
        self.last_error = ""

    def listen(self) -> str:
        """Record one utterance and return normalized text, or an empty string."""
        try:
            with sr.Microphone() as source:
                print("\nListening...")
                self.recognizer.adjust_for_ambient_noise(
                    source, duration=self.ambient_noise_duration
                )
                audio = self.recognizer.listen(source)

            text = self.recognizer.recognize_google(audio)
            print(f"USER: {text}")
            return text.lower().strip()

        except (sr.UnknownValueError, sr.WaitTimeoutError):
            self.last_error = "Speech could not be understood."
            return ""

        except sr.RequestError as error:
            self.available = False
            self.last_error = f"Speech recognition service is unavailable: {error}"
            print(f"[STTService] {self.last_error}")
            return ""

        except (OSError, AttributeError) as error:
            self.available = False
            self.last_error = f"Microphone is unavailable: {error}"
            print(f"[STTService] {self.last_error}")
            return ""

        except Exception as error:
            self.available = False
            self.last_error = f"Unable to record audio: {error}"
            print(f"[STTService] {self.last_error}")
            return ""


if __name__ == "__main__":
    print("FIXORA STT test: speak a short phrase into the microphone.")
    result = STTService().listen()
    print(f"Recognized: {result!r}" if result else "No speech recognized.")