import os

# Bot Configuration
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
MONGODB_PASSWORD = os.environ.get('MONGODB_PASSWORD')
MONGODB_URI = f"mongodb+srv://kiyotakas048:{MONGODB_PASSWORD}@cluster0.ffx6f52.mongodb.net/?retryWrites=true&w=majority"

# Bot Settings
COMMAND_PREFIX = "!"
SPIN_COST = 2000
MAX_SPINS_PER_COMMAND = 30
INITIAL_PPT = 100000
INITIAL_BLACK_TOKENS = 30

# Database Collections
DB_NAME = 'ROTE'
COLLECTIONS = {
    'cards': 'cards',
    'students': 'students',
    'battle': 'BATTLE',
    'temp': 'tem'
}

# Character Rarities
RARE_CHARACTERS = [
    "Ayanokoji kiyotaka", "Horikita suzune", "Kushida kikyo", 
    "Koenji Rokusuke", "Kiryūin Fūka", "Ichinose Honami",
    "Sakayanagi Arisu", "Takuya yagami"
]

UNCOMMON_CHARACTERS = [
    "Sudo ken", "Hirata yosuke", "Chabashira sae"
]

COMMON_CHARACTERS = [
    "Karuizawa Kei", "Tachibana akane", 
    "Yamamura miki", "Tsubaki sakurako"
]

# All characters for spinning (with duplicate weights for rarity)
ALL_CHARACTERS = (
    RARE_CHARACTERS + 
    UNCOMMON_CHARACTERS * 2 + 
    COMMON_CHARACTERS * 3
)

# Move Types
MENTAL_ATTACKS = ["Academic", "Scheming"]
PHYSICAL_ATTACKS = ["Fighting", "Athleticism"] 
SOCIAL_ATTACKS = ["Influence", "Empathy"]

# Custom Emoji Replacements (using Unicode emojis since custom ones aren't working)
EMOJIS = {
    'rare': "✨",      # Sparkles for rare/shiny
    'uncommon': "🌟",   # Star for uncommon/glow  
    'common': "⚪"      # White circle for common
}