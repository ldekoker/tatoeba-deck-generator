import os
import datetime
import subprocess
from shutil import rmtree

DIR_PATH = "./database/"
DB_CONTENTS = set(['date.txt', 'links.csv', 'sentences_with_audio.csv',
                   'sentences_with_audio.uniq.csv', 'sentences.csv',
                   'sentences.escaped_quotes.csv', 'tags.csv', 'tags.escaped_quotes.csv'])

def checkDirExists(path):
    return os.path.exists(path)

def checkDatabase():
    """
    Checks if the user already has the tatoeba database, and that if they do it isn't too old.
    """
    # Check if database folder exists
    if checkDirExists(DIR_PATH):
        contents = os.listdir(DIR_PATH)

        # Check if it has the database files
        if set(contents) != DB_CONTENTS:
            return False
        else:
            # Check if the files are more than 6 months old
            file = open(f'{DIR_PATH}date.txt', 'r')
            date = datetime.date(*[int(n) for n in file.read().split(" ")])
            today = datetime.date.today()
            date_difference = (today - date).days

            if date_difference > (6*28):
                return False
            else:
                return True
    else:
        return False

def downloadDatabase():
    """
    Downloads the database.
    """
    if checkDirExists(DIR_PATH):
        rmtree(DIR_PATH)
    
    subprocess.run(['wsl', 'bash', 'download_and_prepare.sh'], check=True)

    # create date file
    today = datetime.date.today()
    year, month, day = today.year, today.month, today.day
    date_text = f"{year} {month} {day}"
    date_file = open("./database/date.txt", "x")
    date_file.write(date_text)
    date_file.close()


def main():
    # Download database if user doesn't already have it, or their copy is too old
    if not checkDatabase():
        downloadDatabase()
    
    # Make query
    # Download audio files
    # Lemmatise and sort?

if __name__ == "__main__":
    main()