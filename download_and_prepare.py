import os
import urllib.request
import tarfile

def download_and_prepare():
    # Define paths
    base_dir = './database'
    files = [
        'sentences.tar.bz2',
        'links.tar.bz2',
        'tags.tar.bz2',
        'sentences_with_audio.tar.bz2'
    ]

    # Create database directory
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    # Change to database directory
    old_dir = os.getcwd()
    os.chdir(base_dir)

    # Download files
    urls = [
        'https://downloads.tatoeba.org/exports/sentences.tar.bz2',
        'https://downloads.tatoeba.org/exports/links.tar.bz2',
        'https://downloads.tatoeba.org/exports/tags.tar.bz2',
        'https://downloads.tatoeba.org/exports/sentences_with_audio.tar.bz2'
    ]

    for url in urls:
        filename = os.path.basename(url)
        print(f"Downloading {url}.")
        urllib.request.urlretrieve(url, filename)

    # Decompress files
    for file in files:
        if os.path.exists(file):
            print(f"Decompressing {file}.")
            with tarfile.open(file, 'r:bz2') as tar:
                tar.extractall()

    # Prepare files
    def escape_quotes(input_file, output_file):
        with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            for line in infile:
                # Escape quotes
                outfile.write(line.replace('"', '""'))

    def unique_lines(input_file, output_file):
        with open(input_file, 'r', encoding='utf-8') as infile:
            lines = set(infile.readlines())
        with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            outfile.writelines(sorted(lines))

    print("Formatting sentences.csv")
    if os.path.exists('sentences.csv'):
        escape_quotes('sentences.csv', 'sentences.escaped_quotes.csv')
    print("Formatting tags.csv")
    if os.path.exists('tags.csv'):
        escape_quotes('tags.csv', 'tags.escaped_quotes.csv')
    print("Formatting sentences_with_audio.csv")
    if os.path.exists('sentences_with_audio.csv'):
        unique_lines('sentences_with_audio.csv', 'sentences_with_audio.uniq.csv')

    # Clean up
    print("Cleaning up files.")
    for file in files:
        print(f"Removing {file}.")
        os.remove(file)

    os.chdir(old_dir)
