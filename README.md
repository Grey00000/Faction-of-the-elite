# Faction-of-the-elite

## Overview
This is a Discord bot for a CACHA game where user can create character card, spin for their favorite cards and collect them with a virtual currency(ppt-private points), it is based on "Classroom of the Elite" novel. The bot try to hep "classroom of the elite" fans to experience a unique game based on their favorite fanchise.

## File Structure
├── bot.py # Main bot file with commands 
├── config.py # Configuration and constants 
├── database.py # Database operations and MongoDB connection 
├── utils.py # Utility functions for embeds, pagination, etc. 
├── requirements.txt # Python dependencies 

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
#### !help - Show available commands

## Environment Variables Required
#### DISCORD_TOKEN - Discord bot token
#### MONGODB_PASSWORD - MongoDB connection password
