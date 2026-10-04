"""Multi-dimensional Sentiment, 8-Emotion, Sarcasm, and Hinglish Analysis Engine."""
import re
import math
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from backend.app.schemas.sentiment import EmotionType, SentimentResult, SentimentTimelinePoint, StanceType

# High-fidelity emotion & sentiment lexicons with Hinglish code-mixed tokens
EMOTION_LEXICON = {
    "anger": [
        "angry", "furious", "outraged", "scam", "breach", "cheat", "disaster", "terrible",
        "worst", "hate", "unacceptable", "lawsuit", "boycott", "fraud", "alienating",
        # Hinglish & Hindi
        "bakwas", "ghatiya", "gussa", "loot", "chor", "dhokha", "bekar", "fraudster", "barbaad",
        "dimaag kharab", "pagal", "chori", "shameful", "bewakoof"
    ],
    "anxiety": [
        "worried", "anxious", "anxiety", "fear", "risk", "nervous", "layoffs", "uncertainty",
        "danger", "crash", "loss", "warning", "panic", "threat", "vulnerable", "bubble",
        # Hinglish & Hindi
        "chinta", "tension", "darr", "pareshani", "khatra", "gadbad", "loss hoga", "fatafat becho"
    ],
    "excitement": [
        "excited", "breakthrough", "astonishing", "record", "skyrocket", "revolutionary",
        "massive", "gamechanger", "future", "epic", "huge", "surging", "unreal", "hype",
        # Hinglish & Hindi
        "dhamaka", "zabardast", "shandar", "toofani", "chha gaya", "aag laga di", "rocking"
    ],
    "joy": [
        "happy", "delighted", "love", "wonderful", "celebrating", "achievement", "proud",
        "thriving", "fantastic", "blessed", "charm", "glad", "excellent", "pleased",
        # Hinglish & Hindi
        "mast", "mazaa", "khushi", "badhiya", "ekdum sahi", "khoob", "dil khush", "anand"
    ],
    "sadness": [
        "sad", "heartbroken", "depressing", "grief", "unfortunately", "tragic", "loss",
        "sorry", "regret", "disappointed", "struggling", "mourning", "painful",
        # Hinglish & Hindi
        "dukh", "udaas", "afsos", "rona", "dard", "gam", "dukhad"
    ],
    "support": [
        "support", "back", "endorse", "agree", "advocate", "solidarity", "champion",
        "credit", "commend", "praise", "salute", "encourage", "vote", "promising",
        # Hinglish & Hindi
        "saath", "samarthan", "pakka", "sahi bola", "bilkul sahi", "zindabad", "salute hai"
    ],
    "opposition": [
        "oppose", "against", "reject", "boycott", "protest", "counter", "criticize",
        "flawed", "overhyped", "disagree", "object", "condemn", "resist", "ban",
        # Hinglish & Hindi
        "virodh", "khilaaf", "inqar", "galat", "mat maano", "band karo", "overhyped hai"
    ]
}

SARCASM_INDICATORS = [
    r"\boh\s+(great|fantastic|wonderful|incredible|brilliant|genius)\b",
    r"\bwhat\s+(pure\s+)?(genius|masterclass|innovation)\b",
    r"\bas\s+predictable\s+as\s+clockwork\b",
    r"\bcongratulations\s+on\s+(alienating|destroying|crashing)\b",
    r"\bjust\s+what\s+(we|i|my\s+empty\s+wallet)\s+needed\b",
    r"\btruly\s+groundbreaking\b",
    r"\breality\s+check\s+kab\s+aayega\b",
    r"\bkya\s+zabardast\s+.*waah\b",
    r"\bwaah\s+(kya\s+baat|re|bhai)\b",
    r"\bmasterclass\s+in\s+pr\s+disaster\b"
]

