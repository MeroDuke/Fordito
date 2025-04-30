# ⚠️ Ezt a fájlt nem használjuk többé, mert a script betöltése automatikusan API-hívást generál.
# Ez a teszt pénzbe kerülhet, így az automatikus tesztelésből végleg kizárásra került.
# Lásd: FORDITO-77 döntés.

# A build_contextual_prompt() funkciót manuálisan, izolált környezetben lehet tesztelni külön modulba másolással.

# Ez a tesztfájl szándékosan üres.

#import os
#import sys
#import importlib.util
#from unittest.mock import MagicMock

#CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
#PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
#sys.path.insert(0, PROJECT_DIR)

#module_path = os.path.join(PROJECT_DIR, "bin", "03_OpenAI_API_ONLY_4-Turbo_translate_ass.py")
#spec = importlib.util.spec_from_file_location("translate_module", module_path)
#translate_module = importlib.util.module_from_spec(spec)
#spec.loader.exec_module(translate_module)

# Blokkoljuk az esetleges OpenAI API-hívásokat (ha lennének)
#if hasattr(translate_module, "openai"):
#    translate_module.openai.ChatCompletion.create = MagicMock(side_effect=Exception("Blocked API call during test"))

#def test_build_contextual_prompt_minimal():
#    translate_module.CONTEXT_DATA = {}
#    prompt = translate_module.build_contextual_prompt("|||")
#    assert isinstance(prompt, str)
#    assert "You are a professional translator" in prompt
#    assert "|||" in prompt

#def test_build_contextual_prompt_full():
#    translate_module.CONTEXT_DATA = {
#        "synopsis": "A secret war between vampires and humans.",
#        "genres": ["Action", "Supernatural"],
#        "characters": [
#            {"name": "Alice", "name_japanese": "アリス"},
#            {"name": "Bob", "name_japanese": "ボブ"}
#        ]
#    }
#    prompt = translate_module.build_contextual_prompt("|||")
#    assert "Anime synopsis: A secret war between vampires and humans." in prompt
#    assert "Genres: Action, Supernatural" in prompt
#    assert "Character list: Alice (アリス), Bob (ボブ)" in prompt
