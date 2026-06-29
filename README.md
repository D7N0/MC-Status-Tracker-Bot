# MC Status Tracker Bot

A lightweight Discord bot that silently monitors a [DiscordSRV](https://www.spigotmc.org/resources/discordsrv.18494/) server feed channel and tracks live Minecraft player activity.

Built for **PackMC**, a community server progressing through every major Minecraft version from Alpha to Beta to Release.

---

## What it does

- Watches the DiscordSRV feed channel for join/leave events
- Joins a voice channel when the MC server comes online
- Leaves the voice channel when the MC server goes offline
- Updates the bot's nickname in the server to show the current player count in real time (e.g. `🟢 Online: 3` or `🔴 Online: 0`)
- Automatically rejoins the voice channel if disconnected while the server is online
- On restart, scans message history to rebuild state, rejoin the VC, and restore the player count without missing a beat
- Never sends any messages to chat

---

## Setup

### 1. Discord Developer Portal
- Create a new application at [discord.com/developers/applications](https://discord.com/developers/applications)
- Go to **Bot** and enable **Message Content Intent** and **Server Members Intent**
- Copy your bot token

### 2. Invite the bot
- Go to **OAuth2 > URL Generator**
- Scopes: `bot`
- Permissions: `Administrator` (or at minimum: `Manage Nicknames`, `Read Message History`, `View Channels`, `Connect`)
- Open the generated URL and invite to your server

### 3. Configure the bot
Fill in the three IDs at the top of `mc_tracker_bot.py`:

```python
FEED_CHANNEL_ID  = ...  # channel where DiscordSRV posts join/leave events
VOICE_CHANNEL_ID = ...  # voice channel the bot sits in
MC_STATUS_BOT_ID = ...  # user ID of your DiscordSRV bot
```

To get an ID: enable Developer Mode in Discord settings, then right-click any channel or user and select Copy ID.

### 4. Set up the voice channel
- Create a voice channel (e.g. `📡 Server Status`)
- Set `@everyone` Connect permission to ❌ so only the bot sits in it

### 5. Deploy
Paste your bot token into the last line of `mc_tracker_bot.py`:

```python
bot.run("YOUR_TOKEN_HERE")
```

Install dependencies:
```
discord.py[voice]
PyNaCl
```

---

## Files

| File | Description |
|------|-------------|
| `mc_tracker_bot.py` | Main bot logic |
| `requirements.txt` | Python dependencies |

---

## Commands

| Command | Description |
|---------|-------------|
| `!online` | Lists all players currently in-game |
