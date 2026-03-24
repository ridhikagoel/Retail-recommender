"""
In-memory product catalogue and behavioural data.
These module-level constants are the sole data source for all recommender strategies.
"""

# ── Product Catalogue ─────────────────────────────────────────────────────────

PRODUCTS: list[dict] = [
    # Electronics
    {"id": "E001", "name": "ProBook Laptop 15", "category": "Electronics", "subcategory": "Laptops",
     "brand": "TechPro", "price": 899.99, "original_price": 1099.99, "rating": 4.7,
     "review_count": 342, "inventory": 45, "margin": 0.32,
     "image_url": None, "description": "15-inch laptop with Intel i7, 16GB RAM, 512GB SSD",
     "tags": ["laptop", "work", "portable", "intel", "ssd"]},

    {"id": "E002", "name": "NoiseFree Pro Headphones", "category": "Electronics", "subcategory": "Headphones",
     "brand": "SoundWave", "price": 149.99, "original_price": 199.99, "rating": 4.5,
     "review_count": 218, "inventory": 120, "margin": 0.45,
     "image_url": None, "description": "Wireless noise-cancelling over-ear headphones with 30hr battery",
     "tags": ["headphones", "wireless", "noise-cancelling", "music", "work"]},

    {"id": "E003", "name": "UltraWide Monitor 27\"", "category": "Electronics", "subcategory": "Monitors",
     "brand": "VisionTech", "price": 329.99, "original_price": 429.99, "rating": 4.6,
     "review_count": 156, "inventory": 30, "margin": 0.28,
     "image_url": None, "description": "27-inch 4K IPS monitor, USB-C, 144Hz refresh rate",
     "tags": ["monitor", "4k", "display", "work", "gaming"]},

    {"id": "E004", "name": "ErgoKeys Mechanical Keyboard", "category": "Electronics", "subcategory": "Keyboards",
     "brand": "TypeMaster", "price": 89.99, "original_price": 89.99, "rating": 4.4,
     "review_count": 287, "inventory": 200, "margin": 0.52,
     "image_url": None, "description": "Compact TKL mechanical keyboard with RGB backlight",
     "tags": ["keyboard", "mechanical", "rgb", "work", "gaming"]},

    {"id": "E005", "name": "StreamCam HD Webcam", "category": "Electronics", "subcategory": "Webcams",
     "brand": "ClearVision", "price": 69.99, "original_price": 89.99, "rating": 4.3,
     "review_count": 193, "inventory": 85, "margin": 0.48,
     "image_url": None, "description": "1080p webcam with auto-focus and built-in microphone",
     "tags": ["webcam", "work", "streaming", "video-call", "hd"]},

    {"id": "E006", "name": "PowerHub USB-C Dock", "category": "Electronics", "subcategory": "Accessories",
     "brand": "TechPro", "price": 59.99, "original_price": 79.99, "rating": 4.2,
     "review_count": 145, "inventory": 160, "margin": 0.55,
     "image_url": None, "description": "7-in-1 USB-C hub with HDMI, USB 3.0, SD card reader",
     "tags": ["hub", "usb-c", "work", "portable", "adapter"]},

    {"id": "E007", "name": "SlimPad Wireless Mouse", "category": "Electronics", "subcategory": "Peripherals",
     "brand": "TypeMaster", "price": 34.99, "original_price": 44.99, "rating": 4.1,
     "review_count": 312, "inventory": 250, "margin": 0.60,
     "image_url": None, "description": "Silent wireless mouse with ergonomic design, 18-month battery",
     "tags": ["mouse", "wireless", "silent", "ergonomic", "work"]},

    {"id": "E008", "name": "SmartSpeaker Mini", "category": "Electronics", "subcategory": "Smart Home",
     "brand": "EchoTech", "price": 44.99, "original_price": 44.99, "rating": 4.0,
     "review_count": 8, "inventory": 300, "margin": 0.40,
     "image_url": None, "description": "Compact voice-controlled smart speaker with premium sound",
     "tags": ["speaker", "smart-home", "voice", "wireless", "music"]},

    {"id": "E009", "name": "TabletPad Pro 11\"", "category": "Electronics", "subcategory": "Tablets",
     "brand": "TechPro", "price": 549.99, "original_price": 649.99, "rating": 4.6,
     "review_count": 98, "inventory": 55, "margin": 0.29,
     "image_url": None, "description": "11-inch tablet with stylus support, 256GB, WiFi 6",
     "tags": ["tablet", "portable", "stylus", "drawing", "work"]},

    {"id": "E010", "name": "FastCharge Power Bank 20K", "category": "Electronics", "subcategory": "Accessories",
     "brand": "PowerCell", "price": 39.99, "original_price": 49.99, "rating": 4.4,
     "review_count": 425, "inventory": 180, "margin": 0.50,
     "image_url": None, "description": "20,000mAh power bank with 65W fast charging, 3 ports",
     "tags": ["power-bank", "charging", "portable", "travel", "usb-c"]},

    {"id": "E011", "name": "GamerPad Controller Pro", "category": "Electronics", "subcategory": "Gaming",
     "brand": "PlayEdge", "price": 59.99, "original_price": 69.99, "rating": 4.3,
     "review_count": 267, "inventory": 90, "margin": 0.42,
     "image_url": None, "description": "Wireless game controller with haptic feedback, 40hr battery",
     "tags": ["gaming", "controller", "wireless", "console", "pc"]},

    {"id": "E012", "name": "ClearBuds True Wireless Earbuds", "category": "Electronics", "subcategory": "Headphones",
     "brand": "SoundWave", "price": 79.99, "original_price": 99.99, "rating": 4.5,
     "review_count": 189, "inventory": 140, "margin": 0.47,
     "image_url": None, "description": "ANC true wireless earbuds with 6hr playtime + 24hr case",
     "tags": ["earbuds", "wireless", "anc", "music", "sport"]},

    # Home
    {"id": "H001", "name": "BrewMaster Coffee Maker", "category": "Home", "subcategory": "Kitchen Appliances",
     "brand": "HomeEssentials", "price": 79.99, "original_price": 99.99, "rating": 4.6,
     "review_count": 534, "inventory": 65, "margin": 0.38,
     "image_url": None, "description": "12-cup programmable coffee maker with thermal carafe",
     "tags": ["coffee", "kitchen", "morning", "appliance", "programmable"]},

    {"id": "H002", "name": "AmbientGlow Desk Lamp", "category": "Home", "subcategory": "Lighting",
     "brand": "LightCraft", "price": 45.99, "original_price": 45.99, "rating": 4.4,
     "review_count": 178, "inventory": 120, "margin": 0.55,
     "image_url": None, "description": "LED desk lamp with touch control, 5 brightness levels, USB charging",
     "tags": ["lamp", "led", "work", "desk", "dimmable"]},

    {"id": "H003", "name": "ModuStack Desk Organiser Set", "category": "Home", "subcategory": "Organisation",
     "brand": "OrganiPro", "price": 34.99, "original_price": 44.99, "rating": 4.3,
     "review_count": 267, "inventory": 200, "margin": 0.62,
     "image_url": None, "description": "Modular bamboo desk organiser with 6 compartments",
     "tags": ["organiser", "bamboo", "desk", "work", "storage"]},

    {"id": "H004", "name": "CloudComfort Memory Pillow", "category": "Home", "subcategory": "Bedding",
     "brand": "SleepWell", "price": 39.99, "original_price": 55.99, "rating": 4.5,
     "review_count": 612, "inventory": 80, "margin": 0.58,
     "image_url": None, "description": "Contour memory foam pillow for side and back sleepers",
     "tags": ["pillow", "memory-foam", "sleep", "comfort", "neck"]},

    {"id": "H005", "name": "AirPure 400 Air Purifier", "category": "Home", "subcategory": "Air Quality",
     "brand": "CleanAir", "price": 129.99, "original_price": 159.99, "rating": 4.7,
     "review_count": 289, "inventory": 40, "margin": 0.35,
     "image_url": None, "description": "True HEPA air purifier for rooms up to 400 sq ft, whisper quiet",
     "tags": ["air-purifier", "hepa", "health", "home", "allergy"]},

    {"id": "H006", "name": "FreshBrew Electric Kettle", "category": "Home", "subcategory": "Kitchen Appliances",
     "brand": "HomeEssentials", "price": 29.99, "original_price": 39.99, "rating": 4.4,
     "review_count": 398, "inventory": 150, "margin": 0.50,
     "image_url": None, "description": "1.7L stainless steel kettle with temperature control, fast boil",
     "tags": ["kettle", "kitchen", "tea", "coffee", "appliance"]},

    {"id": "H007", "name": "SnapFrame Canvas 18x24", "category": "Home", "subcategory": "Decor",
     "brand": "ArtSpace", "price": 22.99, "original_price": 29.99, "rating": 4.2,
     "review_count": 143, "inventory": 300, "margin": 0.65,
     "image_url": None, "description": "Gallery-style snap frame for posters and prints, silver finish",
     "tags": ["frame", "decor", "wall-art", "home", "gallery"]},

    {"id": "H008", "name": "CleanSweep Robot Vacuum", "category": "Home", "subcategory": "Cleaning",
     "brand": "RoboClean", "price": 189.99, "original_price": 249.99, "rating": 4.5,
     "review_count": 321, "inventory": 35, "margin": 0.30,
     "image_url": None, "description": "Smart robot vacuum with mapping, auto-return, works on carpet and hardwood",
     "tags": ["vacuum", "robot", "cleaning", "smart-home", "automatic"]},

    {"id": "H009", "name": "SpiceRack Bamboo Carousel", "category": "Home", "subcategory": "Kitchen Storage",
     "brand": "OrganiPro", "price": 27.99, "original_price": 27.99, "rating": 4.3,
     "review_count": 189, "inventory": 220, "margin": 0.60,
     "image_url": None, "description": "Rotating 20-jar bamboo spice rack for countertop",
     "tags": ["spice-rack", "bamboo", "kitchen", "storage", "organisation"]},

    {"id": "H010", "name": "WarmWeave Throw Blanket", "category": "Home", "subcategory": "Bedding",
     "brand": "SleepWell", "price": 32.99, "original_price": 42.99, "rating": 4.6,
     "review_count": 476, "inventory": 100, "margin": 0.56,
     "image_url": None, "description": "Extra-large sherpa fleece throw blanket, 60x80 inches",
     "tags": ["blanket", "fleece", "cosy", "home", "sofa"]},

    # Clothing
    {"id": "C001", "name": "TrailBlazer Waterproof Jacket", "category": "Clothing", "subcategory": "Outerwear",
     "brand": "ActiveWear", "price": 119.99, "original_price": 159.99, "rating": 4.6,
     "review_count": 234, "inventory": 60, "margin": 0.45,
     "image_url": None, "description": "Lightweight waterproof jacket with packable hood, 3 colours",
     "tags": ["jacket", "waterproof", "outdoor", "travel", "packable"]},

    {"id": "C002", "name": "SwiftRun Training Shoes", "category": "Clothing", "subcategory": "Footwear",
     "brand": "StepUp", "price": 84.99, "original_price": 109.99, "rating": 4.5,
     "review_count": 387, "inventory": 75, "margin": 0.40,
     "image_url": None, "description": "Cushioned running shoes with breathable mesh upper",
     "tags": ["shoes", "running", "sport", "fitness", "breathable"]},

    {"id": "C003", "name": "ClassicFit Cotton T-Shirt 3-Pack", "category": "Clothing", "subcategory": "Tops",
     "brand": "BasicThreads", "price": 29.99, "original_price": 39.99, "rating": 4.3,
     "review_count": 812, "inventory": 500, "margin": 0.65,
     "image_url": None, "description": "100% organic cotton crew-neck t-shirts, 3-pack, assorted colours",
     "tags": ["t-shirt", "cotton", "casual", "basic", "everyday"]},

    {"id": "C004", "name": "FlexFlow Yoga Pants", "category": "Clothing", "subcategory": "Activewear",
     "brand": "ActiveWear", "price": 49.99, "original_price": 64.99, "rating": 4.7,
     "review_count": 456, "inventory": 90, "margin": 0.50,
     "image_url": None, "description": "High-waist 4-way stretch yoga pants with side pockets",
     "tags": ["yoga", "activewear", "leggings", "fitness", "stretch"]},

    {"id": "C005", "name": "UrbanChic Slim Chinos", "category": "Clothing", "subcategory": "Bottoms",
     "brand": "BasicThreads", "price": 44.99, "original_price": 44.99, "rating": 4.2,
     "review_count": 7, "inventory": 110, "margin": 0.48,
     "image_url": None, "description": "Slim-fit stretch chinos in 4 colours, office-to-weekend style",
     "tags": ["chinos", "slim", "casual", "office", "versatile"]},

    {"id": "C006", "name": "ThermoLayer Base Shirt", "category": "Clothing", "subcategory": "Base Layers",
     "brand": "ActiveWear", "price": 34.99, "original_price": 44.99, "rating": 4.4,
     "review_count": 167, "inventory": 130, "margin": 0.52,
     "image_url": None, "description": "Moisture-wicking thermal base layer for cold weather activities",
     "tags": ["thermal", "base-layer", "sport", "winter", "moisture-wicking"]},

    {"id": "C007", "name": "KnitComfort Merino Sweater", "category": "Clothing", "subcategory": "Knitwear",
     "brand": "WoolMark", "price": 69.99, "original_price": 89.99, "rating": 4.5,
     "review_count": 201, "inventory": 55, "margin": 0.43,
     "image_url": None, "description": "100% merino wool crew-neck sweater, machine washable",
     "tags": ["sweater", "merino", "wool", "casual", "warm"]},

    {"id": "C008", "name": "PocketCargo Shorts", "category": "Clothing", "subcategory": "Bottoms",
     "brand": "BasicThreads", "price": 27.99, "original_price": 35.99, "rating": 4.1,
     "review_count": 298, "inventory": 180, "margin": 0.55,
     "image_url": None, "description": "6-pocket cargo shorts with stretch waistband, quick-dry fabric",
     "tags": ["shorts", "cargo", "casual", "summer", "pockets"]},

    # Beauty
    {"id": "B001", "name": "HydraGlow Daily Moisturiser SPF30", "category": "Beauty", "subcategory": "Skincare",
     "brand": "GlowLab", "price": 28.99, "original_price": 36.99, "rating": 4.7,
     "review_count": 567, "inventory": 200, "margin": 0.68,
     "image_url": None, "description": "Lightweight daily moisturiser with SPF30 and hyaluronic acid",
     "tags": ["moisturiser", "spf", "skincare", "hydrating", "daily"]},

    {"id": "B002", "name": "VitaC Brightening Serum", "category": "Beauty", "subcategory": "Skincare",
     "brand": "GlowLab", "price": 34.99, "original_price": 46.99, "rating": 4.6,
     "review_count": 389, "inventory": 150, "margin": 0.72,
     "image_url": None, "description": "10% vitamin C serum for brightening and anti-oxidant protection",
     "tags": ["serum", "vitamin-c", "brightening", "skincare", "antioxidant"]},

    {"id": "B003", "name": "PureClean Foaming Face Wash", "category": "Beauty", "subcategory": "Cleansers",
     "brand": "NaturalSkin", "price": 14.99, "original_price": 19.99, "rating": 4.4,
     "review_count": 723, "inventory": 300, "margin": 0.70,
     "image_url": None, "description": "Gentle foaming cleanser with aloe vera and green tea extract",
     "tags": ["face-wash", "cleanser", "gentle", "skincare", "daily"]},

    {"id": "B004", "name": "SunGuard Mineral SPF50", "category": "Beauty", "subcategory": "Sun Care",
     "brand": "ShieldSkin", "price": 19.99, "original_price": 24.99, "rating": 4.5,
     "review_count": 412, "inventory": 250, "margin": 0.65,
     "image_url": None, "description": "Mineral sunscreen SPF50 with zinc oxide, reef-safe formula",
     "tags": ["sunscreen", "spf50", "mineral", "sun-care", "reef-safe"]},

    {"id": "B005", "name": "NightRepair Retinol Cream", "category": "Beauty", "subcategory": "Skincare",
     "brand": "GlowLab", "price": 42.99, "original_price": 54.99, "rating": 4.6,
     "review_count": 234, "inventory": 100, "margin": 0.71,
     "image_url": None, "description": "0.3% retinol night cream with peptides for fine lines",
     "tags": ["retinol", "night-cream", "anti-aging", "skincare", "peptides"]},

    {"id": "B006", "name": "VelvetMatte Lip Collection", "category": "Beauty", "subcategory": "Makeup",
     "brand": "ColorStudio", "price": 16.99, "original_price": 16.99, "rating": 4.3,
     "review_count": 6, "inventory": 180, "margin": 0.75,
     "image_url": None, "description": "Long-wear matte lipstick with vitamin E, 12 shades",
     "tags": ["lipstick", "matte", "makeup", "color", "long-wear"]},

    {"id": "B007", "name": "ScalpRevive Hair Serum", "category": "Beauty", "subcategory": "Hair Care",
     "brand": "NaturalSkin", "price": 22.99, "original_price": 22.99, "rating": 4.4,
     "review_count": 5, "inventory": 220, "margin": 0.66,
     "image_url": None, "description": "Nourishing scalp serum with biotin and caffeine for thicker hair",
     "tags": ["hair-serum", "biotin", "scalp", "hair-care", "growth"]},

    {"id": "B008", "name": "EyeRevive Caffeine Eye Cream", "category": "Beauty", "subcategory": "Skincare",
     "brand": "GlowLab", "price": 24.99, "original_price": 31.99, "rating": 4.5,
     "review_count": 298, "inventory": 170, "margin": 0.69,
     "image_url": None, "description": "Caffeine eye cream for dark circles and puffiness",
     "tags": ["eye-cream", "caffeine", "skincare", "dark-circles", "depuffing"]},

    # Grocery
    {"id": "G001", "name": "ProBlend Protein Bars 12-Pack", "category": "Grocery", "subcategory": "Sports Nutrition",
     "brand": "FuelUp", "price": 24.99, "original_price": 31.99, "rating": 4.4,
     "review_count": 678, "inventory": 400, "margin": 0.42,
     "image_url": None, "description": "20g protein per bar, low sugar, 4 flavours, gluten-free",
     "tags": ["protein-bar", "snack", "sport", "gluten-free", "healthy"]},

    {"id": "G002", "name": "OliveFirst Extra Virgin Olive Oil", "category": "Grocery", "subcategory": "Cooking Oils",
     "brand": "MedFresh", "price": 16.99, "original_price": 21.99, "rating": 4.7,
     "review_count": 512, "inventory": 300, "margin": 0.38,
     "image_url": None, "description": "Cold-pressed EVOO from Spanish olives, 500ml, DOP certified",
     "tags": ["olive-oil", "cooking", "healthy", "mediterranean", "evoo"]},

    {"id": "G003", "name": "RoastHouse Whole Bean Coffee 1kg", "category": "Grocery", "subcategory": "Coffee & Tea",
     "brand": "CoffeeCraft", "price": 19.99, "original_price": 25.99, "rating": 4.6,
     "review_count": 834, "inventory": 250, "margin": 0.45,
     "image_url": None, "description": "Single-origin Colombian whole bean coffee, medium roast",
     "tags": ["coffee", "whole-bean", "single-origin", "colombian", "morning"]},

    {"id": "G004", "name": "ZenBrews Matcha Ceremonial Grade", "category": "Grocery", "subcategory": "Coffee & Tea",
     "brand": "TeaTime", "price": 18.99, "original_price": 23.99, "rating": 4.5,
     "review_count": 367, "inventory": 200, "margin": 0.50,
     "image_url": None, "description": "First-flush ceremonial grade matcha from Uji, Japan, 100g",
     "tags": ["matcha", "tea", "ceremonial", "japanese", "healthy"]},

    {"id": "G005", "name": "MixedNuts Premium Selection 500g", "category": "Grocery", "subcategory": "Snacks",
     "brand": "NutHarvest", "price": 13.99, "original_price": 17.99, "rating": 4.3,
     "review_count": 445, "inventory": 350, "margin": 0.40,
     "image_url": None, "description": "Lightly salted mixed nuts: almonds, cashews, walnuts, pecans",
     "tags": ["nuts", "snack", "healthy", "protein", "natural"]},

    {"id": "G006", "name": "GreenShot Spirulina Powder 200g", "category": "Grocery", "subcategory": "Superfoods",
     "brand": "FuelUp", "price": 14.99, "original_price": 19.99, "rating": 4.2,
     "review_count": 213, "inventory": 280, "margin": 0.55,
     "image_url": None, "description": "Organic spirulina powder, rich in protein and iron, unflavoured",
     "tags": ["spirulina", "superfood", "protein", "healthy", "organic"]},

    {"id": "G007", "name": "ChocoBite Dark Chocolate 85% 6-Pack", "category": "Grocery", "subcategory": "Confectionery",
     "brand": "CocoaCraft", "price": 11.99, "original_price": 14.99, "rating": 4.5,
     "review_count": 589, "inventory": 400, "margin": 0.48,
     "image_url": None, "description": "85% cacao dark chocolate bars, ethically sourced, no added sugar",
     "tags": ["chocolate", "dark", "snack", "healthy", "cacao"]},

    {"id": "G008", "name": "FarmFresh Honey Raw 450g", "category": "Grocery", "subcategory": "Sweeteners",
     "brand": "HivePure", "price": 12.99, "original_price": 15.99, "rating": 4.6,
     "review_count": 398, "inventory": 320, "margin": 0.44,
     "image_url": None, "description": "Raw unfiltered wildflower honey, no additives, glass jar",
     "tags": ["honey", "raw", "natural", "sweetener", "wildflower"]},

    # Toys
    {"id": "T001", "name": "StrategyQuest Board Game", "category": "Toys", "subcategory": "Board Games",
     "brand": "PlayMind", "price": 34.99, "original_price": 44.99, "rating": 4.6,
     "review_count": 312, "inventory": 80, "margin": 0.50,
     "image_url": None, "description": "Award-winning strategy board game for 2-6 players, age 10+",
     "tags": ["board-game", "strategy", "family", "multiplayer", "award-winning"]},

    {"id": "T002", "name": "BrickCity Space Station 1200pcs", "category": "Toys", "subcategory": "Building Sets",
     "brand": "BrickWorld", "price": 79.99, "original_price": 99.99, "rating": 4.8,
     "review_count": 445, "inventory": 55, "margin": 0.38,
     "image_url": None, "description": "1200-piece space station building set with 4 mini-figures, age 9+",
     "tags": ["lego", "building", "space", "creative", "stem"]},

    {"id": "T003", "name": "ArtMaster Craft Kit Deluxe", "category": "Toys", "subcategory": "Arts & Crafts",
     "brand": "CreativeKids", "price": 24.99, "original_price": 31.99, "rating": 4.4,
     "review_count": 276, "inventory": 120, "margin": 0.58,
     "image_url": None, "description": "150-piece art and craft kit: watercolours, clay, stencils, glitter",
     "tags": ["craft", "art", "creative", "kids", "watercolour"]},

    {"id": "T004", "name": "RacerX RC Car 4WD", "category": "Toys", "subcategory": "Remote Control",
     "brand": "SpeedKing", "price": 49.99, "original_price": 64.99, "rating": 4.3,
     "review_count": 198, "inventory": 65, "margin": 0.44,
     "image_url": None, "description": "1:16 scale 4WD remote control off-road car, 30mph, age 8+",
     "tags": ["rc-car", "remote-control", "racing", "outdoor", "4wd"]},

    {"id": "T005", "name": "PuzzleWorld 1000pc Landscape", "category": "Toys", "subcategory": "Puzzles",
     "brand": "PlayMind", "price": 17.99, "original_price": 22.99, "rating": 4.5,
     "review_count": 367, "inventory": 200, "margin": 0.60,
     "image_url": None, "description": "1000-piece mountain landscape jigsaw puzzle, premium quality pieces",
     "tags": ["puzzle", "jigsaw", "family", "relaxing", "landscape"]},

    {"id": "T006", "name": "ScienceLab Discovery Kit", "category": "Toys", "subcategory": "Educational",
     "brand": "CreativeKids", "price": 32.99, "original_price": 32.99, "rating": 4.7,
     "review_count": 9, "inventory": 90, "margin": 0.52,
     "image_url": None, "description": "50 science experiments kit for ages 8-12, includes lab equipment",
     "tags": ["science", "educational", "stem", "experiments", "kids"]},
]


