# translations.py
import csv

TRANSLATIONS = {}

def load_translations(path='_static/global/translations.csv'):
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row['key']
            TRANSLATIONS[key] = {lang: row[lang] for lang in row if lang != 'key'}

load_translations()

def get_translation(key, lang='en', **kwargs):
    template = TRANSLATIONS.get(key, {}).get(lang, f"[{key}]")
    if kwargs:
        return template.format(**kwargs)
    return template  # Leave as-is if no values passed