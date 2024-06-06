from langdetect import DetectorFactory, detect
import yake
from collections import Counter
import re

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download("stopwords")
nltk.download("punkt")


class TextAnalyzer:
    def __init__(self):
        pass
        

    def word_frequency(self, text, word):
        occurrences = re.findall(
            r"\b" + re.escape(word) + r"\b", text, flags=re.IGNORECASE
        )
        return len(occurrences)

    def remove_stopwords(self, text):
        DetectorFactory.seed = 0  # Ensures reproducible results with `langdetect`
        
        real_text = text.content
        # Filter out unwanted URLs
        real_text = [item for item in real_text if not item.startswith("gs://") and not item.startswith("https://")]
        
        whole_text = " ".join(real_text)

        # Tokenize the text into words
        words = word_tokenize(whole_text)

        # Filter out stopwords
        # Get English and Spanish stopwords
        stop_words_en = set(stopwords.words("english"))
        stop_words_es = set(stopwords.words("spanish"))

        filtered_words = []
        for word in words:
            # Detect the language of the word
            if not re.search(r'\d', word) or len(word) == 1:
                try: 
                    lang = detect(word.lower())
                    # Apply appropriate stopwords filtering
                    if lang == "en" and word.lower() not in stop_words_en:
                        filtered_words.append(word)
                    elif lang == "es" and word.lower() not in stop_words_es:
                        filtered_words.append(word)
                except:
                    continue
                

        return filtered_words

    def word_cloud_filter(self, text, n=10):
        # print(text)
        whole_text = " ".join(text)
        # print(whole_text)
        words = re.findall(r"\b\w+\b", whole_text.lower())
        word_counts = Counter(words)

        return dict(word_counts.most_common(n))

    def most_common_words(self, text, n=100):
        words = re.findall(r"\b\w+\b", text.lower())
        word_counts = Counter(words)
        return dict(word_counts.most_common(n))
