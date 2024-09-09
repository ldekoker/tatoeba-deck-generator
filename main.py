import os
import datetime

DIR_PATH = "./database/"
DB_CONTENTS = ['date.txt', 'dingus.txt',]

def checkDatabase():
    """
    Checks if the user already has the tatoeba database, and that if they do it isn't too old.
    """
    # Check if database folder exists
    if os.path.exists(DIR_PATH):
        contents = os.listdir(DIR_PATH)

        # Check if it has the database files
        if contents != DB_CONTENTS:
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

def main():
    # Download database if user doesn't already have it, or their copy is too old
    if not checkDatabase():
        # download
        print('p')
    
    # Make query
    # Download audio files
    # Lemmatise and sort?

if __name__ == "__main__":
    main()