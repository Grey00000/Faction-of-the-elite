from pymongo import MongoClient

uri = your link provided by mongodb
mongo_client = MongoClient(uri)
db = mongo_client.get_database('ROTE')
card = db["cards"]
class card_creation:
  # print("hello")

  @staticmethod
  def card_data():
      character_id = int(input("Enter the card id: "))
      character_name = input("What is the name of your character? ")
      character_personality = input("What is the personality of your character? ")
      character_moves = input("What are the moves of your character? ")
      character_url_image = input("What is the URL of the image of your character? ")
      character_star = int(input("What is the star of your character? "))
      character_resolve = int(input("What is the resolve of your character? "))
      character_mental = int(input("What is the mental health of your character? "))
      character_physical = int(input("What is the physical health of your character? "))
      character_social = int(input("What is the social health of your character? "))
      character_initiative = int(input("What is the initiative of your character? "))
      character_support_bonus = input("What is the support bonus of your character? ")
      character_tags = input("What are the tags of this character? ")

      # Create a dictionary with the character data
      character_data = {
          "character_name": character_name,
          "character_personality": character_personality,
          "character_moves": character_moves,
          "character_url_image": character_url_image,
          "character_star": character_star,
          "character_resolve": character_resolve,
          "character_mental": character_mental,
          "character_physical": character_physical,
          "character_social": character_social,
          "character_initiative": character_initiative,
          "character_support_bonus": character_support_bonus,
          "character_tags": character_tags,
          "_id": character_id
      }

      # Insert the character data into the 'cards' collection
      card.insert_one(character_data)

# Call the card_data method to input character data
card_creation.card_data() 
