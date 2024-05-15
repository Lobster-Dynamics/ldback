import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
nltk.download("stopwords")
nltk.download("punkt")
from collections import Counter
from langdetect import detect, DetectorFactory
import yake 

class TextAnalyzer:
    def __init__(self):
        pass

    def word_frequency(self, text, word):
        occurrences = re.findall(r'\b' + re.escape(word) + r'\b', text, flags=re.IGNORECASE)
        return len(occurrences)

    def remove_stopwords(self, text):

        # language = "es"
        # max_ngram_size = 2
        # deduplication_threshold = 1
        # # deduplication_algo = 'seqm'
        # windowSize = 1
        # numOfKeywords = 10

        # kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_threshold, windowsSize=windowSize, top=numOfKeywords, features=None)

        
        # Initialize the language detector
        DetectorFactory.seed = 0  # Ensures reproducible results with `langdetect`

        real_text = text.content
        # print("Original list:", real_text)

        # Create a new list excluding items that start with "https://"
        real_text = [item for item in real_text if not item.startswith("https://")]

        # print("Updated list:", real_text)
        
        whole_text = " ".join(real_text)
        
        # print(len(whole_text))
        # keywords = kw_extractor.extract_keywords(whole_text)

        # for kw in keywords:
        #     print(kw)
        
        # Tokenize the text into words
        words = word_tokenize(whole_text)

        # Get English and Spanish stopwords
        stop_words_en = set(stopwords.words("english"))
        stop_words_es = set(stopwords.words("spanish"))

        filtered_words = []
        for word in words:
            # Detect the language of the word
            try:
                lang = detect(word.lower())
                # Apply appropriate stopwords filtering
                if lang == "en" and word.lower() not in stop_words_en:
                    filtered_words.append(word)
                elif lang == "es" and word.lower() not in stop_words_es:
                    filtered_words.append(word)
            except Exception:
                # If language detection fails, keep the word
                filtered_words.append(word)

        # whole_text = " ".join(filtered_words)
        # keywords = kw_extractor.extract_keywords(whole_text)
        # print("\n")
        # for kw in keywords:
        #     print(kw)
        
        # for word in filtered_words:
        #     print(word)
        
        return filtered_words
    
    def word_cloud_filter(self, text, n=10):
        # print(text)
        whole_text = " ".join(text)
        # print(whole_text)
        words = re.findall(r'\b\w+\b', whole_text.lower())
        word_counts = Counter(words)
        
        return dict(word_counts.most_common(n))

    def most_common_words(self, text, n=100):
        words = re.findall(r'\b\w+\b', text.lower())
        word_counts = Counter(words)
        return dict(word_counts.most_common(n))


