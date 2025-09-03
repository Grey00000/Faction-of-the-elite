import discord
import asyncio
from discord.ext import commands
from config import RARE_CHARACTERS, UNCOMMON_CHARACTERS, COMMON_CHARACTERS, EMOJIS
import logging

logger = logging.getLogger(__name__)

def get_character_rarity(character_name: str) -> str:
    """Determine the rarity of a character"""
    if character_name in RARE_CHARACTERS:
        return "rare"
    elif character_name in UNCOMMON_CHARACTERS:
        return "uncommon"
    elif character_name in COMMON_CHARACTERS:
        return "common"
    return "common"

def get_rarity_emoji(character_name: str) -> str:
    """Get the emoji for a character's rarity"""
    rarity = get_character_rarity(character_name)
    return EMOJIS.get(rarity, "")

def create_character_embed(user: discord.User, character_data: dict, user_character_data: dict = None) -> discord.Embed:
    """Create a Discord embed for a character card"""
    try:
        character_name = character_data["character_name"]
        personality = character_data["character_personality"]
        moves = character_data["character_moves"]
        url = character_data["character_url_image"]
        
        # Use user's collection data if available, otherwise use base data
        if user_character_data:
            resolve = user_character_data["Resolve"]
            mental = user_character_data["Mental"]
            physical = user_character_data["Physical"]
            social = user_character_data["Social"]
            initiative = user_character_data["Initiative"]
            support_bonus = user_character_data["Support_Bonus"]
            tags = user_character_data.get("Tags", "")
            card_star = user_character_data["Star"]
        else:
            resolve = character_data.get("character_resolve", 0)
            mental = character_data.get("character_mental", 0)
            physical = character_data.get("character_physical", 0)
            social = character_data.get("character_social", 0)
            initiative = character_data.get("character_initiative", 0)
            support_bonus = character_data.get("character_support_bonus", "")
            tags = character_data.get("character_tags", "")
            card_star = character_data.get("character_star", 1)

        # Create star display and rank emoji
        star_display = "⭐" * card_star
        rank_emoji = get_rarity_emoji(character_name)
        
        # Handle support bonus formatting
        formatted_support_bonus = support_bonus
        if card_star < 4 and support_bonus:
            try:
                parts = support_bonus.split(" ")
                if len(parts) >= 4:
                    parts[0] = "+16%"
                    formatted_support_bonus = " ".join(parts)
            except:
                formatted_support_bonus = support_bonus

        embed = discord.Embed(
            title=f"{rank_emoji} {character_name} {star_display}",
            description="",
            color=discord.Color.blue()
        )
        
        embed.set_author(name=user.display_name, icon_url=user.avatar.url if user.avatar else "")
        embed.set_image(url=url)
        
        embed.add_field(
            name="Character Info", 
            value=f"**Personality:** {personality}\n**Moves:** {moves}", 
            inline=False
        )
        
        embed.add_field(
            name="Stats", 
            value=f"**Resolve:** {resolve}\n**Mental:** {mental}\n**Physical:** {physical}\n**Social:** {social}\n**Initiative:** {initiative}", 
            inline=True
        )
        
        if formatted_support_bonus:
            embed.add_field(
                name="Support Bonus", 
                value=formatted_support_bonus, 
                inline=False
            )
        
        if tags:
            embed.set_footer(text=f"Tags: {tags}")

        return embed
        
    except Exception as e:
        logger.error(f"Error creating character embed: {e}")
        # Return a basic error embed
        embed = discord.Embed(
            title="Error",
            description="Could not display character card",
            color=discord.Color.red()
        )
        return embed

def format_number(num: int) -> str:
    """Format a number with commas for display"""
    return f"{num:,}"

class PaginationView(discord.ui.View):
    """Modern pagination view using buttons instead of reactions"""
    def __init__(self, embeds: list, timeout: int = 180):
        super().__init__(timeout=timeout)
        self.embeds = embeds
        self.current_page = 0
        self.total_pages = len(embeds)
        
        # Disable buttons if only one page
        if self.total_pages <= 1:
            self.previous_button.disabled = True
            self.next_button.disabled = True
    
    def update_buttons(self):
        """Update button states based on current page"""
        self.previous_button.disabled = (self.current_page == 0)
        self.next_button.disabled = (self.current_page == self.total_pages - 1)
    
    @discord.ui.button(label="◀️ Previous", style=discord.ButtonStyle.gray)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons()
            
            await interaction.response.edit_message(
                embed=self.embeds[self.current_page],
                content=f"Page {self.current_page + 1}/{self.total_pages}",
                view=self
            )
    
    @discord.ui.button(label="Next ▶️", style=discord.ButtonStyle.gray)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_buttons()
            
            await interaction.response.edit_message(
                embed=self.embeds[self.current_page],
                content=f"Page {self.current_page + 1}/{self.total_pages}",
                view=self
            )

async def send_paginated_embeds(ctx, embeds: list, timeout: int = 180):
    """Send paginated embeds with button controls"""
    if not embeds:
        await ctx.send("No results found.")
        return
    
    if len(embeds) == 1:
        # Single embed, no pagination needed
        await ctx.send(embed=embeds[0])
        return
    
    # Multiple embeds, use pagination
    view = PaginationView(embeds, timeout)
    view.update_buttons()
    
    await ctx.send(
        embed=embeds[0],
        content=f"Page 1/{len(embeds)}",
        view=view
    )

class ConfirmView(discord.ui.View):
    """Simple confirm/cancel view"""
    def __init__(self, timeout: int = 60):
        super().__init__(timeout=timeout)
        self.result = None
    
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.result = True
        await interaction.response.edit_message(content="✅ Confirmed!", view=None)
        self.stop()
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.result = False
        await interaction.response.edit_message(content="❌ Cancelled!", view=None)
        self.stop()

async def handle_error(ctx, error: Exception, command_name: str = "command"):
    """Standard error handling for commands"""
    logger.error(f"Error in {command_name}: {error}")
    
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument. Please check the command usage.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"❌ Invalid argument provided. Please check your input.")
    elif isinstance(error, commands.CommandOnCooldown):
        retry_after = getattr(error, 'retry_after', 0)
        await ctx.send(f"⏰ Command is on cooldown. Try again in {retry_after:.1f} seconds.")
    else:
        await ctx.send(f"❌ An error occurred while executing the {command_name}. Please try again later.")