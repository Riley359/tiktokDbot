"""Configuration settings for TikTok scraper."""

# ===== AUTHENTICATION =====
# Paste your sessionid here (between the quotes)
SESSIONID = "4d0cdd9cb552c8fb7afc2499518e11bd"  # Replace with your actual sessionid

# ===== SEARCH STRATEGY CONFIGURATION =====
# Choose search strategy: "parallel", "sequential", "hashtag_only", or "personalized"
SEARCH_STRATEGY = "personalized"  # parallel = all methods at once, sequential = fallback approach, personalized = AI-driven preference-based

# Number of videos to collect
MAX_TOTAL_VIDEOS = 30
VIDEOS_PER_METHOD = 10  # Videos per search method when using parallel strategy
MIN_VIDEOS_PER_HASHTAG = 15  # Minimum videos per hashtag for better diversity

# ===== PERSONALIZED ALGORITHM CONFIGURATION =====
ANALYZE_LIKED_VIDEOS = True        # Whether to analyze liked videos for preferences
LIKED_VIDEOS_ANALYZE_COUNT = 100   # Number of liked videos to analyze for building preferences
USE_PERSONALIZED_FILTERING = True  # Whether to use personalized filtering
MIN_PREFERENCE_SCORE = 0.3        # Minimum preference score threshold (0.0-1.0)
PREFERENCE_PROFILE_FILE = "preference_profile.json"  # File to save/load preferences
UPDATE_PREFERENCES_INCREMENTALLY = True  # Update preferences as new liked videos are found
ENABLE_ALGORITHM_LEARNING = True   # Enable learning from user interactions

# Personalized search weights (how much each factor influences search)
PERSONALIZATION_WEIGHTS = {
    "hashtag_preference": 0.3,      # Weight for preferred hashtags
    "author_preference": 0.25,      # Weight for preferred authors
    "keyword_preference": 0.2,      # Weight for caption keywords
    "engagement_pattern": 0.15,     # Weight for engagement patterns
    "category_preference": 0.1      # Weight for content categories
}

