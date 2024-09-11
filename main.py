import os
import datetime
from shutil import rmtree
import sqlite3
import csv
from query import makeCardsCSV
from download_and_prepare import download_and_prepare
from audio_urls import download_and_rename

DIR_PATH = "./database/"
DB_CONTENTS = set(['date.txt', 'links.csv', 'sentences_with_audio.csv',
                   'sentences_with_audio.uniq.csv', 'sentences.csv',
                   'sentences.escaped_quotes.csv', 'tags.csv', 'tags.escaped_quotes.csv',
                   'tatoeba.sqlite3'])

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
    download_and_prepare()

    # Create a date file to mark the age of the downloaded database.
    today = datetime.date.today()
    year, month, day = today.year, today.month, today.day
    date_text = f"{year} {month} {day}"
    date_file = open("./database/date.txt", "x")
    date_file.write(date_text)
    date_file.close()

    print("Data downloaded from the internet. Next, data will be imported into a database.")

def importDatabase():
    # Create an SQLite database file
    conn = sqlite3.connect('./database/tatoeba.sqlite3')
    c = conn.cursor()

    # Define SQL commands to create tables
    create_tables_sql = """
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS sentences (
        sentence_id INTEGER PRIMARY KEY,
        lang TEXT,
        text TEXT
    );

    CREATE TABLE IF NOT EXISTS sentences_with_audio (
        sentence_id INTEGER,
        audio_id INTEGER,
        username TEXT,
        license TEXT,
        attribution_url TEXT,
        FOREIGN KEY (sentence_id) REFERENCES sentences(sentence_id),
        PRIMARY KEY (sentence_id, audio_id)
    );

    CREATE TABLE IF NOT EXISTS links (
        sentence_id INTEGER,
        translation_id INTEGER,
        FOREIGN KEY (sentence_id) REFERENCES sentences(sentence_id),
        FOREIGN KEY (translation_id) REFERENCES sentences(sentence_id)
    );

    CREATE TABLE IF NOT EXISTS tags (
        sentence_id INTEGER,
        tag_name TEXT,
        FOREIGN KEY (sentence_id) REFERENCES sentences(sentence_id)
    );

    CREATE INDEX IF NOT EXISTS links_index ON links(sentence_id, translation_id);
    CREATE INDEX IF NOT EXISTS tags_index ON tags(sentence_id, tag_name);
    """

    # Execute above SQL commands
    c.executescript(create_tables_sql)
    conn.commit()

    def import_csv_to_db(csv_file, table_name, columns, validate=True, translation=False):
        """
        Given a csv file and an sql table, import the csv file's data into the table.
        """
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')

            # Create an SQLite query to insert data into table based on column names
            query = (f'INSERT OR IGNORE INTO {table_name} ({",".join(columns)}) '
                     f'VALUES ({",".join(["?"] * len(columns))})')

            # for each row in the csv file, insert data into corresponding table
            for data in reader:
                sentence_id = data[0]
                if translation:
                    translation_id = data[1]
                if validate:
                    # Check that it exists in sentences
                    c.execute('SELECT EXISTS(SELECT 1 FROM sentences WHERE sentence_id=?)', (sentence_id,))
                    exists = c.fetchone()[0]

                    if translation:
                        c.execute('SELECT EXISTS(SELECT 1 FROM sentences WHERE sentence_id=?)', (translation_id,))
                        exists = (c.fetchone()[0] and exists)

                    if exists:
                        c.execute(query, data)
                    else:
                        print(f"Skipping row with non-existent sentence_id: {sentence_id}")
                else:
                    c.execute(query, data)
        
        # After all rows are inserted, save data to database.
        conn.commit()

    # Import the csv files into the tables
    import_csv_to_db('database/sentences.escaped_quotes.csv', 'sentences', ['sentence_id', 'lang', 'text'], False)
    print("Finished importing sentences.")
    # Maybe ignore first column?
    import_csv_to_db('database/sentences_with_audio.uniq.csv', 'sentences_with_audio', ['sentence_id', 'audio_id', 'username', 'license', 'attribution_url'])
    print("Finished importing sentences with audio.")
    import_csv_to_db('database/links.csv', 'links', ['sentence_id', 'translation_id'], True, True)
    print("Finished importing sentences links.")
    import_csv_to_db('database/tags.escaped_quotes.csv', 'tags', ['sentence_id', 'tag_name'])
    print("Finished importing sentences tags.")

    # Close the database connection
    conn.close()

    print("Database setup and import completed.")

def main():
    target_lang = input("What is your target language? ")
    
    # Download database if user doesn't already have it, or their copy is too old
    if not checkDatabase():
        input("First, we have to download the data from Tatoeba. Press Enter to continue.")
        downloadTatoebaData()

        print("Now, import the data into a database.")
        importDatabase()

    # Make a CSV file consisting of sentences with target language audio and english translations.
    makeCardsCSV(target_lang, "eng")

    input("Next, we have to download the audio files for the sentences. This may take a while. Press Enter to continue.")
    download_and_rename(target_lang)
    # Lemmatise and sort?
    sort = (input("Do you want to sort the cards? (y/n) ") == 'y' and target_lang == 'mar')
    if sort:
        sortMarathiCards()

if __name__ == "__main__":
    main()