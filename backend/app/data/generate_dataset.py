"""Realistic Synthetic Social Media Dataset Generator with planted trends, sarcasm, and network clusters."""
import json
import random
import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path

SALT = "social-pulse-secret-salt-2026"

def hash_u(username: str) -> str:
    clean = username.strip().lower()
    return "usr_" + hashlib.sha256(f"{SALT}:{clean}".encode("utf-8")).hexdigest()[:16]

USERS = [
    # Cluster 1: Tech / AI Influencers & Enthusiasts
    {"name": "tech_lead_arjun", "lang": "hinglish", "geo": "IN-MH", "age": "25-34", "interest": "Tech & AI", "bio": "Staff AI Engineer in Mumbai. Building distributed LLM infra. Hindi & English.", "is_influencer": True},
    {"name": "ai_researcher_sarah", "lang": "en", "geo": "US-CA", "age": "25-34", "interest": "Tech & AI", "bio": "Research scientist in SF. Foundation models & neuro-symbolic systems.", "is_influencer": True},
    {"name": "dev_priya_codes", "lang": "hinglish", "geo": "IN-KA", "age": "18-24", "interest": "Tech & AI", "bio": "Full-stack dev & open-source contributor from Bengaluru. Coffee + Python.", "is_influencer": False},
    {"name": "rohit_cloud_guru", "lang": "hinglish", "geo": "IN-DL", "age": "35-49", "interest": "Tech & AI", "bio": "DevOps architect & Kubernetes enthusiast. Cloud scalability nerd.", "is_influencer": False},
    {"name": "kevin_mlops", "lang": "en", "geo": "US-WA", "age": "25-34", "interest": "Tech & AI", "bio": "MLOps engineer at cloud startup. Pipeline automation advocate.", "is_influencer": False},
    {"name": "alex_neural_net", "lang": "en", "geo": "UK-ENG", "age": "25-34", "interest": "Tech & AI", "bio": "PhD researcher exploring transformers & cognitive architectures.", "is_influencer": False},
    
    # Cluster 2: Sustainability / Climate Tech
    {"name": "ananya_climate_voice", "lang": "hinglish", "geo": "IN-DL", "age": "25-34", "interest": "Climate & Sustainability", "bio": "Climate policy analyst. Advocating renewable energy & green tech in South Asia.", "is_influencer": True},
    {"name": "david_green_future", "lang": "en", "geo": "DE-BE", "age": "35-49", "interest": "Climate & Sustainability", "bio": "Clean energy researcher based in Berlin. Circular economy enthusiast.", "is_influencer": True},
    {"name": "solar_samuel", "lang": "en", "geo": "US-CA", "age": "35-49", "interest": "Climate & Sustainability", "bio": "Solar grid consultant & EV battery researcher.", "is_influencer": False},
    {"name": "ecofriendly_leila", "lang": "en", "geo": "FR-IDF", "age": "18-24", "interest": "Climate & Sustainability", "bio": "Zero-waste activist & sustainable living advocate.", "is_influencer": False},
    {"name": "vikram_clean_earth", "lang": "hinglish", "geo": "IN-MH", "age": "25-34", "interest": "Climate & Sustainability", "bio": "Urban forestry advocate & environmental educator.", "is_influencer": False},

    # Bridge Nodes: Connect Tech & Climate
    {"name": "marcus_clean_tech", "lang": "en", "geo": "US-CA", "age": "35-49", "interest": "Tech & AI", "bio": "Investing in AI for decarbonization and grid optimization. Tech + Climate bridge.", "is_influencer": True, "is_bridge": True},
    {"name": "tanya_greentech_dev", "lang": "hinglish", "geo": "IN-KA", "age": "25-34", "interest": "Climate & Sustainability", "bio": "Building IoT smart sensors for green agriculture. Tech enthusiast.", "is_influencer": False, "is_bridge": True},

    # Cluster 3: Finance / Crypto
    {"name": "crypto_analyst_raj", "lang": "hinglish", "geo": "IN-MH", "age": "25-34", "interest": "Finance & Crypto", "bio": "Macro financial analyst & on-chain data researcher. Mumbai.", "is_influencer": True},
    {"name": "elena_defi_queen", "lang": "en", "geo": "CH-ZH", "age": "25-34", "interest": "Finance & Crypto", "bio": "DeFi builder & smart contract security researcher. Zurich.", "is_influencer": True},
    {"name": "trader_neil", "lang": "en", "geo": "UK-ENG", "age": "18-24", "interest": "Finance & Crypto", "bio": "Algorithmic day trader. Following liquidity cycles & derivatives.", "is_influencer": False},
    {"name": "varun_hodl", "lang": "hinglish", "geo": "IN-DL", "age": "18-24", "interest": "Finance & Crypto", "bio": "Crypto investor & tech follower. Kabhi loss, kabhi profit!", "is_influencer": False},

    # Cluster 4: Cultural Critics & Satirists (Sarcasm hub)
    {"name": "cynical_sid", "lang": "hinglish", "geo": "IN-MH", "age": "25-34", "interest": "Creative & Media", "bio": "Full-time tech critic, part-time meme creator. Sarcasm is an art form.", "is_influencer": True},
    {"name": "satire_sophie", "lang": "en", "geo": "UK-ENG", "age": "25-34", "interest": "Creative & Media", "bio": "Journalist covering tech excess, corporate buzzwords, and digital absurdities.", "is_influencer": False},
]

