import os
import datetime
import subprocess
from shutil import rmtree

DIR_PATH = "./database/"
DB_CONTENTS = set(['date.txt', 'links.csv', 'sentences_with_audio.csv',
                   'sentences_with_audio.uniq.csv', 'sentences.csv',
                   'sentences.escaped_quotes.csv', 'tags.csv', 'tags.escaped_quotes.csv'])

def checkPathExists(path):
    """
    Returns True if the given path exists.
    """
    return os.path.exists(path)

def checkDatabase():
    """
    Checks if the user already has the tatoeba database, and that if they do it isn't too old.
    """
    # Check if database folder exists
    if checkPathExists(DIR_PATH):
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

def downloadTatoebaData():
    """
    Downloads the database.
    """
    # If the path to the database already exists, then it must be incomplete or
    # more than 6 months old, so it must be deleted and replaced.
    if checkPathExists(DIR_PATH):
        rmtree(DIR_PATH)
    
    # Run the shell commands to download all of the files.
    subprocess.run(['wsl', 'bash', 'download_and_prepare.sh'], check=True)

    # Create a date file to mark the age of the downloaded database.
    today = datetime.date.today()
    year, month, day = today.year, today.month, today.day
    date_text = f"{year} {month} {day}"
    date_file = open("./database/date.txt", "x")
    date_file.write(date_text)
    date_file.close()

    print("Data downloaded from the internet. Next, data will be imported into a database.")

def main():
    # Download database if user doesn't already have it, or their copy is too old
    if not checkDatabase():
        downloadTatoebaData()
    
    # Make query
    # Download audio files
    # Lemmatise and sort?

if __name__ == "__main__":
    main()