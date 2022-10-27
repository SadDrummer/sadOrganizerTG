from datetime import datetime as dt
from datetime import time
from telegram.ext import (Updater, CommandHandler, CallbackContext, Filters, MessageHandler)
from telegram import (Update, KeyboardButton, ReplyKeyboardMarkup)
import pytz
import json


TOKEN = open("token.txt").read()
button_run = "Запустить отслеживание"
reply_markup = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=button_run)]],
        resize_keyboard=True
    )


def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет", reply_markup=reply_markup)


def help(update: Update, context: CallbackContext):
    update.message.reply_text("Справка", reply_markup=reply_markup)


def run_button(update: Update, context: CallbackContext):
    text = update.message.text
    if text == button_run:
        run_checking(update, context)
    return


def telegram_daily_job(context: CallbackContext):
    job = context.job
    context.bot.send_message(job.context, text=today_tasks())


def run_checking(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    beep_time = time(hour=10).replace(tzinfo=pytz.timezone("Europe/Moscow"))
    beep_time = time(hour=16, minute=41).replace(tzinfo=pytz.timezone("Europe/Moscow"))
    context.job_queue.run_daily(telegram_daily_job, time=beep_time, context=chat_id, name=str(chat_id))
    update.message.reply_text("Отслеживание запущено", reply_markup=reply_markup)


def is_task_today(task_date_field):
    today = dt.now()
    weekdays = ["mo", "tu", "we", "th", "fr", "sa", "su"]
    task_dates = task_date_field.split(',')
    if (weekdays[dt.weekday(today)] in task_dates):
        return True
    if (str(today.day) in task_dates):
        return True
    if ((str(today.day) + "." + str(today.month)) in task_dates):
        return True
    if ((str(today.day) + "." + str(today.month) + '.' + str(today.year)) in task_dates):
        return True
    return False


def today_tasks():
    tasks = json.load(open("tasks.json", encoding="utf-8"))["tasks"]
    message = "Сегодня:\n\n"
    for task in tasks:
        if (is_task_today(task["date"])):
            message += task["name"] + "\nОписание:\n" + task["description"] + "\n\n"
    return message[:-2]


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('run_cheking', run_checking))
    dp.add_handler(MessageHandler(Filters.text,  run_button))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()