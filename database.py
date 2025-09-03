from pymongo import MongoClient
from config import MONGODB_URI, DB_NAME, COLLECTIONS
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        try:
            self.client = MongoClient(MONGODB_URI)
            self.db = self.client[DB_NAME]
            self.cards = self.db[COLLECTIONS['cards']]
            self.students = self.db[COLLECTIONS['students']]
            self.battle = self.db[COLLECTIONS['battle']]
            self.temp = self.db[COLLECTIONS['temp']]
            logger.info("Database connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def get_card_by_name(self, character_name: str):
        """Get a character card by name"""
        try:
            return self.cards.find_one({"character_name": character_name})
        except Exception as e:
            logger.error(f"Error fetching card {character_name}: {e}")
            return None

    def search_cards(self, search_term: str):
        """Search for cards by name (case-insensitive)"""
        try:
            return list(self.cards.find({"character_name": {"$regex": search_term, "$options": "i"}}))
        except Exception as e:
            logger.error(f"Error searching cards with term {search_term}: {e}")
            return []

    def get_user(self, user_id: int):
        """Get user data by Discord ID"""
        try:
            return self.students.find_one({"_id": user_id})
        except Exception as e:
            logger.error(f"Error fetching user {user_id}: {e}")
            return None

    def create_user(self, user_id: int, username: str, initial_ppt: int = 100000, initial_tokens: int = 30):
        """Create a new user"""
        try:
            user_data = {
                "_id": user_id,
                "name": username,
                "ppt": initial_ppt,
                "black_token": initial_tokens,
                "ftps": 0,
                "collection": {}
            }
            self.students.insert_one(user_data)
            logger.info(f"Created new user: {username} ({user_id})")
            return user_data
        except Exception as e:
            logger.error(f"Error creating user {user_id}: {e}")
            return None

    def update_user_ppt(self, user_id: int, amount: int):
        """Update user's PPT (add or subtract)"""
        try:
            self.students.update_one(
                {"_id": user_id},
                {"$inc": {"ppt": amount}}
            )
            return True
        except Exception as e:
            logger.error(f"Error updating PPT for user {user_id}: {e}")
            return False

    def add_card_to_collection(self, user_id: int, character_data: dict):
        """Add a card to user's collection or upgrade existing one"""
        try:
            character_name = character_data["character_name"]
            user = self.get_user(user_id)
            
            if not user:
                return False
                
            if "collection" not in user:
                user["collection"] = {}
            
            # If character doesn't exist in collection, add it
            if character_name not in user["collection"]:
                user["collection"][character_name] = {
                    "Mental": character_data.get("character_mental", 0),
                    "Physical": character_data.get("character_physical", 0),
                    "Social": character_data.get("character_social", 0),
                    "Resolve": character_data.get("character_resolve", 0),
                    "Initiative": character_data.get("character_initiative", 0),
                    "Support_Bonus": character_data.get("character_support_bonus", ""),
                    "Tags": character_data.get("character_tags", ""),
                    "Star": character_data.get("character_star", 1)
                }
            else:
                # Upgrade existing character
                current_star = user["collection"][character_name].get("Star", 1)
                if current_star < 5:
                    user["collection"][character_name]["Star"] = current_star + 1
                    # Increase stats
                    stats_to_increase = ["Mental", "Physical", "Social", "Initiative", "Resolve"]
                    for stat in stats_to_increase:
                        user["collection"][character_name][stat] += 20
            
            self.students.update_one({"_id": user_id}, {"$set": user})
            return True
            
        except Exception as e:
            logger.error(f"Error adding card to collection for user {user_id}: {e}")
            return False

    def get_user_collection(self, user_id: int):
        """Get user's card collection"""
        try:
            user = self.get_user(user_id)
            return user.get("collection", {}) if user else {}
        except Exception as e:
            logger.error(f"Error getting collection for user {user_id}: {e}")
            return {}

# Global database instance
db = Database()