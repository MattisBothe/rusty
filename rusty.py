import re
import discord
from discord import app_commands
import requests
import asyncio
import os
import platform
import psutil
import time
from dotenv import load_dotenv

# ===== Konfiguration =====
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
API_KEY = os.getenv("GEMINI_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID"))

if not TOKEN or not API_KEY or not OWNER_ID:
    raise ValueError("❌ Fehlende Umgebungsvariablen! Bitte .env Datei prüfen.")

# ===== Whitelist =====
# Füge hier die Discord User-IDs ein die /ask nutzen dürfen
# Deine eigene ID muss hier nicht rein, deine ID muss in die .env
WHITELIST = {
    # 123456789012345678,  # Beispiel: Freund 1
    # 987654321098765432,  # Beispiel: Freund 2
}

# ===== Bot Setup =====
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

start_time = time.time()

os.makedirs("logs", exist_ok=True)


# ===== Logging Funktion =====
def log_user(user_id: int, user_name: str, location: str, frage: str, antwort: str):
    filename = f"logs/{user_id}.txt"
    try:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(f"{user_name} | {location}\nFrage: {frage}\nAntwort: {antwort}\n---\n")
    except Exception as e:
        print(f"[Logging Fehler] {e}")


# ===== Bot ready =====
@client.event
async def on_ready():
    await tree.sync()
    print(f"Rusty ist online als {client.user}")


# ===== /ping =====
@tree.command(name="ping", description="Zeigt deinen Ping")
async def ping(interaction: discord.Interaction):
    latency = round(client.latency * 1000)
    await interaction.response.send_message(f"Pong! 🏓\nPing: {latency} ms")


# ===== /uptime =====
@tree.command(name="uptime", description="Wie lange Rusty läuft")
async def uptime(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Nur für Entwickler.", ephemeral=True)
        return

    uptime_seconds = int(time.time() - start_time)
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60

    await interaction.response.send_message(f"⏱ Rusty läuft seit: {hours}h {minutes}m {seconds}s")


# ===== /info =====
@tree.command(name="info", description="System Infos anzeigen")
async def info(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Nur für Entwickler.", ephemeral=True)
        return

    cpu = platform.processor()
    cores = psutil.cpu_count()
    freq = psutil.cpu_freq()
    freq_mhz = round(freq.current, 2) if freq else "Unbekannt"
    ram = round(psutil.virtual_memory().total / (1024 ** 3), 2)

    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        gpu_info = "\n".join(
            [f"{g.name} ({round(g.memoryTotal / 1024, 2)} GB VRAM)" for g in gpus]
        ) or "Keine GPU gefunden"
    except Exception:
        gpu_info = "Keine GPU"

    text = (
        f"💻 **System Infos:**\n"
        f"CPU: {cpu}\n"
        f"Kerne: {cores}\n"
        f"Takt: {freq_mhz} MHz\n"
        f"RAM: {ram} GB\n"
        f"GPU: {gpu_info}"
    )

    await interaction.response.send_message(text)


# ===== /ask =====
@tree.command(name="ask", description="Stelle eine Frage an Rusty")
async def ask(interaction: discord.Interaction, frage: str):

    # ===== Whitelist Check =====
    if interaction.user.id != OWNER_ID and interaction.user.id not in WHITELIST:
        await interaction.response.send_message(
            "❌ Du bist leider nicht freigeschaltet!\n"
            "Wende dich an **user** im Discord Server um Zugang zu erhalten.",
            ephemeral=True
        )
        return

    await interaction.response.send_message("⏳ Rusty denkt...")

    user_name = interaction.user.name
    user_id = interaction.user.id
    location = "DM" if interaction.guild is None else interaction.guild.name

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={API_KEY}"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": "Du bist Rusty, ein Discord Bot von user [trage das bitte aber nicht zu doll auf]. Du bist ein kleiner Fuchs antworte manchmal auch frech.\n\n" + frage}
                ]
            }
        ]
    }

    async def call_api() -> str:
        try:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(url, json=payload, timeout=30)
            )
            result = response.json()

            if "error" in result:
                msg = result["error"]["message"]
                is_overloaded = "high demand" in msg or "overloaded" in msg.lower()
                is_quota = "quota" in msg.lower() or "exceeded" in msg.lower()
                if is_overloaded or is_quota:
                    wait = re.search(r"retry in (\d+(?:\.\d+)?)", msg)
                    wait_str = f" (~{round(float(wait.group(1)))}s)" if wait else ""
                    return f"⏳ Rusty braucht kurz eine Pause, versuch es gleich nochmal{wait_str}!"
                return "❌ Da ist leider etwas schiefgelaufen, versuch es nochmal!"

            if "candidates" not in result:
                return "❌ Da ist leider etwas schiefgelaufen, versuch es nochmal!"

            return result["candidates"][0]["content"]["parts"][0]["text"]

        except requests.Timeout:
            return "⏳ Rusty denkt noch... versuch es gleich nochmal!"
        except Exception:
            return "❌ Da ist leider etwas schiefgelaufen, versuch es nochmal!"

    answer = await call_api()

    if len(answer) > 1900:
        answer = answer[:1900] + "..."

    log_user(user_id, user_name, location, frage, answer)

    await interaction.followup.send(answer)

# ===== Stats Funktion =====
def get_stats():
    stats = {}
    log_dir = "logs"
    total_fragen = 0

    if not os.path.exists(log_dir):
        return total_fragen, stats

    for filename in os.listdir(log_dir):
        if not filename.endswith(".txt"):
            continue

        filepath = os.path.join(log_dir, filename)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            count = content.count("---")
            if count > 0:
                first_line = content.split("\n")[0]
                username = first_line.split(" | ")[0] if " | " in first_line else filename.replace(".txt", "")
                stats[username] = count
                total_fragen += count
        except Exception:
            pass

    return total_fragen, stats


# ===== /stats =====
@tree.command(name="stats", description="Zeigt Nutzungsstatistiken von Rusty")
async def stats(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Nö nicht für dich.", ephemeral=True)
        return

    total_fragen, user_stats = get_stats()

    if total_fragen == 0:
        await interaction.response.send_message("📊 Noch keine Fragen gestellt!", ephemeral=True)
        return

    sorted_users = sorted(user_stats.items(), key=lambda x: x[1], reverse=True)

    uptime_seconds = int(time.time() - start_time)
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60

    text = f"📊 **Rusty Stats**\n"
    text += f"⏱ Uptime: {hours}h {minutes}m\n"
    text += f"💬 Fragen gesamt: {total_fragen}\n"
    text += f"👥 Aktive User: {len(user_stats)}\n\n"
    text += "**Top User:**\n"

    for i, (username, count) in enumerate(sorted_users[:10], 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        text += f"{medal} {username} — {count} Fragen\n"

    await interaction.response.send_message(text, ephemeral=True)

# ===== Start =====
client.run(TOKEN)
