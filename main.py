from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from collections import defaultdict
import time
import threading

bot_ready = threading.Event() #to handle opening menu only after bot is connected
notif_active = threading.Event() #notif loop

def setup():
    options = Options()
    options.add_experimental_option("detach", True)
    options.add_argument("--user-data-dir=chrome-data")
    options.add_argument("--no-sandbox")
    #options.add_argument("--headless")
    #options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

#driver.get("https://music.youtube.com")
#print(driver.title)

def scroll_playlist(driver):
    print("Scrolling playlist...")
    prev_count = 0
    same_count = 0

    while same_count<5:  #end of playlist
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);") #executes js to scroll to bottom of page
        time.sleep(5) #wait time

        songs = driver.find_elements(By.CSS_SELECTOR, "ytmusic-responsive-list-item-renderer") #filter based on css selector
        cur_count = len(songs)

        print(f"\rSongs found: {cur_count}", end="")

        if cur_count == prev_count:
            same_count += 1
        else:
            same_count = 0

        prev_count = cur_count

        driver.execute_script("window.scrollBy(0, -200);") #scroll up to deal with partially loaded stuff
        time.sleep(1)

def list_songs(driver, playlist_url):
    try:
        print("Opening playlist")
        driver.get(playlist_url)
        print("Waiting for page to load")
        time.sleep(5)

        scroll_playlist(driver)

        songs = driver.find_elements(By.CSS_SELECTOR, "ytmusic-responsive-list-item-renderer") #ytm-responsive-list-item-renderer is for each song
        print(f"\nExtracting info...")

        for i, song in enumerate(songs, 1):
            try:
                title = None
                artist = None

                #getting title
                try:
                    title = song.find_element(By.CSS_SELECTOR, "yt-formatted-string.title-column").text
                except:
                    try:
                        title = song.find_element(By.CSS_SELECTOR, "[title]").get_attribute("title")
                    except:
                        pass

                #getting artist name
                try:
                    artist = song.find_element(By.CSS_SELECTOR, "yt-formatted-string.flex-column").text
                except:
                    try:
                        res = song.find_elements(By.CSS_SELECTOR, "yt-formatted-string")
                        if len(res)>1:
                            artist = res[1].text #position of artit
                    except:
                        pass

                if title and artist:
                    print(f"{i}, {title} - {artist}")
                else:
                    print(f"{i}. Error -> cannot extract info")

            except Exception as e:
                print(f"{i}. Error extracting song -> {str(e)}")

            if i%50 == 0:
                time.sleep(2) #pause every 50 songs

    except Exception as e:
        print(f"Error occured. {str(e)}")

def find_duplicates(driver, playlist_url):
    try:
        print("Opening playlist")
        driver.get(playlist_url)
        print("Waiting for page to load")
        time.sleep(5)

        scroll_playlist(driver)

        songs = driver.find_elements(By.CSS_SELECTOR, "ytmusic-responsive-list-item-renderer")
        print("\nChecking for duplicates...")

        songs_count = defaultdict(list)

        for i, song in enumerate(songs, 1):
            try:
                title = None
                artist = None

                try:
                    title = song.find_element(By.CSS_SELECTOR, "yt-formatted-string.title-column").text
                except:
                    try:
                        title = song.find_element(By.CSS_SELECTOR, "[title]").get_attribute("title")
                    except:
                        pass

                try:
                    artist = song.find_element(By.CSS_SELECTOR, "yt-formatted-string.flex-column").text
                except:
                    try:
                        res = song.find_elements(By.CSS_SELECTOR, "yt-formatted-string")
                        if len(res)>1:
                            artist = res[1].text
                    except:
                        pass

                if title and artist:
                    k = (title.lower(), artist.lower())
                    songs_count[k].append((i, f"{title} - {artist}"))

            except Exception as e:
                print(f"Error checking song {i}: {str(e)}")

            if i%50 == 0:
                time.sleep(2)

        dup = {k:v for k, v in songs_count.items() if len(v)>1}  #Filtering only duplicates

        if dup:
            print("\n Duplicates found")
            for song, pos in dup.items():
                song_info = pos[0][1]
                pos_list = [str(p[0]) for p in pos]
                print(f"\n{song_info}")
                print(f"Found at positons: {','.join(pos_list)}")
        else:
            print("\nNo duplicates found.")

    except Exception as e:
        print(f"Error finding duplicates: {str(e)}")

def search_song(driver, playlist_url):
    try:
        query = input("Enter song name to search:").lower()

        print("Opening playlist")
        driver.get(playlist_url)
        print("Waiting for page to load")
        time.sleep(5)

        scroll_playlist(driver)

        songs = driver.find_elements(By.CSS_SELECTOR, "ytmusic-responsive-list-item-renderer")
        print("\nProcessing playlist...")

        songs_pos = defaultdict(list) #Storing song positions

        for i, song in enumerate(songs, 1):
            try:
                title = None
                artist = None

                try:
                    title = song.find_element(By.CSS_SELECTOR, "yt-formatted-string.title-column").text
                except:
                    try:
                        title = song.find_element(By.CSS_SELECTOR, "[title]").get_attribute("title")
                    except:
                        pass

                try:
                    artist = song.find_element(By.CSS_SELECTOR, "yt-formatted-string.flex-column").text
                except:
                    try:
                        res = song.find_elements(By.CSS_SELECTOR, "yt-formatted-string")
                        if len(res)>1:
                            artist = res[1].text
                    except:
                        pass

                if title and artist:
                    k = (title.lower(), artist.lower())
                    songs_pos[k].append((i, f"{title}-{artist}"))

            except Exception as e:
                print(f"Error processing {i}: {str(e)}")

            if i%50 == 0:
                time.sleep(2)

        found = False #flag to go through processed songs

        for (title, artist), pos in songs_pos.items():
            if query in title:
                found = True
                song_info = pos[0][1]

                pos_list = [str(p[0]) for p in pos] #all positions where song present
                print(f"\n{song_info}")
                print(f"Found at positions: {','.join(pos_list)}")

        if not found:
            print("\nNot present in playlist")

    except Exception as e:
        print(f"Error searching for song: {str(e)}")

def display(driver, playlist_url):
    while True:
        print("==YTM Manager==")
        print("1.List all songs")
        print("2.List duplicates in the playlist")
        print("3.Search within playlist")
        print("4.Exit")

        choice = int(input("Enter your choice(1-4):"))

        if choice == 1:
            list_songs(driver, playlist_url)
            input("Press enter to continue")

        elif choice == 2:
            find_duplicates(driver, playlist_url)
            input("Press enter to continue")

        elif choice == 3:
            search_song(driver, playlist_url)
            input("Press enter to continue")

        elif choice == 4:
            notif_active.clear()
            print("Exiting program")
            driver.quit()
            break

        else:
            print("Invalid choice")

def main():
    playlist_url = input("Enter playlist URL:")
    driver = setup()

    print("Opening menu...")

    display(driver, playlist_url)

if __name__ == "__main__":
    main()


