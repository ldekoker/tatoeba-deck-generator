import sqlite3
import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_audio_urls(target_lang, database="./database/tatoeba.sqlite3"):
    base_dir = './output/audio'

    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

        conn = sqlite3.connect(database)
        c = conn.cursor()

        query = f"""
        SELECT sentence_id
        FROM sentences
        WHERE lang = '{target_lang}' AND sentence_id IN (SELECT sentence_id FROM sentences_with_audio)
        """

        audio_urls = []
        for row in c.execute(query):
                audio_url = f"https://audio.tatoeba.org/sentences/{target_lang}/{row[0]}.mp3"
                audio_urls.append(audio_url)

        conn.close()
        return audio_urls
    
def download_audio(url, directory):
      """Download a single audio file using requests."""
      local_filename = os.path.join(directory, url.split('/')[-1])
      try:
            with requests.get(url, stream=True) as r:
                  r.raise_for_status()
                  with open(local_filename, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                              f.write(chunk)
            return local_filename
      except requests.RequestException as e:
            print(f"Failed to download {url}: {e}")
            return None
      
def rename_files(lang_code):
      """Rename the downloaded audio files to include the language code."""
      audio_dir = "./output/audio/"
      for f in os.listdir(audio_dir):
            old_path = os.path.join(audio_dir, f)
            new_filename = f"tatoeba_{lang_code}_" + f
            new_path = os.path.join(audio_dir, new_filename)
            os.rename(old_path, new_path)

def download_and_rename(lang_code, max_workers=8, database='./database/tatoeba.sqlite3'):
    """Download audio files in parallel and rename them."""
    # Get audio URLs
    audio_urls = get_audio_urls(lang_code, database)

    # Create output directory if it doesn't exist
    os.makedirs('./output/audio/', exist_ok=True)

    # Download audio files in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(download_audio, url, './output/audio/') for url in audio_urls]
        for future in as_completed(futures):
            downloaded_file = future.result()
            if downloaded_file:
                print(f"Downloaded: {downloaded_file}")

    rename_files(lang_code)