class MultiDimensionalSentimentEngine:
    def __init__(self):
        self._compiled_sarcasm = [re.compile(p, re.IGNORECASE) for p in SARCASM_INDICATORS]

    def detect_language(self, text: str) -> str:
        text_lower = text.lower()
        hinglish_words = ["hai", "hain", "kya", "bhai", "yeh", "woh", "sach", "bhi", "par", "kab", "aayega", "dosto", "bakwas", "mast", "mazaa", "kar", "rahe", "gaya"]
        matches = sum(1 for w in hinglish_words if re.search(r"\b" + w + r"\b", text_lower))
        if matches >= 2:
            return "hinglish"
        # Check Devanagari script
        if re.search(r"[\u0900-\u097F]", text):
            return "hi"
        return "en"

    def analyze(self, text: str, target_topic: Optional[str] = None) -> SentimentResult:
        lang = self.detect_language(text)
        tokens = re.findall(r"\b\w+\b", text.lower())
        token_set = set(tokens)

        # 1. Sarcasm Analysis
        sarcasm_detected = False
        sarcasm_score = 0.05
        for pattern in self._compiled_sarcasm:
            if pattern.search(text):
                sarcasm_detected = True
                sarcasm_score = 0.92
                break

        # Check punctuation irony (e.g. "?!?!", quotes around praise)
        if re.search(r"[\"\'](genius|innovative|visionary)[\"\']", text, re.IGNORECASE):
            sarcasm_detected = True
            sarcasm_score = max(sarcasm_score, 0.85)

        # 2. Emotion Scoring
        emotion_counts: Dict[str, float] = {e: 0.1 for e in EMOTION_LEXICON}
        for emotion, keywords in EMOTION_LEXICON.items():
            for kw in keywords:
                if " " in kw:
                    if kw in text.lower():
                        emotion_counts[emotion] += 2.0
                elif kw in token_set:
                    emotion_counts[emotion] += 1.5

        # If sarcasm detected, invert apparent praise into anger/opposition
        if sarcasm_detected:
            emotion_counts["anger"] += 3.0
            emotion_counts["opposition"] += 2.5
            emotion_counts["joy"] = max(0.0, emotion_counts["joy"] - 2.0)
            emotion_counts["excitement"] = max(0.0, emotion_counts["excitement"] - 2.0)

        total_score = sum(emotion_counts.values())
        emotion_probs = {e: round(score / total_score, 3) for e, score in emotion_counts.items()}
        
        # Determine dominant emotion
        max_emotion = max(emotion_counts, key=emotion_counts.get)
        if emotion_counts[max_emotion] <= 0.2:
            dominant_emotion: EmotionType = "neutral"
        else:
            dominant_emotion: EmotionType = max_emotion # type: ignore

        # 3. Polarity Calculation (-1.0 to +1.0)
        pos_weight = (emotion_probs["joy"] + emotion_probs["excitement"] + emotion_probs["support"])
        neg_weight = (emotion_probs["anger"] + emotion_probs["sadness"] + emotion_probs["anxiety"] + emotion_probs["opposition"])
        
        raw_polarity = pos_weight - neg_weight
        if sarcasm_detected:
            raw_polarity = -abs(raw_polarity) - 0.2

        polarity = max(-1.0, min(1.0, round(raw_polarity, 2)))

        # 4. Stance Calculation towards target topic
        stance: StanceType = "neutral"
        if target_topic and target_topic.lower() in text.lower():
            if polarity > 0.25:
                stance = "favorable"
            elif polarity < -0.25:
                stance = "against"
            else:
                stance = "neutral"
        elif polarity > 0.35:
            stance = "favorable"
        elif polarity < -0.35:
            stance = "against"
        else:
            stance = "none"

        return SentimentResult(
            polarity=polarity,
            emotion=dominant_emotion,
            emotion_scores=emotion_probs,
            sarcasm=sarcasm_detected,
            sarcasm_score=round(sarcasm_score, 3),
            stance=stance,
            language=lang
        )

sentiment_engine = MultiDimensionalSentimentEngine()
