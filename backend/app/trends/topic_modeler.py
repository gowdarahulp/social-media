"""Topic modeling and keyword/hashtag extraction."""
import re
from collections import Counter
from typing import Any, Dict, List, Set, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "by", "from",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did",
    "i", "you", "he", "she", "it", "we", "they", "this", "that", "these", "those", "what", "which",
    "who", "whom", "will", "would", "shall", "should", "can", "could", "may", "might", "must",
    "bhai", "hai", "hain", "kya", "yeh", "woh", "par", "ko", "se", "kar", "rahe", "gaya"
}

class TopicModeler:
    @staticmethod
    def extract_hashtags(text: str) -> List[str]:
        return re.findall(r"#\w+", text)

    @staticmethod
    def extract_keywords_ctf_idf(documents_by_topic: Dict[str, List[str]], top_k: int = 6) -> Dict[str, List[str]]:
        """Class-based TF-IDF (c-TF-IDF) keyword extraction per topic."""
        topic_names = list(documents_by_topic.keys())
        if not topic_names:
            return {}

        combined_docs = [" ".join(documents_by_topic[t]) for t in topic_names]
        if not any(combined_docs):
            return {t: [] for t in topic_names}

        vectorizer = TfidfVectorizer(
            stop_words=list(STOPWORDS),
            max_features=2000,
            ngram_range=(1, 2)
        )
        try:
            tfidf_matrix = vectorizer.fit_transform(combined_docs)
            feature_names = vectorizer.get_feature_names_out()
            
            topic_keywords = {}
            for idx, topic in enumerate(topic_names):
                row = tfidf_matrix.getrow(idx).toarray()[0]
                top_indices = row.argsort()[::-1][:top_k]
                kws = [feature_names[i] for i in top_indices if row[i] > 0]
                topic_keywords[topic] = kws
            return topic_keywords
        except Exception:
            # Fallback simple frequency
            res = {}
            for t, docs in documents_by_topic.items():
                words = re.findall(r"\b\w{3,}\b", " ".join(docs).lower())
                filtered = [w for w in words if w not in STOPWORDS]
                counts = Counter(filtered).most_common(top_k)
                res[t] = [w for w, _ in counts]
            return res