# ── Purchase History ──────────────────────────────────────────────────────────
# user_id -> list of product_ids purchased

PURCHASE_HISTORY: dict[str, list[str]] = {
    "current_user": ["E001", "E002", "E004", "H002", "H003", "H005"],
    "user_01":      ["E002", "E012", "B001", "B003", "G003"],
    "user_02":      ["E001", "E003", "E006", "H002", "H008"],
    "user_03":      ["H001", "H006", "G002", "G003", "G007", "G008"],
    "user_04":      ["C001", "C002", "C004", "G001", "G005"],
    "user_05":      ["B001", "B002", "B003", "B004", "B005", "G004"],
    "user_06":      ["E004", "E007", "E010", "H003", "H009"],
    "user_07":      ["T001", "T002", "T005", "G007", "C003"],
    "user_08":      ["E001", "E009", "H005", "H008", "B001"],
    "user_09":      ["C002", "C004", "C006", "G001", "G005", "G006"],
    "user_10":      ["E002", "E012", "E011", "H002", "H010"],
    "user_11":      ["B001", "B002", "B008", "H004", "H010"],
    "user_12":      ["G002", "G003", "G004", "G007", "G008", "H001"],
    "user_13":      ["E003", "E005", "E006", "H002", "H007"],
    "user_14":      ["C001", "C007", "B003", "G005", "T003"],
    "user_15":      ["E001", "E004", "E006", "H003", "H009"],
    "user_16":      ["T001", "T002", "T004", "G007", "C008"],
    "user_17":      ["B003", "B004", "B005", "G004", "H004"],
    "user_18":      ["E010", "H006", "G001", "G003", "C003"],
    "user_19":      ["E011", "T001", "T004", "C008", "G005"],
    "user_20":      ["H001", "H004", "H010", "B001", "G008"],
    "user_21":      ["E002", "E007", "E012", "H002", "B002"],
    "user_22":      ["C002", "C004", "C007", "G001", "G006"],
    "user_23":      ["E001", "E003", "H005", "H008", "B008"],
    "user_24":      ["T002", "T003", "T005", "T006", "G007", "C003"],
}