# Generate additional ~40 cohort users to guarantee strong k-anonymity (k>=20) across categories
for i in range(1, 45):
    USERS.append({
        "name": f"community_user_{i}",
        "lang": random.choice(["en", "en", "hinglish", "hi"]),
        "geo": random.choice(["IN-MH", "IN-KA", "IN-DL", "US-CA", "UK-ENG"]),
        "age": random.choice(["18-24", "25-34", "25-34", "35-49"]),
        "interest": random.choice(["Tech & AI", "Tech & AI", "Finance & Crypto", "Climate & Sustainability"]),
        "bio": f"Digital nomad, social media observer #{i} interested in modern trends and news.",
        "is_influencer": False
    })

POST_TEMPLATES = [
    # #AIRevolution
    {"topic": "#AIRevolution", "text": "The latest multi-modal benchmark results are astounding. Reasoning accuracy jumped 35% in one quarter!", "lang": "en", "polarity": 0.85, "emotion": "excitement", "sarcasm": False, "stance": "favorable"},
    {"topic": "#AIRevolution", "text": "Yeh naye AI agents sach me complex coding workflows automate kar rahe hain. Dev velocity 3x ho gayi!", "lang": "hinglish", "polarity": 0.82, "emotion": "joy", "sarcasm": False, "stance": "favorable"},
    {"topic": "#AIRevolution", "text": "Worried about the sudden wave of automated layoffs across IT teams. How do junior developers survive this transition?", "lang": "en", "polarity": -0.65, "emotion": "anxiety", "sarcasm": False, "stance": "against"},
    {"topic": "#AIRevolution", "text": "Bhai har company AI wrapper bana kar billion dollar valuation maang rahi hai. Reality check kab aayega?", "lang": "hinglish", "polarity": -0.55, "emotion": "opposition", "sarcasm": True, "sarcasm_score": 0.88, "stance": "against"},
    {"topic": "#AIRevolution", "text": "Oh incredible! Another wrapper that adds three buttons to a prompt and charges $40/month. What pure visionary genius.", "lang": "en", "polarity": -0.72, "emotion": "anger", "sarcasm": True, "sarcasm_score": 0.94, "stance": "against"},
    {"topic": "#AIRevolution", "text": "Full support to the open weights movement. Open models democratize access for researchers in developing nations.", "lang": "en", "polarity": 0.78, "emotion": "support", "sarcasm": False, "stance": "favorable"},
    {"topic": "#AIRevolution", "text": "Deploying local LLMs on workstation for offline private intelligence. Works like a charm.", "lang": "en", "polarity": 0.60, "emotion": "joy", "sarcasm": False, "stance": "favorable"},
    {"topic": "#AIRevolution", "text": "AI alignment research should be prioritised over reckless capabilities racing.", "lang": "en", "polarity": 0.10, "emotion": "neutral", "sarcasm": False, "stance": "neutral"},

    # #SustainableTech
    {"topic": "#SustainableTech", "text": "Massive milestone: Next-gen solid-state battery achieved 800 cycles with 90% capacity retention.", "lang": "en", "polarity": 0.88, "emotion": "joy", "sarcasm": False, "stance": "favorable"},
    {"topic": "#SustainableTech", "text": "Solar energy adoption rate in western India has crossed expectations. Clean power decentralization in full swing!", "lang": "hinglish", "polarity": 0.75, "emotion": "excitement", "sarcasm": False, "stance": "favorable"},
    {"topic": "#SustainableTech", "text": "Using AI predictive modeling to balance renewable power grid load during extreme heat waves.", "lang": "en", "polarity": 0.70, "emotion": "support", "sarcasm": False, "stance": "favorable"},
    {"topic": "#SustainableTech", "text": "Greenwashing in corporate climate pledges is reaching comical levels. Planting 100 trees while burning megawatts?", "lang": "en", "polarity": -0.68, "emotion": "anger", "sarcasm": True, "sarcasm_score": 0.89, "stance": "against"},
    {"topic": "#SustainableTech", "text": "Battery recycling infra is desperately lagging behind EV manufacturing scale.", "lang": "en", "polarity": -0.45, "emotion": "anxiety", "sarcasm": False, "stance": "against"},

    # #CryptoRally
    {"topic": "#CryptoRally", "text": "Total on-chain volume exploded 120% overnight. Institutional inflows breaking quarterly records!", "lang": "en", "polarity": 0.90, "emotion": "excitement", "sarcasm": False, "stance": "favorable"},
    {"topic": "#CryptoRally", "text": "Bhai market green dekh ke confidence laut aaya hai! Target 100k confirmed lag raha hai.", "lang": "hinglish", "polarity": 0.80, "emotion": "joy", "sarcasm": False, "stance": "favorable"},
    {"topic": "#CryptoRally", "text": "Leverage liquidation cascade will be brutal when this overheated funding rate unwinds. Stay safe.", "lang": "en", "polarity": -0.58, "emotion": "anxiety", "sarcasm": False, "stance": "neutral"},
    {"topic": "#CryptoRally", "text": "Great! Another pump and dump round so venture funds can dump on retail. As predictable as clockwork.", "lang": "en", "polarity": -0.75, "emotion": "anger", "sarcasm": True, "sarcasm_score": 0.91, "stance": "against"},
    {"topic": "#CryptoRally", "text": "Decentralized finance lending protocols proved remarkably resilient throughout this volatility spike.", "lang": "en", "polarity": 0.65, "emotion": "support", "sarcasm": False, "stance": "favorable"},

    # #BrandCrisis
    {"topic": "#BrandCrisis", "text": "CloudCorp just forced telemetry on all private enterprise servers without consent. Massive security breach!", "lang": "en", "polarity": -0.85, "emotion": "anger", "sarcasm": False, "stance": "against"},
    {"topic": "#BrandCrisis", "text": "Kya bakwas update hai, production server pura down ho gaya. Customer support ka koi ata pata nahi.", "lang": "hinglish", "polarity": -0.80, "emotion": "anger", "sarcasm": False, "stance": "against"},
    {"topic": "#BrandCrisis", "text": "Congratulations CloudCorp on alienating your entire developer community in a single release. Masterclass in PR disaster!", "lang": "en", "polarity": -0.90, "emotion": "anger", "sarcasm": True, "sarcasm_score": 0.96, "stance": "against"},
    {"topic": "#BrandCrisis", "text": "Our engineering department is urgently migrating away from this platform. Cannot trust unannounced telemetry changes.", "lang": "en", "polarity": -0.60, "emotion": "anxiety", "sarcasm": False, "stance": "against"},
    {"topic": "#BrandCrisis", "text": "Company issued an official apology, but trust is broken. Words mean nothing without immediate code rollback.", "lang": "en", "polarity": -0.40, "emotion": "sadness", "sarcasm": False, "stance": "against"}
]

