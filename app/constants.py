from __future__ import annotations


APP_TITLE = "EdgeVoice"
PLAYBACK_COMMAND_TIMEOUT_SECONDS = 5.0
PREVIEW_TIMEOUT_SECONDS = 12.0

PREVIEW_PHRASES: dict[str, str] = {
    "ar": "مرحبًا، هذه معاينة قصيرة للصوت المحدد.",
    "bg": "Здравейте, това е кратък преглед на избрания глас.",
    "ca": "Hola, aquesta és una breu mostra de la veu seleccionada.",
    "cs": "Dobrý den, toto je krátká ukázka vybraného hlasu.",
    "da": "Hej, dette er en kort prøve af den valgte stemme.",
    "de": "Hallo, dies ist eine kurze Vorschau der ausgewählten Stimme.",
    "el": "Γεια σας, αυτό είναι ένα σύντομο δείγμα της επιλεγμένης φωνής.",
    "en": "Hello, this is a short preview of the selected voice.",
    "es": "Hola, esta es una breve muestra de la voz seleccionada.",
    "et": "Tere, see on valitud hääle lühike eelvaade.",
    "fi": "Hei, tämä on lyhyt esikatselu valitusta äänestä.",
    "fr": "Bonjour, voici un court aperçu de la voix sélectionnée.",
    "he": "שלום, זו הדגמה קצרה של הקול שנבחר.",
    "hi": "नमस्ते, यह चुनी गई आवाज़ का एक छोटा पूर्वावलोकन है।",
    "hr": "Pozdrav, ovo je kratki pregled odabranog glasa.",
    "hu": "Üdvözlöm, ez a kiválasztott hang rövid előnézete.",
    "id": "Halo, ini adalah pratinjau singkat suara yang dipilih.",
    "it": "Ciao, questa è una breve anteprima della voce selezionata.",
    "ja": "こんにちは。これは選択した音声の短いプレビューです。",
    "ko": "안녕하세요. 선택한 음성의 짧은 미리 듣기입니다.",
    "lt": "Sveiki, tai trumpa pasirinkto balso peržiūra.",
    "lv": "Sveiki, šis ir īss izvēlētās balss priekšskatījums.",
    "ms": "Halo, ini ialah pratonton ringkas suara yang dipilih.",
    "nl": "Hallo, dit is een korte preview van de geselecteerde stem.",
    "no": "Hei, dette er en kort forhåndsvisning av den valgte stemmen.",
    "pl": "Cześć, to jest krótki podgląd wybranego głosu.",
    "pt": "Olá, esta é uma breve prévia da voz selecionada.",
    "ro": "Salut, aceasta este o scurtă previzualizare a vocii selectate.",
    "ru": "Здравствуйте, это короткое превью выбранного голоса.",
    "sk": "Dobrý deň, toto je krátka ukážka vybraného hlasu.",
    "sl": "Pozdravljeni, to je kratek predogled izbranega glasu.",
    "sv": "Hej, det här är en kort förhandsvisning av den valda rösten.",
    "ta": "வணக்கம், இது தேர்ந்தெடுத்த குரலின் சுருக்கமான முன்னோட்டம்.",
    "th": "สวัสดี นี่คือตัวอย่างสั้น ๆ ของเสียงที่เลือกไว้",
    "tr": "Merhaba, bu seçili sesin kısa bir önizlemesidir.",
    "uk": "Вітаю, це короткий попередній перегляд вибраного голосу.",
    "vi": "Xin chào, đây là bản xem trước ngắn của giọng nói đã chọn.",
    "zh": "你好，这是所选语音的简短预览。",
}


def get_preview_phrase(locale: str) -> str:
    language = locale.split("-", 1)[0].lower() if locale and locale != "All" else "en"
    return PREVIEW_PHRASES.get(language, PREVIEW_PHRASES["en"])