# ── Trending Data ─────────────────────────────────────────────────────────────
# product_id -> 7-day purchase count

TRENDING_DATA: dict[str, int] = {
    "E001": 187, "E002": 143, "E003": 98,  "E004": 165, "E005": 76,
    "E007": 112, "E010": 134, "E012": 88,
    "H001": 156, "H003": 89,  "H004": 201, "H005": 67,  "H006": 121,
    "H008": 54,  "H010": 178,
    "C002": 93,  "C003": 145, "C004": 112,
    "B001": 167, "B002": 89,  "B003": 203, "B004": 134,
    "G001": 78,  "G003": 192, "G004": 87,  "G005": 65,  "G007": 144, "G008": 99,
    "T001": 71,  "T002": 83,
}


# ── New Arrivals ──────────────────────────────────────────────────────────────
# Product IDs added in the last 30 days (low review_count products)

NEW_ARRIVALS: list[str] = ["E008", "E009", "C005", "B006", "B007", "H007", "G006", "T006"]


# ── Flash Deals ───────────────────────────────────────────────────────────────
# product_id -> {discount_pct, ends_hours}
# All products must have margin > MIN_FLASH_MARGIN (0.10)

FLASH_DEALS: dict[str, dict] = {
    "E003": {"discount_pct": 23, "ends_hours": 6},    # margin 0.28 — monitor
    "H004": {"discount_pct": 29, "ends_hours": 4},    # margin 0.58 — pillow
    "B002": {"discount_pct": 26, "ends_hours": 10},   # margin 0.72 — serum
    "G002": {"discount_pct": 23, "ends_hours": 8},    # margin 0.38 — olive oil
    "C001": {"discount_pct": 25, "ends_hours": 3},    # margin 0.45 — jacket
    "T002": {"discount_pct": 20, "ends_hours": 12},   # margin 0.38 — building set
}