def generate_dataset(output_path: Path, num_posts: int = 380):
    random.seed(42)
    start_time = datetime(2026, 10, 1, 8, 0, tzinfo=timezone.utc)
    
    posts = []
    
    tech_users = [u for u in USERS if u["interest"] == "Tech & AI"]
    eco_users = [u for u in USERS if u["interest"] == "Climate & Sustainability"]
    crypto_users = [u for u in USERS if u["interest"] == "Finance & Crypto"]
    influencer_users = [u for u in USERS if u.get("is_influencer")]
    bridge_users = [u for u in USERS if u.get("is_bridge")]

    for i in range(1, num_posts + 1):
        post_id = f"p_{i:04d}"
        
        day_dice = random.random()
        if day_dice < 0.20:
            time_offset = timedelta(hours=random.uniform(0, 24))
            topic_pool = ["#AIRevolution", "#SustainableTech"]
        elif day_dice < 0.55:
            time_offset = timedelta(hours=24 + random.uniform(2, 18))
            topic_pool = ["#AIRevolution", "#AIRevolution", "#SustainableTech"]
        elif day_dice < 0.85:
            time_offset = timedelta(hours=48 + random.uniform(1, 20))
            topic_pool = ["#CryptoRally", "#CryptoRally", "#BrandCrisis", "#BrandCrisis"]
        else:
            time_offset = timedelta(hours=72 + random.uniform(0, 18))
            topic_pool = ["#AIRevolution", "#SustainableTech", "#CryptoRally", "#BrandCrisis"]

        timestamp = start_time + time_offset
        chosen_topic = random.choice(topic_pool)
        
        matching_templates = [t for t in POST_TEMPLATES if t["topic"] == chosen_topic]
        tpl = random.choice(matching_templates)
        
        if chosen_topic == "#AIRevolution":
            author = random.choice(tech_users + bridge_users)
        elif chosen_topic == "#SustainableTech":
            author = random.choice(eco_users + bridge_users)
        elif chosen_topic == "#CryptoRally":
            author = random.choice(crypto_users)
        else:
            author = random.choice(USERS)
            
        author_hash = hash_u(author["name"])
        platform = random.choices(["x", "telegram", "reddit", "youtube"], weights=[0.55, 0.25, 0.12, 0.08])[0]
        
        parent_id = None
        reply_to = None
        mentions = []
        retweets = None
        
        earlier_same_topic = [p for p in posts if chosen_topic in p["topics"] and p["_dt"] < timestamp]
        if earlier_same_topic and random.random() < 0.35:
            target_post = random.choice(earlier_same_topic[-20:])
            parent_id = target_post["post_id"]
            reply_to = target_post["user_hash"]
            if random.random() < 0.4:
                rand_inf = random.choice(influencer_users)
                mentions.append(hash_u(rand_inf["name"]))
        elif random.random() < 0.20:
            if earlier_same_topic:
                target_post = random.choice(earlier_same_topic[-15:])
                retweets = target_post["user_hash"]
                
        is_inf = author.get("is_influencer", False)
        base_likes = random.randint(150, 4500) if is_inf else random.randint(2, 60)
        likes = base_likes
        rts = int(likes * random.uniform(0.15, 0.45))
        replies = int(likes * random.uniform(0.05, 0.25))
        views = likes * random.randint(15, 45)
        
        sarcasm_score = tpl.get("sarcasm_score", 0.0) if tpl["sarcasm"] else round(random.uniform(0.01, 0.15), 3)
        
        post_obj = {
            "post_id": post_id,
            "platform": platform,
            "user_hash": author_hash,
            "text": tpl["text"],
            "lang": tpl["lang"],
            "timestamp": timestamp.isoformat(),
            "_dt": timestamp,
            "parent_id": parent_id,
            "reply_to": reply_to,
            "mentions": mentions,
            "retweets": retweets,
            "engagement": {
                "likes": likes,
                "retweets": rts,
                "replies": replies,
                "quotes": int(rts * 0.1),
                "views": views
            },
            "bio_text": author["bio"],
            "topics": [chosen_topic],
            "sentiment": {
                "polarity": tpl["polarity"],
                "emotion": tpl["emotion"],
                "emotion_scores": {tpl["emotion"]: 0.85, "neutral": 0.15},
                "sarcasm": tpl["sarcasm"],
                "sarcasm_score": sarcasm_score,
                "stance": tpl["stance"],
                "language": tpl["lang"]
            }
        }
        
        posts.append(post_obj)

    posts.sort(key=lambda x: x["_dt"])
    for p in posts:
        del p["_dt"]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for p in posts:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
            
    print(f"Generated {len(posts)} posts saved to {output_path}")

if __name__ == "__main__":
    out_file = Path("C:/Users/HP/.gemini/antigravity/scratch/social-pulse/backend/app/data/sample_dataset.jsonl")
    generate_dataset(out_file)
