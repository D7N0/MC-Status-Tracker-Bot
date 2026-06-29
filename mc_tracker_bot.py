import discord
import re
import os
from discord.ext import commands

# ── CONFIG ────────────────────────────────────────────────────────────────────
FEED_CHANNEL_ID  = 1231231231231231234
VOICE_CHANNEL_ID = 1231231231231231234
MC_STATUS_BOT_ID = 1231231231231231234
# ─────────────────────────────────────────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

online_players: set[str] = set()
last_count = -1
server_is_online = False

JOIN_RE  = re.compile(r"^(.+) joined the game\.$", re.MULTILINE)
LEAVE_RE = re.compile(r"^(.+) left the game\.$",   re.MULTILINE)


async def update_nickname():
    global last_count
    count = len(online_players)
    if count == last_count:
        return
    last_count = count
    vc = bot.get_channel(VOICE_CHANNEL_ID)
    if vc is None:
        return
    nick = f"🟢 Online: {count}" if count > 0 else "🔴 Online: 0"
    await vc.guild.me.edit(nick=nick)


async def join_vc():
    vc = bot.get_channel(VOICE_CHANNEL_ID)
    if vc and isinstance(vc, discord.VoiceChannel):
        if not vc.guild.voice_client:
            await vc.connect()


async def leave_vc():
    vc = bot.get_channel(VOICE_CHANNEL_ID)
    if vc and vc.guild.voice_client:
        await vc.guild.voice_client.disconnect()


async def rebuild_state():
    """Scan message history to rebuild server/player state on startup."""
    global server_is_online

    channel = bot.get_channel(FEED_CHANNEL_ID)
    if channel is None:
        return

    print("Scanning message history to rebuild state...")

    # collect recent messages from MC Status bot (newest first)
    messages = []
    async for msg in channel.history(limit=200):
        if msg.author.id == MC_STATUS_BOT_ID:
            messages.append(msg)

    # find index of most recent server online/offline message
    server_msg_index = None
    for i, msg in enumerate(messages):
        if "Server online!" in msg.content:
            server_is_online = True
            server_msg_index = i
            print("History: server was online — rebuilding player state")
            break
        elif "Server offline!" in msg.content:
            server_is_online = False
            server_msg_index = i
            print("History: server was offline — staying out of VC")
            break

    # if server was online, replay all messages between now and that point
    # to figure out who's currently in game
    if server_is_online and server_msg_index is not None:
        # messages[0] is newest, messages[server_msg_index] is the online msg
        # replay oldest to newest (reverse) so joins/leaves apply correctly
        relevant = messages[:server_msg_index]  # everything after server came online
        for msg in reversed(relevant):
            for player in JOIN_RE.findall(msg.content):
                online_players.add(player.strip())
            for player in LEAVE_RE.findall(msg.content):
                online_players.discard(player.strip())

    print(f"Rebuilt state — server online: {server_is_online}, players online: {online_players}")

    if server_is_online:
        await join_vc()

    await update_nickname()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} — rebuilding state from history")
    await rebuild_state()


@bot.event
async def on_voice_state_update(member, before, after):
    if member.id != bot.user.id:
        return
    if before.channel and after.channel is None and server_is_online:
        print("Bot was disconnected from VC — rejoining...")
        await join_vc()


@bot.event
async def on_message(message: discord.Message):
    global server_is_online

    if message.channel.id != FEED_CHANNEL_ID:
        return
    if message.author.id != MC_STATUS_BOT_ID:
        return

    content = message.content
    changed = False

    if "Server online!" in content:
        server_is_online = True
        await join_vc()
    elif "Server offline!" in content:
        server_is_online = False
        online_players.clear()
        await update_nickname()
        await leave_vc()

    for player in JOIN_RE.findall(content):
        online_players.add(player.strip())
        changed = True

    for player in LEAVE_RE.findall(content):
        online_players.discard(player.strip())
        changed = True

    if changed:
        await update_nickname()

    await bot.process_commands(message)


@bot.command(name="online")
async def who_online(ctx):
    if not online_players:
        await ctx.send("🔴 No players online right now.")
    else:
        player_list = "\n".join(f"• {p}" for p in sorted(online_players))
        await ctx.send(f"🟢 **Online ({len(online_players)}):**\n{player_list}")


bot.run("PASTE_TOKEN_HERE")