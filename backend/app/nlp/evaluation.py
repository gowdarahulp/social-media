"""Evaluation suite for Multi-dimensional Sentiment & Emotion Engine."""
from typing import Any, Dict, List, Tuple
from backend.app.nlp.sentiment_analyzer import sentiment_engine

BENCHMARK_DATASET: List[Dict[str, Any]] = [
    # Anger
    {"text": "Worst customer service ever. Total scam and unacceptable outage!", "emotion": "anger", "sarcasm": False},
    {"text": "Kya bakwas update hai, mera pura production database uda diya!", "emotion": "anger", "sarcasm": False},
    # Anxiety
    {"text": "The mass layoffs across tech are terrifying, feeling so worried about the future.", "emotion": "anxiety", "sarcasm": False},
    {"text": "Yeh crypto crash dekh kar to bohot tension ho rahi hai bhai.", "emotion": "anxiety", "sarcasm": False},
    # Excitement
    {"text": "Astounding AI capabilities released today! Truly revolutionary milestone.", "emotion": "excitement", "sarcasm": False},
    {"text": "Zabardast rally! Market breaking all all-time highs today!", "emotion": "excitement", "sarcasm": False},
    # Joy
    {"text": "So happy and proud to announce we hit our green energy targets early!", "emotion": "joy", "sarcasm": False},
    {"text": "Aaj to mazaa aa gaya, code pehli baar me compile ho gaya aur run ho gaya!", "emotion": "joy", "sarcasm": False},
    # Sadness
    {"text": "Heartbroken and grieving the tragic loss of an inspiring mentor.", "emotion": "sadness", "sarcasm": False},
    {"text": "Bohot afsos hua ye depressing khabar sun kar.", "emotion": "sadness", "sarcasm": False},
    # Support
    {"text": "We completely endorse and salute this open source initiative.", "emotion": "support", "sarcasm": False},
    {"text": "Hum pura support karte hain clean energy revolution ko.", "emotion": "support", "sarcasm": False},
    # Opposition
    {"text": "We strongly oppose and reject these monopolistic corporate practices.", "emotion": "opposition", "sarcasm": False},
    {"text": "Ye overhyped product ka virodh hona chahiye.", "emotion": "opposition", "sarcasm": False},
    # Sarcasm tests
    {"text": "Oh fantastic! Another mandatory subscription fee for basic features, what pure genius.", "emotion": "anger", "sarcasm": True},
    {"text": "Congratulations CloudCorp on alienating your entire developer base in one release. Masterclass in PR disaster!", "emotion": "anger", "sarcasm": True}
]

def evaluate_sentiment_engine() -> Dict[str, Any]:
    correct_emotion = 0
    correct_sarcasm = 0
    total = len(BENCHMARK_DATASET)
    
    classes = ["anger", "anxiety", "excitement", "joy", "sadness", "support", "opposition"]
    tp = {c: 0 for c in classes}
    fp = {c: 0 for c in classes}
    fn = {c: 0 for c in classes}

    for item in BENCHMARK_DATASET:
        res = sentiment_engine.analyze(item["text"])
        actual_em = item["emotion"]
        pred_em = res.emotion
        
        if pred_em == actual_em:
            correct_emotion += 1
            if actual_em in tp:
                tp[actual_em] += 1
        else:
            if pred_em in fp:
                fp[pred_em] += 1
            if actual_em in fn:
                fn[actual_em] += 1

        if res.sarcasm == item["sarcasm"]:
            correct_sarcasm += 1

    f1_scores = {}
    for c in classes:
        p = tp[c] / (tp[c] + fp[c]) if (tp[c] + fp[c]) > 0 else 0.0
        r = tp[c] / (tp[c] + fn[c]) if (tp[c] + fn[c]) > 0 else 0.0
        f1 = (2 * p * r) / (p + r) if (p + r) > 0 else 0.0
        f1_scores[c] = round(f1, 2)

    macro_f1 = round(sum(f1_scores.values()) / len(f1_scores), 2)
    acc_emotion = round(correct_emotion / total, 2)
    acc_sarcasm = round(correct_sarcasm / total, 2)

    return {
        "sample_size": total,
        "emotion_accuracy": acc_emotion,
        "macro_f1": macro_f1,
        "per_class_f1": f1_scores,
        "sarcasm_accuracy": acc_sarcasm
    }

if __name__ == "__main__":
    report = evaluate_sentiment_engine()
    print("Sentiment Evaluation Report:", report)
