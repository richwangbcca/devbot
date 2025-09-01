import json
import os
import random
import shlex

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import discord
from discord.ext import commands
from dotenv import load_dotenv
import openai
import pytz

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USER_ID = int(os.getenv("DISCORD_USER_ID"))
DATA_FILE = "projects.json"
COLOR = 0x0d9aff

LOCAL_TIMEZONE = os.getenv("LOCAL_TIMEZONE", "America/Los_Angeles")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default(), help_command=None)
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
        msg = f"{medium_msg}\n- {todo_msg}"

    elif choice == "three_mediums":
        msg = "Solve **3 LeetCode mediums**."

    elif choice == "two_hards":
        msg = "Solve **2 LeetCode hards**."

    elif choice == "sprint":
        spec = await generate_sprint_spec()
        msg = f"**1-hour Development Sprint**\n\n{spec}"

    else:
        msg = "Error picking challenge. Looks like you're off the hook today."

    await user.send(content=f"Good morning <@{USER_ID}>!",
                    embed=discord.Embed(
                        title="Today's Challenge:",
                        description=msg,
                        color=COLOR
                    )
    )

# Bot commands
@bot.command(name='projects')
async def show_projects(ctx):
    data = load_data()
    projects = sorted(data['projects'])
    
    embed = discord.Embed(
        title="Your Projects",
        color=COLOR
    )

    for project in projects:
        todos = data["projects"][project]["todos"]
        if todos:
            todo_list = "\n".join(f"{i+1}. {t}" for i, t in enumerate(todos))
        else:
            todo_list = "No TODOs for this project!"
        embed.add_field(name=project, value=todo_list, inline=False)

    await ctx.send(embed=embed)

@bot.command(name='add_project')
async def add_project(ctx, name: str):
    """
    Add a project to the bot.
    !add_project "<project name>"
    """
    data = load_data()
    if name in data["projects"]:
        await ctx.send(embed=discord.Embed(
            description=f"Project '{name}' already exists!",
            color=COLOR)
        )
        return
    
    data["projects"][name] = {"todos": []}
    save_data(data)

    await ctx.send(embed=discord.Embed(
        description=f"Project '{name}' added!",
        color=COLOR)
    )

@bot.command(name="add_todo")
async def add_todo(ctx, *, args: str):
    """
    Add a todo to the project
    !add_todo "<project name>" "<todo>"
    """
    try:
        parts = shlex.split(args)
        if len(parts) != 2:
            raise ValueError("Invalid number of arguments")
        project, todo = parts
    except Exception:
        await ctx.send(embed=discord.Embed(
            description="Usage: `!add_todo \"project name\" \"todo\"`",
            color=COLOR
        ))
        return
    
    data = load_data()
    if project not in data["projects"]:
        await ctx.send(embed=discord.Embed(
            description=f"Project '{project}' not found.",
            color=COLOR)
        )
        return
    
    data["projects"][project]["todos"].append(todo)
    save_data(data)
    await ctx.send(embed=discord.Embed(
        title=f"Added TODO to {project}:",
        description=todo,
        color=COLOR)
    )

@bot.command(name="list_todos")
async def list_todos(ctx, project: str):
    """
    List the todos for a given project
    !list_todos <project name>
    """
    data = load_data()
    if project not in data["projects"]:
        await ctx.send(embed=discord.Embed(
            description=f"Project '{project}' not found.",
            color=COLOR)
        )
        return
    
    todos = data["projects"][project]["todos"]
    if not todos:
        await ctx.send(embed=discord.Embed(
            description=f"No TODOs for project '{project}'.",
            color=COLOR)
        )
    else:
        formatted = "\n".join(f"{i+1}. {t}" for i, t in enumerate(todos))
        await ctx.send(embed=discord.Embed(
            title=f"TODOs for '{project}':",
            description=formatted,
            color=COLOR)
        )

@bot.command(name="mark_done")
async def mark_done(ctx, *, args: str):
    """
    Mark a TODO as done. Use !list_todos to check TODO indices.
    !mark_done "<project name>" <index>
    """
    try:
        parts = shlex.split(args)
        if len(parts) != 2:
            raise ValueError("Invalid number of arguments")
        project, index = parts
        index = int(index)
    except Exception:
        await ctx.send(embed=discord.Embed(
            description="Usage: `!add_todo \"project name\" index`",
            color=COLOR
        ))
        return
    
    data = load_data()
    if project not in data["projects"]:
        await ctx.send(embed=discord.Embed(
            description=f"Project '{project}' not found.",
            color=COLOR)
        )
        return
    
    todos = data["projects"][project]["todos"]
    if index < 1 or index > len(todos):
        await ctx.send(embed=discord.Embed(
            description=f"Invalid TODO index. Use !list_todos to check.",
            color=COLOR)
        )
        return
    
    removed = todos.pop(index - 1)
    save_data(data)

    await ctx.send(embed=discord.Embed(
        title=f"Marked as done for {project}:",
        description=removed,
        color=COLOR)
    )

@bot.command(name="challenge")
async def challenge(ctx):
    """
    Manually trigger a challenge DM.
    !challenge
    """
    await pick_challenge()

@bot.command(name="help", hidden=True)
async def help(ctx):
    embed = discord.Embed(
        title="Commands",
        description="Here are the available commands:",
        color=COLOR
    )
    for command in sorted(bot.commands, key=lambda c: c.name):
        if command.hidden: continue
        embed.add_field(
            name=f"!{command.name}",
            value=command.help or "No description",
            inline=False
        )
    
    await ctx.send(embed=embed)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=discord.Embed(
            description="Invalid command. Use `!help` to see how to use commands.",
            color=COLOR
        ))

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