# ── Editorial Picks ───────────────────────────────────────────────────────────
# Curated theme -> [product_ids]
# "Work From Home" must exist — used by get_landing_page orchestrator

EDITORIAL_PICKS: dict[str, list[str]] = {
    "Work From Home": [
        "E001", "E002", "E003", "E004", "E005", "E006", "E007",
        "H002", "H003", "H009", "G003",
    ],
    "Self Care": [
        "B001", "B002", "B003", "B004", "B005", "B008",
        "G004", "G007", "H004", "H010",
    ],
    "Home Refresh": [
        "H001", "H002", "H003", "H005", "H006", "H008",
        "H009", "H010", "G002", "G008",
    ],
}


# ── DB Access Helpers (psycopg2) ──────────────────────────────────────────────

def get_connection():
    """Return a new psycopg2 connection. Caller is responsible for closing."""
    import psycopg2
    from backend.config import (
        POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB,
        POSTGRES_USER, POSTGRES_PASSWORD,
    )
    return psycopg2.connect(
        host=POSTGRES_HOST, port=POSTGRES_PORT, dbname=POSTGRES_DB,
        user=POSTGRES_USER, password=POSTGRES_PASSWORD,
    )


def fetch_product_by_id(conn, product_id: str) -> dict | None:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        row = cur.fetchone()
        if row is None:
            return None
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))


def fetch_products(conn, category: str | None = None) -> list[dict]:
    with conn.cursor() as cur:
        if category:
            cur.execute("SELECT * FROM products WHERE category = %s", (category,))
        else:
            cur.execute("SELECT * FROM products")
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def fetch_purchase_history(conn) -> dict[str, list[str]]:
    with conn.cursor() as cur:
        cur.execute("SELECT user_id, product_id FROM purchases ORDER BY purchased_at")
        result: dict[str, list[str]] = {}
        for user_id, product_id in cur.fetchall():
            result.setdefault(user_id, []).append(product_id)
        return result


def fetch_trending_data(conn, days: int = 7) -> dict[str, int]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT product_id, COUNT(*) AS cnt
            FROM purchases
            WHERE purchased_at >= NOW() - (%(days)s || ' days')::INTERVAL
            GROUP BY product_id
            """,
            {"days": days},
        )
        return {row[0]: row[1] for row in cur.fetchall()}
