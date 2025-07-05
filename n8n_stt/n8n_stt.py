import asyncio
import httpx
import tempfile
import wave
import os
import logging

from wyoming.server import AsyncTcpServer, AsyncEventHandler
from wyoming.asr import Transcript
from wyoming.event import Event
from wyoming.info import Info, AsrProgram, AsrModel, Attribution

N8N_WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL", "YOUR_N8N_WEBHOOK_URL_HERE")

class N8nSTTHandler(AsyncEventHandler):
    """
    Wyoming AsyncEventHandler that receives audio, sends it to n8n, and returns the transcription.
    """
    def __init__(self, reader, writer):
        super().__init__(reader, writer)
        self.audio_data = b""
        self.audio_rate = 16000
        self.audio_width = 2
        self.audio_channels = 1

    async def handle_event(self, event):

        if event.type == "transcribe":
            logging.info("Transcribe received: will start recording.")
            self.transcribe_requested = True
            self.audio_data = b""  # reset audio buffer

        elif event.type == "audio-start":
            self.audio_rate = event.data["rate"]
            self.audio_width = event.data["width"]
            self.audio_channels = event.data["channels"]
            #logging.info(f"AudioStart: rate={self.audio_rate}, width={self.audio_width}, channels={self.audio_channels}")

        elif event.type == "audio-chunk":
            self.audio_data += event.payload

        elif event.type == "audio-stop":
            if getattr(self, "transcribe_requested", False):
                
                logging.info(f"AudioStop received. Starting transcription of {len(self.audio_data)} bytes.")

                text = await self.transcribe_with_n8n(
                    self.audio_data, self.audio_rate, self.audio_width, self.audio_channels
                )

                if text is None:
                    logging.info("Transcription failed or empty.")
                    await self.write_event(Transcript(text="").event())
                else:
                    logging.info(f"Transcription: '{text}'")
                    await self.write_event(Transcript(text=text).event())

                # reset
                self.audio_data = b""
                self.transcribe_requested = False

                return False  # Close connection after transcription
            else:
                logging.info("AudioStop received without transcribe request. Ignoring.")
                self.audio_data = b""

        elif event.type == "describe":
            
            #logging.info("Describe received, sending info response...")

            info_event = Info(
                asr=[
                    AsrProgram(
                        name="n8n-stt",
                        description="STT via n8n + Whisper",
                        attribution=Attribution(
                            name="n8n + Whisper via webhook",
                            url="https://n8n.io/"
                        ),
                        installed=True,
                        version="1.0",
                        models=[
                            AsrModel(
                                name="whisper-openai",
                                description="Transcriber Whisper via n8n webhook",
                                attribution=Attribution(
                                    name="OpenAI Whisper",
                                    url="https://github.com/openai/whisper"
                                ),
                                installed=True,
                                version="2025.07.01",
                                languages=["it"]
                            )
                        ]
                    )
                ]
            )

            await self.write_event(info_event.event())

        elif isinstance(event, Event):
            
            logging.debug(f"type(event): {type(event)}")
            logging.debug(f"Generic Wyoming event received: {event.type}")

        else:
            logging.debug(f"Unhandled Wyoming event: {type(event)}")

        return True

    async def transcribe_with_n8n(self, audio_bytes, rate, width, channels):
        temp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                temp_file_path = tmp.name
                wav_writer = wave.open(tmp, 'wb')
                wav_writer.setnchannels(channels)
                wav_writer.setsampwidth(width)
                wav_writer.setframerate(rate)
                wav_writer.writeframes(audio_bytes)
                wav_writer.close()
            
            logging.debug(f"Temporary WAV file: {temp_file_path}")

            async with httpx.AsyncClient() as client:
                with open(temp_file_path, "rb") as f:
                    files = {"file": ("audio.wav", f, "audio/wav")}
                    
                    logging.debug(f"Sending to n8n: {N8N_WEBHOOK_URL}")

                    resp = await client.post(N8N_WEBHOOK_URL, files=files, timeout=30)
                    resp.raise_for_status()
                    data = resp.json()
                    
                    logging.debug(f"n8n response: {data}")
                    
                    return data.get("text")
        except httpx.HTTPStatusError as e:
            logging.error(f"n8n HTTP error (Status: {e.response.status_code}): {e.response.text}")
            return None
        except httpx.RequestError as e:
            logging.error(f"n8n network/timeout error: {e}")
            return None
        except Exception as e:
            logging.error(f"Generic n8n transcription error: {e}")
            return None
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                logging.debug(f"Temporary file removed: {temp_file_path}")


async def main():
    logging.basicConfig(level=logging.INFO)
    host = "0.0.0.0"
    port = 10300
    server = AsyncTcpServer(host, port)
    logging.info(f"Starting Wyoming n8n-STT server on {host}:{port}")
    await server.run(lambda r, w: N8nSTTHandler(r, w))

if __name__ == "__main__":
    asyncio.run(main())
