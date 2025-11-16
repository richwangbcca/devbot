# Daily Challenge Discord Bot: Devbot

A personal productivity bot that sends daily coding challenges and helps manage project TODOs. Built to offset the cognitive load of planning daily coding!

## Features

### Daily Challenges
The bot randomly selects from 4 challenge types:
- **1 LeetCode Medium + Random TODO** - Solve a medium problem and work on an existing project
- **3 LeetCode Mediums** - For interview prep
- **2 LeetCode Hards** - Even more interview prep
- **1-Hour Development Sprint** - Build a mini-app from an AI-generated spec

### Project Management
- Add projects and track TODOs
- Mark items as complete
- Random TODO selection for daily challenges

## Setup

### Prerequisites
- Python 3.8+
- Discord Bot Token
- OpenAI API Key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/richwangbcca/devbot.git
cd devbot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file:
```env
DISCORD_TOKEN=your_discord_bot_token
OPENAI_API_KEY=your_openai_api_key
DISCORD_USER_ID=your_discord_user_id
```

4. Run the bot:
```bash
python bot.py
```

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `!add_project <name>` | Create a new project | `!add_project "portfolio site"`|
| `!add_todo <project> <todo>` | Add a TODO to a project | `!add_todo "portfolio site" "Fix mobile navigation"` |
| `!list_todos <project>` | View all TODOs for a project | `!list_todos portfolio site` |
| `!mark_done <project> <index>` | Mark a TODO as complete | `!mark_done "portfolio site" 1` |
| `!challenge` | Manually trigger a challenge DM | `!challenge` |
| `!projects` | List all projects an their TODOs | `!projects` |

## Getting Your Discord Credentials

### Discord Bot Token:
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and create a bot
4. Copy the token

### Your Discord User ID:
1. Enable Developer Mode in Discord (Settings → Advanced → Developer Mode)
2. Right-click your username and select "Copy User ID"

### Bot Permissions:
The bot needs:
- Send Messages
- Send Messages in Threads
- Send Direct Messages

## How It Works

The bot stores project data in `projects.json` and uses OpenAI's API to generate creative app ideas for sprint challenges. Daily challenges are sent via DM to keep your practice consistent and private.

## Example Challenge Output

```
Today's challenge:
- Solve 1 LeetCode medium
- Work on portfolio-site → TODO: Fix mobile navigation
```

or

```
Today's challenge: 1-hour Development Sprint

Build a simple habit tracker app with the following features:
- Add/remove habits
- Mark daily completions
- View streak counters
- Clean, minimal UI
```

## Why I Built This

As someone who often gets lost in planning, I wanted a system that would:
- Pick my daily tasks for me so I wouldn't overthink it
- Give me variety in daily challenges
- Connect interview prep with real project work
- Keep me accountable through automated daily challenges.
