from rake_nltk import Rake

def extract_keywords(text):
    if not text or len(text.strip()) < 20:
        return []

    try:
        rake = Rake()
        rake.extract_keywords_from_text(text)
        phrases = rake.get_ranked_phrases()

        clean_phrases = []
        for phrase in phrases[:8]:
            phrase = phrase.strip()
            if phrase and len(phrase) > 2:
                clean_phrases.append(phrase)

        return clean_phrases

    except Exception:
        return []