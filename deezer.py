import requests
import pygame
from unidecode import unidecode
import os
import re
from bs4 import BeautifulSoup
import auth
import appdirs
import datetime
import gui
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import sys
import argparse
import sub
from pathlib import Path
import crypto
import datetime
import time


# Variables
APP_NAME = 'speakDeezer'
appdata_dir = Path.home() / 'AppData' / 'Local' / 'speakDeezer'
HISTORY_FILE = appdata_dir/'history.txt'
USER_FILE = os.path.join(appdirs.user_data_dir(APP_NAME), 'users.txt')
API_BASE_URL = "https://api.deezer.com/"
USERNAME = auth.get_current_user()


def log_history(input_str):
    # get current timestamp
    if not os.path.exists(HISTORY_FILE):
        # create history file if it doesn't exist
        with open(HISTORY_FILE, 'w') as hf:
            hf.write('')
    
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # log user input to history file
    with open(HISTORY_FILE, 'a') as hf:
        hf.write(f'{timestamp}: {USERNAME} - {input_str}\n')

def search_song(query):
    log_history(query)
    url = f"https://api.deezer.com/search?q={query}"
    response = requests.get(url)
    log_history(response)
    return response.json()

def select_song(search_results):
    print("Select a song from the list:")
    for i, song in enumerate(search_results["data"]):
        print(f"{i + 1}. {song['title']} by {song['artist']['name']}")
    while True:
        try:
            user_choice = int(input("Enter the number of your choice: ")) - 1
            if user_choice < 0 or user_choice >= len(search_results["data"]):
                print("Invalid choice. Please try again.")
            else:
                return search_results["data"][user_choice]
        except ValueError:
            print("Invalid input. Please enter a number.")

def download_song(song):
    song_url = song["preview"]
    response = requests.get(song_url)
    if response.status_code != 200:
        print(f"Failed to download song {song['title']} - Status code: {response.status_code}")
        return None
    filename = f"{song['title']}.mp3"

    try:
        music_dir = os.path.join(os.path.expanduser("~"), "Music")
        os.makedirs(music_dir, exist_ok=True)
        filepath = os.path.join(music_dir + "/speakDeezer/", filename)
        with open(filepath, "wb") as f:
            f.write(response.content)
    except IOError:
        print(f"Failed to write song {song['title']} to file")
        return None
    return filepath

def play_song(filename):
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
    except Exception as e:
        print(e)

def search_and_play():
    query = input("Enter the name of the song you want to search: ")
    search_results = search_song(query)
    if len(search_results["data"]) == 0:
        print("No results found.")
    else:
        selected_song = select_song(search_results)
        print(f"Now downloading {selected_song['title']} by {selected_song['artist']['name']}...")
        filename = download_song(selected_song)
        print(filename)
        play_song(filename)

def select_song_for_lyrics():
    query = input("Enter the name of the song for which you want to see the lyrics: ")
    search_results = search_song(query)
    if "data" not in search_results:
        print("An error occurred while retrieving the search results.")
        return None
    elif len(search_results["data"]) == 0:
        print("No results found.")
        return None
    else:
        selected_song = select_song(search_results)
        return selected_song

def sanitize_name(name):
    """Removes all non-alphabetic characters from a string."""
    return re.sub(r'[^a-zA-Z]', '', name)

def show_lyrics():
    song = select_song_for_lyrics()
    if song:
        title = song["title"]
        artist = unidecode(song["artist"]["name"]).lower().replace(" ", "")
        title_normalized = unidecode(title).lower().replace(" ", "")
        print(f"Lyrics for {title} by {song['artist']['name']}:")
        url = f"https://www.azlyrics.com/lyrics/{artist}/{title_normalized}.html"
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            print("An error occurred while retrieving the lyrics.")
            return None
        soup = BeautifulSoup(response.content, "html.parser")
        lyrics_div = soup.find("div", class_=False, id=False)
        if lyrics_div:
            lyrics = lyrics_div.get_text().strip()
            print(lyrics)
        else:
            print("Lyrics not found.")


