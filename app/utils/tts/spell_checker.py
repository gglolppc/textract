import re
import time

from langdetect import detect
from spellchecker import SpellChecker

# базовые языки
spell_ru = SpellChecker(language="ru")
spell_en = SpellChecker(language="en")

# кэш для новых языков
_spell_cache = {}

def get_spellchecker(lang: str) -> SpellChecker:
    # если язык уже известен
    if lang == "ru":
        return spell_ru
    if lang == "en":
        return spell_en

    # если уже подгружен — берём из кэша
    if lang in _spell_cache:
        return _spell_cache[lang]

    # пробуем создать новый словарь, если поддерживается
    try:
        sc = SpellChecker(language=lang)
        _spell_cache[lang] = sc

        return sc
    except Exception:
        # fallback на английский
        return spell_en


def is_meaningful_text(text: str) -> bool:
    text = text.strip()
    if not text:
        return False

    try:
        lang = detect(text)
    except Exception:
        return False

    spell = get_spellchecker(lang)
    words = [w for w in re.findall(r"[a-zA-Zа-яА-ЯёЁ]+", text.lower()) if len(w) > 2]
    if len(words) < 2:
        return False

    misspelled = spell.unknown(words)
    ratio = (len(words) - len(misspelled)) / len(words)
    return ratio >= 0.4

