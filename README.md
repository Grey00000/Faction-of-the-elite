# Faction-of-the-elite

## Overview
This is a Discord bot for a CACHA game where user can create character card, spin for their favorite cards and collect them with a virtual currency(ppt-private points), it is based on "Classroom of the Elite" novel. The bot try to hep "classroom of the elite" fans to experience a unique game based on their favorite fanchise.

## File Structure
├── bot.py # Main bot file with commands  
├── config.py # Configuration and constants   
├── database.py # Database operations and MongoDB connection   
├── utils.py # Utility functions for embeds, pagination, etc.  
├── requirements.txt # Python dependencies  

## Discord appearance
#### Registration 
<img width="603" height="198" alt="Screenshot_2025-09-03_21-02-15" src="https://github.com/user-attachments/assets/b6271016-609c-4c1d-b773-249bd85122cf" />  <be>
#### User profile  
<img width="478" height="354" alt="Screenshot_2025-09-03_21-02-44" src="https://github.com/user-attachments/assets/5844c64a-7205-4254-8931-7c79a57bda62" />   <be>
#### Injecting ppt(private points) 
<img width="474" height="552" alt="Screenshot_2025-09-03_21-03-25" src="https://github.com/user-attachments/assets/457493d3-042b-4fa5-99de-3ab0b4439d39" />  <be>

#### Spinning for characters 

![WhatsApp Image 2025-09-03 at 21 56 47](https://github.com/user-attachments/assets/b2a836fd-2cea-4207-b93f-b8dea35af279)  <be>

#### User collection

![WhatsApp Image 2025-09-03 at 21 56 46](https://github.com/user-attachments/assets/8506eb8d-15e8-405f-8fe4-defbade7143b)  <be>

#### Help command
<img width="423" height="527" alt="Screenshot_2025-09-03_21-08-24" src="https://github.com/user-attachments/assets/95ef9770-a0ca-43b9-aa0f-318994aa97c3" />





## Key Features
#### User Registration System - Register users with initial PPT and tokens
#### Character Card Collection - Spin for cards with rarity system
#### Profile Management - View user stats and collection
#### Character Search - Find specific characters by name
#### Modern UI Components - Interactive buttons and views
#### Proper Error Handling - User-friendly error messages
#### Paginated Collections - Navigate through large card collections

## Commands Available
#### !register - Register as a new user
#### !profile - View your profile and stats
#### !find <name> - Search for character cards
#### !spin <amount> - Spin for character cards (costs PPT)
#### !collection - View your card collection
#### !inject - Add 100k PPT (testing only)
#### !bothelp - Show available commands

## Environment Variables Required
#### DISCORD_TOKEN - Discord bot token
#### MONGODB_PASSWORD - MongoDB connection password