def search_songs_by_artist(artist):
    response = requests.get(f"{API_BASE_URL}/search?q={artist}&limit=20&type=artist")
    if response.status_code == 200:
        data = response.json()["data"]
        if len(data) > 0:
            artist_data = data[0].get("artist", None)
            if artist_data:
                artist_id = artist_data.get("id", None)
                if artist_id:
                    songs_response = requests.get(f"{API_BASE_URL}/artist/{artist_id}/top?limit=20")
                    if songs_response.status_code == 200:
                        songs = songs_response.json().get("data", None)
                        if songs:
                            if len(songs) > 0:
                                return songs
                            else:
                                print(f"No songs found for artist {artist}.")
                        else:
                            print(f"Error: Could not retrieve songs for artist {artist}.")
                    else:
                        print(f"Error: Could not retrieve songs for artist {artist}.")
                else:
                    print(f"Error: Artist ID not found for artist {artist}.")
            else:
                print(f"Error: Artist data not found for artist {artist}.")
        else:
            print(f"No artist found with name {artist}.")
    else:
        print("Error retrieving search results.")


        
        
def search_songs_by_genre(genre):
    response = requests.get(f"{API_BASE_URL}/search?q={genre}&limit=20&type=genre")
    if response.status_code == 200:
        try:
            data = response.json()["data"]
        except KeyError:
            print(f"Error parsing response data for genre {genre}.")
            return None
        if len(data) > 0:
            genre_id = data[0]["id"]
            songs_response = requests.get(f"{API_BASE_URL}/genres/{genre_id}/songs?limit=20")
            if songs_response.status_code == 200:
                try:
                    songs = songs_response.json()["data"]
                except KeyError:
                    print(f"Error parsing response data for songs in genre {genre}.")
                    return None
                if len(songs) > 0:
                    return songs
                else:
                    print(f"No songs found for genre {genre}.")
            else:
                print(f"Error retrieving songs for genre {genre}.")
        else:
            print(f"No genre found with name {genre}.")
    else:
        print("Error retrieving search results.")


def play_songs_by_artist():
    artist_name = input("Enter the name of the artist: ")
    songs = search_songs_by_artist(artist_name)
    if songs is None:
        print(f"Error: Could not retrieve songs by {artist_name}.")
        return
    elif not songs:
        print(f"No songs found by {artist_name}.")
        return
    
    print(f"Found {len(songs)} songs by {artist_name}:")
    for i, song in enumerate(songs):
        print(f"{i + 1}. {song['title']} by {song['artist']['name']}")

    try:
        song_choice = int(input("Enter the number of the song you want to play: "))
    except ValueError:
        print("Invalid input. Please enter a number.")
        return
    
    if song_choice < 1 or song_choice > len(songs):
        print("Invalid song choice.")
        return
    
    song = songs[song_choice - 1]
    play_song(download_song(song))


def play_songs_by_genre():
    genre_name = input("Enter the name of the genre: ")
    log_history(f"{genre_name}")
    songs = search_songs_by_genre(genre_name)
    if not songs:
        print(f"No songs found in the {genre_name} genre.")
        return
    print(f"Found {len(songs)} songs in the {genre_name} genre:")
    for i, song in enumerate(songs):
        print(f"{i + 1}. {song['title']} by {song['artist']['name']}")
        log_history(f"{i + 1}. {song['title']} by {song['artist']['name']}")
    try:
        song_choice = int(input("Enter the number of the song you want to play: "))
        if song_choice < 1 or song_choice > len(songs):
            print("Invalid song choice.")
            log_history("Invalid song choice.")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        log_history("Invalid input. Please enter a number.")
        return
    song = songs[song_choice - 1]
    play_song(song)


def show_recommendations():
    print("Recommendations are not available at this time.")

def exit_program():
    print("Exiting program.")
    pygame.mixer.music.stop()
    pygame.quit()
    quit()
    


