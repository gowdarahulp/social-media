"""Tests for sentiment analysis, Hinglish code-mixed support, sarcasm, and timeline aggregation."""
import pytest
from backend.app.nlp.sentiment_analyzer import sentiment_engine
from backend.app.nlp.evaluation import evaluate_sentiment_engine
from backend.app.nlp import get_sentiment_timeline_aggregation
from backend.app.connectors.replay import ReplayConnector
from backend.app.db.repository import PostRepository

def test_sentiment_polarity_and_emotions():
    res_joy = sentiment_engine.analyze("We are thrilled and celebrating this extraordinary achievement!")
    assert res_joy.emotion in ["joy", "excitement"]
    assert res_joy.polarity > 0.3
    
    res_anger = sentiment_engine.analyze("Unacceptable fraud and terrible customer service, boycott this company!")
    assert res_anger.emotion in ["anger", "opposition"]
    assert res_anger.polarity < -0.3
    
    res_anxiety = sentiment_engine.analyze("Massive fear and anxiety about the market crash and sudden layoffs.")
    assert res_anxiety.emotion == "anxiety"
    assert res_anxiety.polarity < 0.0

def test_hinglish_code_mixed_detection():
    # Hinglish joy
    res_hinglish_joy = sentiment_engine.analyze("Yeh update ekdum mast hai bhai, mazaa aa gaya coding karke!")
    assert res_hinglish_joy.language == "hinglish"
    assert res_hinglish_joy.emotion in ["joy", "excitement"]
    assert res_hinglish_joy.polarity > 0.2
    
    # Hinglish anger
    res_hinglish_anger = sentiment_engine.analyze("Kya bakwas aur ghatiya service hai, dimaag kharab kar diya!")
    assert res_hinglish_anger.language == "hinglish"
    assert res_hinglish_anger.emotion == "anger"
    assert res_hinglish_anger.polarity < -0.3

def test_sarcasm_detection():
    sarcastic_text = "Oh fantastic! Another mandatory subscription price hike, what pure genius."
    res = sentiment_engine.analyze(sarcastic_text)
    assert res.sarcasm is True
    assert res.sarcasm_score > 0.7
    # Sarcastic praise should invert to negative polarity
    assert res.polarity < 0.0
    assert res.emotion in ["anger", "opposition"]

def test_sentiment_evaluation_benchmark_metrics():
    report = evaluate_sentiment_engine()
    assert report["sample_size"] >= 16
    assert report["emotion_accuracy"] >= 0.85
    assert report["macro_f1"] >= 0.80
    assert report["sarcasm_accuracy"] >= 0.85

@pytest.mark.anyio
async def test_sentiment_timeline_aggregation():
    PostRepository.clear_all()
    # Ingest a sample from replay connector
    connector = ReplayConnector()
    posts = await connector.fetch(limit=60)
    for p in posts:
        s = sentiment_engine.analyze(p.text)
        PostRepository.insert_post(p, s)
        
    timeline = get_sentiment_timeline_aggregation(bucket="day")
    assert len(timeline) >= 1
    assert timeline[0].post_count > 0
    assert isinstance(timeline[0].avg_polarity, float)
    assert isinstance(timeline[0].emotions, dict)
