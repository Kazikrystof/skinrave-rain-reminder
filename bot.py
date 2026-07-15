import discord
from discord.ext import commands
from discord import app_commands
import json, os
from dotenv import load_dotenv
from pathlib import Path
from logger import log
import scraper


BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / "configs.json"
load_dotenv(BASE_DIR / ".env")
TOKEN = os.getenv("TOKEN")


MY_GUILD_ID = 1500953012409991229

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

guild = discord.Object(id=MY_GUILD_ID)


@bot.event
async def on_ready():
    synced = await bot.tree.sync()

    print(f"Synchronizováno {len(synced)} příkazů")


async def send_pot_alert(channel_id, amount, role_id=None):

    channel = bot.get_channel(channel_id)

    if not channel:
        return
    mention = ""

    if role_id:
        mention = f"<@&{role_id}>"

    embed = discord.Embed(
        title="💰 Pot Alert!",
        description=f"The rain pot has reached **${amount}**.",
        color=discord.Color.gold()
    )

    embed.add_field(
        name="🌐 Site",
        value="SkinRave",
        inline=True
    )

    embed.add_field(
        name="🔗 Join",
        value="[Click here](https://skinrave.gg/)",
        inline=False
    )

    embed.set_footer(
        text="Rain Checker • By kazikrystof"
    )

    await channel.send(
    content=mention,
    embed=embed
)

@app_commands.checks.has_permissions(administrator=True)
@bot.tree.command(
    name="potalert",
    description="Set the minimum pot value for notifications."
)
@app_commands.describe(
    amount="Minimum pot amount",
    role="Role to mention (optional)"
)
async def potalert(interaction: discord.Interaction, amount: float, role: discord.Role | None = None):

    guild_id = str(interaction.guild.id)

    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Setup nebyl proveden
    if guild_id not in data:
        await interaction.response.send_message(
            "❌ Please use **/setup** first.",
            ephemeral=True
        )
        return

    # Uložení hodnoty
    data[guild_id]["min_pot"] = amount
    if role:
        data[guild_id]["pot_role"] = role.id
    else:
        data[guild_id]["pot_role"] = None

    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    await interaction.response.send_message(
        f"✅ Pot alert has been set to **${amount}**."
    )

@bot.tree.command(
    name="pot",
    description="Shows the current rain pot"
)
async def pot(interaction: discord.Interaction):

    if scraper.amount is None:
        embed = discord.Embed(
            title="🌧️ Rain Pot",
            description="No rain is currently active.",
            color=discord.Color.red()
        )

        embed.set_footer(
            text="Rain Checker • By kazikrystof"
        )

        await interaction.response.send_message(embed=embed)
        return

    embed = discord.Embed(
        title="🌧️ Current Rain Pot",
        color=discord.Color.green()
    )

    embed.add_field(
        name="💰 Amount",
        value=f"${scraper.amount}",
        inline=True
    )

    embed.add_field(
        name="🌐 Site",
        value="SkinRave",
        inline=True
    )

    embed.set_footer(
        text="Rain Checker • By kazikrystof"
    )

    await interaction.response.send_message(embed=embed)

@app_commands.checks.has_permissions(administrator=True)
@bot.tree.command(
    name="setup",
    description="Select current channel for rain notifications",
    
)
async def setup(interaction: discord.Interaction):

    guild_id = str(interaction.guild.id)
    channel_id = interaction.channel.id

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    data[guild_id] = {
        "channel_id": channel_id
    }

    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    await interaction.response.send_message(
        "✅ Tento kanál byl nastaven pro Rain notifikace."
    )


async def send_rain(channel_id, amount, online):
    

    channel = bot.get_channel(channel_id)

    print("Channel:", channel)

    if not channel:
        print("❌ Channel nebyl nalezen!")
        return

    channel = bot.get_channel(channel_id)

    if not channel:
        return

    embed = discord.Embed(
        title="🌧️ Rain Started!",
        description="A new **SkinRave Rain** has just started.",
        color=discord.Color.green()
    )

    embed.add_field(
        name="💰 Rain Pool",
        value=f"**${amount}**",
        inline=True
    )

    embed.add_field(
        name="🌐 Site",
        value="SkinRave",
        inline=True
    )
    embed.add_field(
        name="👥 Online ",
        value=f"{online}",
        inline=True
        )

    embed.add_field(
        name="🔗 Join",
        value="[Click here](https://skinrave.gg/)",
        inline=False
    )

    embed.set_footer(
        text="Rain Checker • By kazikrystof"
    )

    await channel.send(embed=embed)

async def testall(ctx):
    print("TESTALL START")

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        print(data)

        for guild_id, guild in data.items():
            channel_id = guild["channel_id"]

            print(f"Guild: {guild_id}")
            print(f"Channel: {channel_id}")

            await send_rain(
                channel_id,
                "19.05",
                "852"
            )

            print("Odesláno")

        await ctx.send("✅ Hotovo")

    except Exception as e:
        print("CHYBA:", repr(e))
        await ctx.send(f"❌ {e}")

@app_commands.checks.has_permissions(administrator=True)
@bot.tree.command(
    name="help",
    description="Shows all available commands."
)
async def help(interaction: discord.Interaction):

    embed = discord.Embed(
        title="📖 Rain Checker Commands",
        color=discord.Color.blue()
    )

    commands = sorted(bot.tree.get_commands(), key=lambda c: c.name)

    for command in commands:
        embed.add_field(
            name=f"/{command.name}",
            value=command.description or "No description",
            inline=False
        )

    embed.set_footer(text="Rain Checker • By kazikrystof")

    await interaction.response.send_message(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    print("COMMAND ERROR:", repr(error))