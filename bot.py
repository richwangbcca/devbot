import json
import os
import random
import discord

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext import commands
from dotenv import load_dotenv
import openai
import pytz

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USER_ID = int(os.getenv("DISCORD_USER_ID"))
DATA_FILE = "projects.json"

LOCAL_TIMEZONE = os.getenv("LOCAL_TIMEZONE", "America/Los_Angeles")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())
scheduler = AsyncIOScheduler(timezone=pytz.timezone(LOCAL_TIMEZONE))

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"projects": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

client = openai.OpenAI(api_key=OPENAI_API_KEY)

async def generate_sprint_spec():
    domains = [
        "frontend web app ",
        "full-stack web app ",
        "CLI tool ",
        "machine learning prototype ",
        "systems-level program ",
        "automation script ",
        " "
    ]
    domain = random.choice(domains)
    resp = client.responses.create(
        model = "gpt-4o-mini",
        instructions = "You are an assistant generating mini-app ideas for a startup trainee.",
        input=f"Give me a single small {domain}project idea that can be implemented in one hour by one developer without LLM assistance. Provide clear features and deliverables. Do not provide" \
        "any other text."
    )

    return resp.output_text

async def pick_challenge():
    weights = [0.4, 0.3, 0.2, 0.1]  # Medium+TODO, 3 Mediums, 2 Hards, Sprint
    choice = random.choices(
        ["medium_plus_todo", "three_mediums", "two_hards", "sprint"],
        weights=weights
    )[0]

    user = await bot.fetch_user(USER_ID)
    if not user:
        print("Could not fetch user for DM.")
        return

    data = load_data()
    todos = [(p, t) for p, d in data["projects"].items() for t in d["todos"]]

    if choice == "medium_plus_todo":
        medium_msg = "Solve **1 LeetCode medium**."
        if todos:
            project, todo = random.choice(todos)
            todo_msg = f"Work on **{project}** → TODO: {todo}"
        else:
            todo_msg = "No TODOs found! Do two more mediums or a hard instead."
        msg = f"Today's challenge:\n- {medium_msg}\n- {todo_msg}"

    elif choice == "three_mediums":
        msg = "Today's challenge: Solve **3 LeetCode mediums**."

    elif choice == "two_hards":
        msg = "Today's challenge: Solve **2 LeetCode hards**."

    elif choice == "sprint":
        spec = await generate_sprint_spec()
        msg = f"Today's challenge: **1-hour Startup Speed Sprint**\n\n{spec}"

    else:
        msg = "Error picking challenge."

    await user.send(f"Good morning <@{USER_ID}>! {msg}")

# Bot commands
@bot.command(name='add_project')
async def add_project(ctx, name: str):
    data = load_data()
    if name in data["projects"]:
        await ctx.send(f"Project '{name}' already exists.")
        return
    data["projects"][name] = {"todos": []}
    save_data(data)
    await ctx.send(f"Project '{name}' added.")

@bot.command(name="add_todo")
async def add_todo(ctx, project: str, *, todo: str):
    data = load_data()
    if project not in data["projects"]:
        await ctx.send(f"Project '{project}' not found.")
        return
    data["projects"][project]["todos"].append(todo)
    save_data(data)
    await ctx.send(f"Added TODO to {project}: {todo}")

@bot.command(name="list_todos")
async def list_todos(ctx, project: str):
    data = load_data()
    if project not in data["projects"]:
        await ctx.send(f"Project '{project}' not found.")
        return
    todos = data["projects"][project]["todos"]
    if not todos:
        await ctx.send(f"No TODOs for project '{project}'.")
    else:
        formatted = "\n".join(f"{i+1}. {t}" for i, t in enumerate(todos))
        await ctx.send(f"TODOs for '{project}':\n{formatted}")

@bot.command(name="mark_done")
async def mark_done(ctx, project: str, index: int):
    data = load_data()
    if project not in data["projects"]:
        await ctx.send(f"Project '{project}' not found.")
        return
    todos = data["projects"][project]["todos"]
    if index < 1 or index > len(todos):
        await ctx.send(f"Invalid TODO index. Use !list_todos to check.")
        return
    removed = todos.pop(index - 1)
    save_data(data)
    await ctx.send(f"Marked as done: {removed}")

@bot.command(name="challenge")
async def challenge(ctx):
    """Manually trigger a challenge DM."""
    await pick_challenge()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    scheduler.add_job(
        pick_challenge,
        trigger=CronTrigger(hour=9, minute=0, timezone=LOCAL_TIMEZONE),
        name="Daily Challenge"
    )
    scheduler.start()
    print(f"Scheduler started, daily challenge set for 9:00 {LOCAL_TIMEZONE}")

bot.run(TOKEN)