# ===== HASHTAG CATEGORIES =====
HASHTAG_CATEGORIES = {
    # Core Trending
    "trending": ["fyp", "foryou", "viral", "trending", "xyzbca", "explore", "discovered", "recommended", "blowthisup", "viral_video"],
    
    # Entertainment & Comedy
    "entertainment": ["funny", "comedy", "memes", "pranks", "jokes", "humor", "lol", "laugh", "hilarious", "entertainment"],
    "comedy_skits": ["skit", "acting", "drama", "theater", "performance", "roleplay", "impression", "comedy_skit", "funny_video"],
    "memes_trends": ["meme", "trend", "challenge", "tiktoktrend", "memetrend", "viraltrend", "tiktokmeme", "internet_culture"],
    
    # Music & Performance
    "music_dance": ["music", "dance", "singing", "dancing", "musicvideo", "song", "cover", "original", "performer"],
    "hip_hop": ["hiphop", "rap", "beats", "freestyle", "hiphopmusic", "rapper", "hiphopculture", "bars", "flow"],
    "pop_music": ["pop", "popmusic", "mainstream", "charts", "radio", "billboard", "spotify", "apple_music"],
    "indie_alternative": ["indie", "alternative", "underground", "independent", "altmusic", "indieartist", "alternative_rock"],
    "classical_jazz": ["classical", "jazz", "orchestra", "piano", "violin", "saxophone", "blues", "instrumental"],
    
    # Lifestyle & Fashion
    "lifestyle": ["fashion", "beauty", "makeup", "ootd", "style", "aesthetic", "vibe", "mood", "lifestyle_content"],
    "fashion_trends": ["fashion_week", "designer", "streetwear", "vintage", "thrift", "sustainable_fashion", "fashionista"],
    "beauty_makeup": ["skincare", "cosmetics", "tutorial", "transformation", "glowup", "selfcare", "beauty_tips"],
    "home_decor": ["homedecor", "interior", "design", "apartment", "room", "decoration", "minimalist", "cozy"],
    
    # Food & Cooking
    "food": ["food", "cooking", "recipe", "foodie", "baking", "chef", "delicious", "yummy", "tasty"],
    "cooking_tutorials": ["cookingtips", "recipe_video", "kitchen", "cooking_hacks", "meal_prep", "easy_recipes"],
    "international_cuisine": ["italian", "mexican", "asian", "indian", "french", "mediterranean", "fusion", "authentic"],
    "desserts_sweets": ["dessert", "cake", "cookies", "pastry", "chocolate", "sweet", "treats", "bakery"],
    "healthy_eating": ["healthy", "nutrition", "diet", "wellness", "organic", "vegan", "vegetarian", "keto"],
    
    # Technology & Science
    "tech": ["tech", "technology", "gadgets", "ai", "coding", "programming", "developer", "software", "hardware"],
    "ai_ml": ["artificial_intelligence", "machine_learning", "chatgpt", "automation", "robotics", "future_tech"],
    "coding_programming": ["python", "javascript", "webdev", "coding_life", "programmer", "developer_life", "github"],
    "science": ["science", "physics", "chemistry", "biology", "space", "astronomy", "research", "experiment"],
    
    # Fitness & Health
    "fitness": ["fitness", "workout", "gym", "health", "exercise", "training", "fit", "strong", "muscle"],
    "yoga_meditation": ["yoga", "meditation", "mindfulness", "zen", "spiritual", "peace", "relaxation", "stretching"],
    "sports": ["sports", "football", "basketball", "soccer", "tennis", "baseball", "athletics", "competition"],
    "martial_arts": ["martialarts", "karate", "boxing", "mma", "jujitsu", "taekwondo", "self_defense", "combat"],
    
    # Travel & Adventure
    "travel": ["travel", "vacation", "wanderlust", "adventure", "explore", "journey", "destination", "backpacking"],
    "nature_outdoors": ["nature", "hiking", "camping", "mountains", "forest", "beach", "sunset", "wilderness"],
    "city_exploration": ["city", "urban", "street", "architecture", "cafe", "restaurant", "nightlife", "culture"],
    "international_travel": ["europe", "asia", "america", "africa", "australia", "backpacker", "solo_travel"],
    
    # Animals & Pets
    "pets": ["pets", "dogs", "cats", "animals", "cute", "puppy", "kitten", "pet_care", "animal_lover"],
    "dogs": ["dog", "puppy", "doggo", "golden_retriever", "labrador", "bulldog", "training", "dog_tricks"],
    "cats": ["cat", "kitten", "kitty", "feline", "cat_videos", "cute_cats", "cat_behavior", "cat_memes"],
    "wildlife": ["wildlife", "zoo", "safari", "birds", "ocean", "marine_life", "conservation", "nature_documentary"],
    
    # Arts & Creativity
    "diy_crafts": ["diy", "crafts", "art", "creative", "handmade", "artistic", "craft_tutorial", "maker"],
    "visual_arts": ["painting", "drawing", "sketch", "digital_art", "illustration", "artist", "artwork"],
    "photography": ["photography", "photo", "camera", "photographer", "portrait", "landscape", "street_photography"],
    "music_production": ["music_production", "beats", "studio", "producer", "mixing", "mastering", "sound_design"],
    
    # Gaming & Entertainment
    "gaming": ["gaming", "gamer", "videogames", "twitch", "esports", "pc_gaming", "console", "mobile_games"],
    "specific_games": ["minecraft", "fortnite", "among_us", "valorant", "league_of_legends", "genshin_impact"],
    "gaming_content": ["gameplay", "gaming_setup", "gaming_chair", "streaming", "lets_play", "game_review"],

    "life_skills": ["life_hacks", "adulting", "money", "finance", "career", "job", "interview", "resume"],
    
    # Business & Career
    "entrepreneurship": ["business", "entrepreneur", "startup", "hustle", "success", "motivation", "goals"],
    "finance": ["money", "investing", "stocks", "crypto", "finance_tips", "budgeting", "savings", "wealth"],
    "career_advice": ["career", "job_search", "professional", "networking", "linkedin", "resume_tips"],
    
    # Social Issues & Awareness
    "social_awareness": ["awareness", "mental_health", "self_care", "positivity", "inspiration", "kindness"],
    "environmental": ["climate", "sustainability", "eco_friendly", "zero_waste", "environment", "green_living"],
    "diversity_inclusion": ["diversity", "inclusion", "equality", "representation", "culture", "community"],
    
    # Relationships & Family
    "relationships": ["relationship", "dating", "love", "couple", "marriage", "family", "friendship"],
    "parenting": ["parenting", "mom", "dad", "baby", "kids", "children", "family_life", "pregnancy"],
    
    # Seasonal & Events
    "seasonal": ["summer", "winter", "spring", "fall", "holiday", "christmas", "halloween", "new_year"],
    "celebrations": ["party", "celebration", "birthday", "wedding", "graduation", "anniversary"],
    
    # Automotive & Transportation
    "automotive": ["cars", "automotive", "driving", "road_trip", "motorcycle", "truck", "racing"],
    
    # Books & Literature
    "books_literature": ["books", "reading", "booktok", "author", "novel", "poetry", "literature", "book_review"],
    
    # Psychology & Philosophy
    "psychology": ["psychology", "therapy", "mental_health", "self_improvement", "mindset", "philosophy"],
    
    # Random & Niche
    "satisfying": ["satisfying", "oddly_satisfying", "asmr", "relaxing", "calm", "therapeutic"],
    "weird_interesting": ["weird", "interesting", "facts", "random", "cool", "amazing", "mind_blown"],
    "nostalgia": ["nostalgia", "throwback", "90s", "2000s", "childhood", "memories", "retro", "vintage"]
}

# Select which categories to search (empty list = all categories)
ACTIVE_CATEGORIES = []  # Empty list = all categories for maximum diversity

# ===== TREND FILTERING =====
TREND_FILTERS = {
    "min_likes": 1000,          # Minimum number of likes
    "min_views": 10000,         # Minimum number of views/plays
    "min_shares": 50,           # Minimum number of shares
    "min_comments": 20,         # Minimum number of comments
    "max_age_days": 0,         # Maximum age in days (set to 0 to disable)
    "min_engagement_rate": 0.01 # Minimum engagement rate (likes/views)
}

# ===== CONTENT FILTERING =====
CONTENT_FILTERS = {
    "exclude_keywords": ["ads", "sponsored", "promotion"],  # Keywords to avoid in captions
    "min_caption_length": 100,   # Minimum caption length
    "verified_only": False,     # Only verified accounts
    "language": None            # Language filter (None = all languages)
}

# ===== DOWNLOAD SETTINGS =====
DOWNLOAD_VIDEOS = False
DOWNLOAD_DIR = "tiktok_videos"
