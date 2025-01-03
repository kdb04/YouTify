import discord
from discord.ext import tasks
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from dotenv import load_dotenv
import os

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_TOKEN')
PLAYLIST_URL = os.getenv('PLAYLIST_URL')

#Bot setup
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install(), options=chrome_options))

def scrape_playlist():
    driver = get_driver()
    driver.get(PLAYLIST_URL)
    time.sleep(5)  # Wait for the page to load

    song_elements = driver.find_elements(By.CSS_SELECTOR, "ytmusic-responsive-list-item-renderer")
    songs = [song.text.split("\n")[0] for song in song_elements]  # Get song names
    driver.quit()
    return set(songs)

# Global variables to track playlist changes
previous_songs = set()
is_scraping = False
initial_songs = set()
scraped_songs = set()
removed_songs = set()

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    if not playlist_monitor.is_running():
        playlist_monitor.start()  # Start the playlist monitoring loop

@client.event
async def on_message(message):
    global is_scraping, initial_songs, scraped_songs, removed_songs

    #start scraping
    if message.content.lower() == "!start":
        if is_scraping:
            await message.channel.send("The bot is already monitoring the playlist!")
        else:
            is_scraping = True
            initial_songs = scrape_playlist()  #init state
            scraped_songs.clear()  # reset
            removed_songs.clear()
            await message.channel.send("Started monitoring the playlist for new and removed songs!")

    #stop scraping
    elif message.content.lower() == "!stop":
        if is_scraping:
            is_scraping = False
            await message.channel.send("Stopped monitoring the playlist.")
        else:
            await message.channel.send("The bot is not currently monitoring the playlist.")

    #check added songs
    elif message.content.lower() == "!added":
        if scraped_songs:
            await message.channel.send(f"**Songs added during this session:**\n" + "\n".join(scraped_songs))
        else:
            await message.channel.send("No new songs were added during this session.")

    #check removed songs
    elif message.content.lower() == "!removed":
        if removed_songs:
            await message.channel.send(f"**Songs removed during this session:**\n" + "\n".join(removed_songs))
        else:
            await message.channel.send("No songs were removed during this session.")

@tasks.loop(seconds=30)  #checking updates
async def playlist_monitor():
    global is_scraping, initial_songs, scraped_songs, removed_songs

    if is_scraping:
        current_songs = scrape_playlist()
        added_songs = current_songs - initial_songs  #new songs
        removed_songs = initial_songs - current_songs  #removed songs

        scraped_songs.update(added_songs)
        removed_songs.update(removed_songs)
        initial_songs = current_songs

client.run(DISCORD_BOT_TOKEN)
