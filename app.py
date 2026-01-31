import sys
import asyncio
import pyttsx3
from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent
from collections import deque

if len(sys.argv) < 2:
    print("Uso: python apptts.py <tiktok_username>")
    sys.exit(1)

USERNAME = sys.argv[1]

chat_queue = asyncio.Queue()
client = TikTokLiveClient(unique_id=USERNAME)

# Guardamos los últimos mensajes leídos (anti-duplicados)
seen_messages = deque(maxlen=200)


def speak(text: str):
    engine = pyttsx3.init()
    engine.setProperty("rate", 175)
    engine.say(text)
    engine.runAndWait()
    engine.stop()


@client.on(CommentEvent)
async def on_comment(event: CommentEvent):
    msg_id = f"{event.user.unique_id}:{event.comment}"

    # ❌ si ya lo vimos, lo ignoramos
    if msg_id in seen_messages:
        return

    seen_messages.append(msg_id)

    await chat_queue.put(
        f"{event.user.nickname} dice {event.comment}"
    )


async def consume_queue():
    loop = asyncio.get_running_loop()

    while True:
        text = await chat_queue.get()
        print(text)

        await loop.run_in_executor(None, speak, text)
        chat_queue.task_done()


async def main():
    consumer_task = asyncio.create_task(consume_queue())
    await client.start()
    await consumer_task


asyncio.run(main())
