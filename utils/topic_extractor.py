from collections import Counter
import re

STOP_WORDS = {
    "the", "is", "in", "and", "to", "of", "a", "that", "it", "on", "for", "as",
    "with", "this", "was", "are", "be", "by", "or", "an", "at", "from", "you",
    "your", "we", "they", "their", "he", "she", "his", "her", "have", "has",
    "had", "but", "not", "can", "will", "would", "about", "into", "than", "then",
    "them", "been", "what", "when", "where", "who", "which", "how", "all", "more",
    "our", "out", "up", "down", "if", "so", "do", "does", "did", "these", "those"
}

def detect_topic(text):
    if not text or len(text.strip()) < 20:
        return "General"

    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    filtered_words = [w for w in words if w not in STOP_WORDS]

    if not filtered_words:
        return "General"

    counts = Counter(filtered_words)
    most_common = counts.most_common(3)

    if not most_common:
        return "General"

    topic_words = [word.capitalize() for word, _ in most_common]
    return ", ".join(topic_words)