def main(user):
    
        
    pygame.init()
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"Welcome {user}, what would you like to do?\n")
        print("1. Search for a song and play it")
        print("2. Show song lyrics")
        print("3. Show youre recommendations")
        print("4. Play songs by artist")
        print("5. Play songs by genre")
        print("6. Exit program")
        print(f"\nLogout({user} - {sub.check_subscription(user)})")
        sub.write_subscriptions()
        try:
            user_choice = int(input("Enter the number of your choice: "))
            if user_choice == 1:
                log_history(f"{user_choice}")
                search_and_play()
                input("Press Enter to continue...")
                os.system('cls' if os.name == 'nt' else 'clear')
            elif user_choice == 2:
                log_history(f"{user_choice}")
                show_lyrics()
                input("Press Enter to continue...")
                os.system('cls' if os.name == 'nt' else 'clear')
            elif user_choice == 3:
                log_history(f"{user_choice}")
                show_recommendations()
                input("Press Enter to continue...")
                os.system('cls' if os.name == 'nt' else 'clear')
            elif user_choice == 4:
                log_history(f"{user_choice}")
                play_songs_by_artist()
                input("Press Enter to continue...")
                os.system('cls' if os.name == 'nt' else 'clear')
            elif user_choice == 5:
                log_history(f"{user_choice}")
                print("This featute is not available at this time.")
            elif user_choice == 6:
                exit_program()
                break
            elif user_choice == 7:
                log_history(f"{user_choice}")
                python = sys.executable
                os.execl(python, python, *sys.argv)
                auth.logout()
            elif user_choice == 69:
                history_folder = os.path.dirname(HISTORY_FILE)
                os.startfile(history_folder)
                break
            elif user_choice == 68:
                try:
                    print(os.path.join(appdirs.user_data_dir(APP_NAME), 'users.txt'))
                    input("Press Enter to continue...")
                except Exception as e:
                    print(e)
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def boot_up_animation():
    print("Starting Deezer Player...")
    time.sleep(0.1)
    print("\nLoading...\n")
    animations = ["|/-\\", "▖▘-◑-▗", "◢◣◤◥", "▌▄▐▀", "╰( ⁰ ਊ ⁰ )━☆ﾟ.*･｡ﾟ"]
    animation_idx = 0
    api_available = check_api_availability()
    while not api_available:
        animation = animations[animation_idx % len(animations)]
        print("Checking API availability " + animation, end="\r")
        animation_idx += 1
        time.sleep(0.1)
        api_available = check_api_availability()
    print("\nAPI is ready!")
    music_dir = os.path.join(os.path.expanduser("~"), "Music")
    if not os.path.exists(music_dir + "/speakDeezer/"):
        os.makedirs(music_dir + "/speakDeezer/")
        print("Created 'speakDezzer' directory for storing songs/lysrics/playlist and keys.")

    input("Press Enter to continue...")
    os.system('cls' if os.name == 'nt' else 'clear')

def create_playlist(username, playlist_name):
    """Creates a new playlist for the user with the given username."""
    # Save the playlist to a file or database associated with the username
    pass

def save_playlist(username, playlist_name):
    """Saves an existing playlist for the user with the given username."""
    # Save the playlist to a file or database associated with the username
    pass

def load_playlist(username, playlist_name):
    """Loads a playlist for the user with the given username."""
    # Load the playlist from a file or database associated with the username
    pass


def check_api_availability(base_url=API_BASE_URL):
    try:
        response = requests.get(f"{base_url}/ping")
        response.raise_for_status()
        print("Deezer API is available.")
        return True
    except requests.exceptions.RequestException:
        print("Deezer API is not available.")
        return False
    


def login():

        while True:
            
            
             # check if user is logged in
            current_user = auth.get_current_user()
            if not current_user:
                # prompt user to log in or register
                while True:
                    choice = input('Please log in (1) or register (2): ')
                    if choice == '1':
                        # prompt user to enter username and password
                        username = input('Username: ')
                        password = input('Password: ')
                        # log in user
                        if auth.login(username, password):
                            USERNAME = current_user
                            return username
                            break
                    elif choice == '2':
                        # prompt user to enter desired username and password
                        username = input('Desired username: ')
                        password = input('Desired password: ')
                        # register user
                        if auth.register(username, password):
                            USERNAME = current_user
                            return username
                            break
                    else:
                        print('Invalid choice')
                        
            else:
                USERNAME = current_user
                return current_user
if __name__ == '__main__':
    os.system("title speakDeezer")
    parser = argparse.ArgumentParser(description='speakDeezer')
    parser.add_argument('query', nargs='?', help='search query or track id')
    parser.add_argument('--gui', action='store_true', help='start with GUI')
    args = parser.parse_args()
    if(args.gui):
        app = QApplication([])
        window = gui.App()
        app.exec_()
    else:
        os.system('cls' if os.name == 'nt' else 'clear')
        boot_up_animation()
        main(login())

