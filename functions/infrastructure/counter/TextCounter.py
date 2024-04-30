import re
from collections import Counter

class TextAnalyzer:
    def __init__(self):
        pass

    def word_frequency(self, text, word):
        occurrences = re.findall(r'\b' + re.escape(word) + r'\b', text, flags=re.IGNORECASE)
        return len(occurrences)

    def most_common_words(self, text, n=5):
        words = re.findall(r'\b\w+\b', text.lower())
        word_counts = Counter(words)
        return dict(word_counts.most_common(n))


