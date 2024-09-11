import csv
import os
import sqlite3

output_dir = 'output'
native_langs = []


def native_lang_columns():
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
        global native_langs
        native_langs = natives.split(" ")

        conn = sqlite3.connect(database)
        c = conn.cursor()

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
                        {native_lang_columns()}
        FROM
                        sentences AS target_sentences
        WHERE
                        target_sentences.lang = "{target}" AND
                        target_sentences.sentence_id IN (SELECT sentence_id FROM sentences_with_audio)
        ;
        """
        if not os.path.exists('output'):
                os.makedirs('output')
        with open(f'{os.path.join(output_dir, target)} → {natives}.csv', 'w', newline='', encoding='utf-8') as csvfile:
                out = csv.writer(csvfile, delimiter='\t',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
                for row in c.execute(query):
                        out.writerow(row)

        conn.close()


if __name__ == '__main__':
        makeCardsCSV('fin', 'eng rus ita')