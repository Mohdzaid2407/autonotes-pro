from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

def get_summary(text):
    if not text or len(text.strip()) < 50:
        return text

    try:
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = LsaSummarizer()

        summary_sentences = summarizer(parser.document, 3)

        summary = " ".join(str(sentence) for sentence in summary_sentences)

        if not summary.strip():
            return text[:500]

        return summary

    except Exception as e:
        return f"Summary error: {str(e)}"