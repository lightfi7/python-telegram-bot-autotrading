import json

with open('./lang/lang.json', 'r') as file:
    translations = json.load(file)


def translate(key, lang='en'):
    return translations[lang][key]
