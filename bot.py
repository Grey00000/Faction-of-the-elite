import os
import logging
import discord
import asyncio
import random
from discord.ext import commands
from database import db
from utils import (
    create_character_embed, send_paginated_embeds, 
    format_number, handle_error, ConfirmView
)
from config import (
    DISCORD_TOKEN, COMMAND_PREFIX, ALL_CHARACTERS, 
    SPIN_COST, MAX_SPINS_PER_COMMAND, INITIAL_PPT, INITIAL_BLACK_TOKENS
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot setup
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

@bot.event
async def on_ready():
    logger.info(f"Bot logged in as {bot.user.name}")
    print(f"✅ {bot.user.name} is ready!")

@bot.event
async def on_command_error(ctx, error):
    await handle_error(ctx, error, ctx.command.name if ctx.command else "unknown")

# User Registration Command
@bot.command(name='register')
async def register_user(ctx):
    """Register a new user in the bot system"""
    try:
        user_id = ctx.author.id
        username = ctx.author.display_name
        
        # Check if user already exists
        existing_user = db.get_user(user_id)
        if existing_user:
            embed = discord.Embed(
                title="Already Registered!",
                description="You are already registered in the system.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return
        
        # Create new user
        new_user = db.create_user(user_id, username, INITIAL_PPT, INITIAL_BLACK_TOKENS)
        if new_user:
            embed = discord.Embed(
                title="Registration Successful!",
                description=f"Welcome {username}! You've been registered with {format_number(INITIAL_PPT)} PPT and {INITIAL_BLACK_TOKENS} Black Tokens.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        else:
            raise Exception("Failed to create user")
            
    except Exception as e:
        await handle_error(ctx, e, "register")

# Profile Command
@bot.command(name='profile')
async def view_profile(ctx):
    """View your user profile"""
    try:
        user_id = ctx.author.id
        user_data = db.get_user(user_id)
        
        if not user_data:
            embed = discord.Embed(
                title="Not Registered",
                description="You need to register first! Use `!register` to get started.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="Your Profile",
            color=discord.Color.blue()
        )
        embed.set_author(
            name=ctx.author.display_name, 
            icon_url=ctx.author.avatar.url if ctx.author.avatar else ""
        )
        embed.set_thumbnail(url="https://i.pinimg.com/564x/f2/39/fb/f239fb9dde7db666cc92cea145e10934.jpg")
        
        embed.add_field(name="Name", value=user_data["name"], inline=False)
        embed.add_field(name="PPT", value=format_number(user_data["ppt"]), inline=True)
        embed.add_field(name="Black Tokens", value=user_data["black_token"], inline=True)
        embed.add_field(name="FTPS", value=user_data["ftps"], inline=True)
        
        # Collection info
        collection = user_data.get("collection", {})
        embed.add_field(name="Cards Collected", value=len(collection), inline=True)
        
        await ctx.send(embed=embed, delete_after=60)
        
    except Exception as e:
        await handle_error(ctx, e, "profile")

# Find Character Command
@bot.command(name='find')
async def find_character(ctx, *, character_name: str):
    """Search for character cards by name"""
    try:
        matching_cards = db.search_cards(character_name)
        
        if not matching_cards:
            embed = discord.Embed(
                title="No Results",
                description=f"No characters found matching '{character_name}'",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        embeds = []
        for card_data in matching_cards:
            embed = create_character_embed(ctx.author, card_data)
            embeds.append(embed)
        
        await send_paginated_embeds(ctx, embeds)
        
    except Exception as e:
        await handle_error(ctx, e, "find")

# Collection Command
@bot.command(name='collection')
async def view_collection(ctx):
    """View your character collection"""
    try:
        user_id = ctx.author.id
        user_data = db.get_user(user_id)
        
        if not user_data or not user_data.get("collection"):
            embed = discord.Embed(
                title="Empty Collection",
                description="You don't have any characters yet! Use `!spin` to get some cards.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return
        
        collection = user_data["collection"]
        embeds = []
        
        for character_name, character_data in collection.items():
            card_data = db.get_card_by_name(character_name)
            if card_data:
                embed = create_character_embed(ctx.author, card_data, character_data)
                embeds.append(embed)
        
        await send_paginated_embeds(ctx, embeds)
        
    except Exception as e:
        await handle_error(ctx, e, "collection")

# Spin Command with modern UI
class SpinView(discord.ui.View):
    def __init__(self, ctx, num_spins: int):
        super().__init__(timeout=300)
        self.ctx = ctx
        self.num_spins = num_spins
        self.total_cost = num_spins * SPIN_COST
        self.spin_results = []
        
    @discord.ui.button(label="Confirm Spin", style=discord.ButtonStyle.green, emoji="🎰")
    async def confirm_spin(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("This is not your spin!", ephemeral=True)
            return
            
        await interaction.response.defer()
        
        # Check user has enough PPT
        user_data = db.get_user(self.ctx.author.id)
        if not user_data or user_data["ppt"] < self.total_cost:
            embed = discord.Embed(
                title="Insufficient PPT",
                description=f"You need {format_number(self.total_cost)} PPT but only have {format_number(user_data['ppt'] if user_data else 0)}",
                color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=embed, view=None)
            return
        
        # Perform spins
        embed = discord.Embed(title="🎰 Spinning cards...", description="Please wait...")
        await interaction.edit_original_response(embed=embed, view=None)
        
        for i in range(self.num_spins):
            selected_character = random.choice(ALL_CHARACTERS)
            character_data = db.get_card_by_name(selected_character)
            
            if character_data:
                # Add to user's collection (this handles both new cards and upgrades)
                db.add_card_to_collection(self.ctx.author.id, character_data)
                
                # ALWAYS get the updated character data and create an embed for each spin
                updated_user = db.get_user(self.ctx.author.id)
                user_character_data = updated_user["collection"].get(selected_character)
                
                embed = create_character_embed(self.ctx.author, character_data, user_character_data)
                self.spin_results.append(embed)
            else:
                # If no character data found, create a basic error embed but still count the spin
                error_embed = discord.Embed(
                    title="Unknown Character",
                    description=f"Could not find data for {selected_character}",
                    color=discord.Color.orange()
                )
                self.spin_results.append(error_embed)
            
            # Update progress every few spins
            if (i + 1) % 3 == 0 or i == self.num_spins - 1:
                progress_embed = discord.Embed(
                    title="🎰 Spinning cards...", 
                    description=f"Progress: {i+1}/{self.num_spins}"
                )
                await interaction.edit_original_response(embed=progress_embed)
        
        # Deduct PPT
        db.update_user_ppt(self.ctx.author.id, -self.total_cost)
        
        # Show results
        if self.spin_results:
            await send_paginated_embeds(self.ctx, self.spin_results)
        
        final_embed = discord.Embed(
            title="Spin Complete!",
            description=f"Processed {self.num_spins} spins and obtained {len(self.spin_results)} results for {format_number(self.total_cost)} PPT",
            color=discord.Color.green()
        )
        await interaction.edit_original_response(embed=final_embed, view=None)
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="❌")
    async def cancel_spin(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("This is not your spin!", ephemeral=True)
            return
            
        embed = discord.Embed(title="Spin Cancelled", color=discord.Color.red())
        await interaction.response.edit_message(embed=embed, view=None)

@bot.command(name='spin')
async def spin_cards(ctx, num_spins: int = 1):
    """Spin for character cards"""
    try:
        # Validate input
        if num_spins < 1 or num_spins > MAX_SPINS_PER_COMMAND:
            embed = discord.Embed(
                title="Invalid Spin Count",
                description=f"You can spin between 1 and {MAX_SPINS_PER_COMMAND} cards at once.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        # Check if user is registered
        user_data = db.get_user(ctx.author.id)
        if not user_data:
            embed = discord.Embed(
                title="Not Registered",
                description="You need to register first! Use `!register` to get started.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        total_cost = num_spins * SPIN_COST
        
        embed = discord.Embed(
            title="🎰 Confirm Spin",
            description=f"Spin {num_spins} card{'s' if num_spins > 1 else ''} for {format_number(total_cost)} PPT?",
            color=discord.Color.blue()
        )
        embed.add_field(name="Your PPT", value=format_number(user_data["ppt"]), inline=True)
        embed.add_field(name="Cost", value=format_number(total_cost), inline=True)
        embed.add_field(name="Remaining", value=format_number(user_data["ppt"] - total_cost), inline=True)
        
        view = SpinView(ctx, num_spins)
        await ctx.send(embed=embed, view=view)
        
    except Exception as e:
        await handle_error(ctx, e, "spin")

# Inject PPT Command (for testing)
@bot.command(name='inject')
async def inject_ppt(ctx):
    """Add 100k PPT to your account (for testing)"""
    try:
        user_data = db.get_user(ctx.author.id)
        if not user_data:
            await ctx.send("You need to register first!")
            return
        
        db.update_user_ppt(ctx.author.id, 100000)
        embed = discord.Embed(
            title="PPT Injected!",
            description="Added 100,000 PPT to your account.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        
    except Exception as e:
        await handle_error(ctx, e, "inject")

# Help Command
@bot.command(name='bothelp')
async def custom_help(ctx):
    """Show bot commands and information"""
    embed = discord.Embed(
        title="🎴 ROTE Bot Commands",
        description="Character Card Collection & Battle Bot",
        color=discord.Color.purple()
    )
    
    commands_info = [
        ("!register", "Register as a new user"),
        ("!profile", "View your profile and stats"),
        ("!find <name>", "Search for character cards"),
        ("!spin <amount>", "Spin for character cards (costs PPT)"),
        ("!collection", "View your card collection"),
        ("!inject", "Add 100k PPT (testing only)"),
        ("!bothelp", "Show this help message")
    ]
    
    for command, description in commands_info:
        embed.add_field(name=command, value=description, inline=False)
    
    embed.set_footer(text="Use the commands to start collecting characters!")
    await ctx.send(embed=embed)

# Run the bot
def main():
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN not found in environment variables!")
        print("❌ Please set your DISCORD_TOKEN in the .env file")
        return
    
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        print(f"❌ Failed to start bot: {e}")

if __name__ == "__main__":
    main()