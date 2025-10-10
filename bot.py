import json, time, calendar
from datetime import datetime
import google.generativeai as genai
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TO_DO_LIST = "ToDoList.json"
HABIT_LIST = "HabitList.json"

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

def load_list(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_list(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

to_do_list = load_list(TO_DO_LIST)
habit_list = load_list(HABIT_LIST)
weeklist = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
today_deadline = ["example1", "example2", "example3", "example4"]

def to_do_list_making():
    current_date = datetime.now().strftime("%Y-%m-%d")
    result = f"[{current_date} To-Do List]\n"
    for i, item in enumerate(today_deadline):
        result += f"{i + 1}. {item}\n"
    return result

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Let me help you manage your time! ✨")
    time.sleep(1)
    await commands(update, context)

async def print_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    print(f"Chat ID: {chat_id}")
    await update.message.reply_text(f"ID: {chat_id}")

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"{Update} caused an error: {context.error}")

async def commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Here are my commands:\n")
    await update.message.reply_text(
        "/command - All commands\n"
        "/time - Current time\n"
        "/to_do - To-do list\n"
        "/habit - Habit tracker\n"
        "/finish - Finish to-do\n"
        "/add - Add to-do\n"
        "/delete - Delete to-do\n"
        "/edit - Edit to-do\n"
        "/begin - Start habit\n"
        "/end - End habit\n"
        "/remove - Remove habit"
    )

async def show_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")
    weekday = weeklist[datetime.now().weekday()]
    await update.message.reply_text(f"Today is {current_date} ({weekday})\nNow it’s {current_time}")

async def show_to_do(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(today_deadline) == 0:
        await update.message.reply_text("No tasks yet. Add some with /add")
    else:
        await update.message.reply_text(to_do_list_making())

async def show_habit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(habit_list) == 0:
        await update.message.reply_text("No habits yet. Start one with /begin")
    else:
        await update.message.reply_text(f"Habits:\n{habit_list}")

async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(to_do_list) == 0:
        await update.message.reply_text("All tasks are done!")
    else:
        to_do_list.pop(0)
        save_list(TO_DO_LIST, to_do_list)
        await update.message.reply_text("Task completed!")

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    to_do_list.append(text[5:])
    save_list(TO_DO_LIST, to_do_list)
    await update.message.reply_text(f"Added task: {text[5:]}")

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if len(to_do_list) == 0:
        await update.message.reply_text("No tasks to delete!")
    else:
        to_do_list.pop(int(text[8:]) - 1)
        save_list(TO_DO_LIST, to_do_list)
        await update.message.reply_text("Task deleted!")

async def edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    to_do_list[int(text[6]) - 1] = text[8:]
    save_list(TO_DO_LIST, to_do_list)
    await update.message.reply_text(f"Edited task: {text[8:]}")

async def begin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    habit_list.append(text[7:])
    save_list(HABIT_LIST, habit_list)
    await update.message.reply_text(f"Started habit: {text[7:]}")

async def end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if len(habit_list) == 0:
        await update.message.reply_text("No habits to end!")
    else:
        habit_list.pop(int(text[7:]) - 1)
        save_list(HABIT_LIST, habit_list)
        await update.message.reply_text(f"Ended habit!")

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    habit_list.pop(int(text[8:]) - 1)
    save_list(HABIT_LIST, habit_list)
    await update.message.reply_text(f"Removed habit!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text.lower() == "command":
        await commands(update, context)
    elif text.lower() == "time":
        await show_time(update, context)
    elif text.lower() == "to-do":
        await show_to_do(update, context)
    elif text.lower() == "habit":
        await show_habit(update, context)
    elif text.startswith("finish"):
        await finish(update, context)
    elif text.startswith("add"):
        await add(update, context)
    elif text.startswith("delete"):
        await delete(update, context)
    elif text.startswith("edit"):
        await edit(update, context)
    elif text.startswith("begin"):
        await begin(update, context)
    elif text.startswith("end"):
        await end(update, context)
    elif text.startswith("remove"):
        await remove(update, context)
    else:
        response = model.generate_content(text)
        if hasattr(response, "text"):
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("I didn’t understand that.")

async def repeat(context: ContextTypes.DEFAULT_TYPE):
    H = int(datetime.now().strftime("%H"))
    M = int(datetime.now().strftime("%M"))
    if H == 7 and M == 30:
        await context.bot.send_message(CHAT_ID, "Good morning! Time to wake up!")
        if len(to_do_list) != 0:
            await context.bot.send_message(CHAT_ID, to_do_list_making())
        else:
            await context.bot.send_message(CHAT_ID, "You have no tasks. Add some with /add")

print("Bot is running...")
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("command", commands))
app.add_handler(CommandHandler("time", show_time))
app.add_handler(CommandHandler("to_do", show_to_do))
app.add_handler(CommandHandler("habit", show_habit))
app.add_handler(CommandHandler("finish", finish))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("delete", delete))
app.add_handler(CommandHandler("edit", edit))
app.add_handler(CommandHandler("begin", begin))
app.add_handler(CommandHandler("end", end))
app.add_handler(CommandHandler("remove", remove))
app.add_handler(MessageHandler(filters.TEXT, handle_message))
app.job_queue.run_repeating(repeat, interval=60, first=1)
app.add_error_handler(error)
app.run_polling()
