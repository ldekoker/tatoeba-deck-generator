import csv
import os
import sqlite3

def native_lang_columns(native_langs):
    """
    Create an SQL query for each of the given native languages. Will be inserted into the makeCardsCSV query.
    """
    def native_lang_column(lang):
        return f"""
        "<ul class=""translations""><li>" ||
        (
            SELECT group_concat(sentences.text, "</li><li>")
            FROM links JOIN sentences
            ON
                links.translation_id = sentences.sentence_id
            WHERE
                links.sentence_id = target_sentences.sentence_id
                AND
                sentences.lang = '{lang}'
                )
        || "</li></ul>"
        """
    result = ""
    for lang in native_langs[:-1]:
        result += native_lang_column(lang) + ", "
    result += native_lang_column(native_langs[-1])
    return result

def makeCardsCSV(target, natives, database="./database/tatoeba.sqlite3"):    
    """
    Queries the SQLite database to generate a csv composed of target language sentences, with audio, that have native language translations.
    """
    native_langs = natives.split(" ")

    conn = sqlite3.connect(database)
    c = conn.cursor()

    # Create the SQL Query
    query = f"""
    SELECT
        target_sentences.sentence_id,
        target_sentences.text,
        "[sound:tatoeba_" || "{target}" || "_" || target_sentences.sentence_id || ".mp3]",
        "<ul class=""tags""><li>" ||
        (
            SELECT group_concat(tag_name, "</li><li>")
            FROM tags
            WHERE tags.sentence_id = target_sentences.sentence_id
        )
        || "</li></ul>",
        {native_lang_columns(native_langs)}
    FROM
        sentences AS target_sentences
    WHERE
        target_sentences.lang = "{target}" AND
        target_sentences.sentence_id IN (SELECT sentence_id FROM sentences_with_audio)
    ;
    """
    # Make an output directory
    if not os.path.exists('output'):
        os.makedirs('output')

    # Create the CSV in the output directory
    output_dir = 'output'
    with open(f'{os.path.join(output_dir, target)} → {natives}.csv', 'w', newline='', encoding='utf-8') as csvfile:
        out = csv.writer(csvfile, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)

        for row in c.execute(query):
            out.writerow(row)

    conn.close()

if __name__ == '__main__':
        makeCardsCSV('fin', 'eng rus ita')