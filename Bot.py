from datetime import datetime
import requests
import credentials
from bs4 import BeautifulSoup
from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram.ext import MessageHandler, Filters
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from Calendar import getCred, getEvents, addEvent
from Notion import getToDOTask

# Set token
token = credentials.telegram_token

# Set updater
updater = Updater(token=token, use_context=False)

# Set dispatcher
dispatcher = updater.dispatcher


def start(bot, update):
    """
    action when user type /start in chat
    """
    msg = update.message
    first_name = msg['chat']['first_name']
    update.message.reply_text(
        text=f'Hello {first_name}, what can I do for you?'
    )


def help(bot, update):
    """
    show list functionalities of telegram-bot
    """
    txt = 'commands: /start, /corona, /roger, /getcal, /addcal, /gnotion'
    update.message.reply_text(text=txt)


def default(bot, update):
    """
    If cannot match any functionality, return default message
    """
    txt = f"Cannot understand: {update.message.text}\n"
    txt = txt + "Please type /help for more information"
    update.message.reply_text(text=txt)


def coronaReg(bot, update):
    """
    Get latest regulations of corona in Bavaria
    """
    url = "https://www.br.de/nachrichten/deutschland-welt/coronavirus-in-bavaria-assistance-in-english,RtO8eS2"
    requestSession = requests.session()
    page = requestSession.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    sections = soup.find('section', {"id": "articlebody"})
    section = sections.find_all('section')[1]
    title = section.select('h2')[0].get_text()
    bot.sendMessage(chat_id=update.message.chat_id, text=title)
    for p in section.select('p'):
        txt = p.get_text()
        bot.sendMessage(chat_id=update.message.chat_id, text=txt)
        if len(txt) == 10:
            break


def rogerGame(bot, update):
    """
    Get roger federer latest game information
    """
    url = "https://www.perfect-tennis.com/roger-federers-schedule/"
    requestSession = requests.session()
    page = requestSession.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    spanIDs = ["Where_is_Roger_Federer_Playing_Now",
               "What_Tournament_is_Roger_Federer_Playing_Next", "Who_is_Roger_Federer_Playing_Next"]
    for spanID in spanIDs:
        span = soup.find('span', {"id": spanID})
        bot.sendMessage(chat_id=update.message.chat_id, text=span.get_text())
        content = span.parent.next_sibling.next_sibling.get_text()
        bot.sendMessage(chat_id=update.message.chat_id, text=content)


def getCalender(bot, update):
    """
    Get list of events from google calender
    """
    service = getCred()
    txt = update.message.text.replace("/getcal", "")
    if not txt:
        events = getEvents(service)
    else:
        day = txt.replace(" ", "")
        try:
            _ = datetime.strptime(day, "%Y-%m-%d")
        except ValueError:
            err_message = "Wrong date format, format should be /getcal yyyy-mm-dd"
            bot.sendMessage(chat_id=update.message.chat_id, text=err_message)
        else:
            events = getEvents(service, day)

    for event in events:
        txt = f'Event name: {event["summary"]}'  # time slot
        bot.sendMessage(chat_id=update.message.chat_id, text=txt)

    if not events:
        txt = "Empty calendar!"
        bot.sendMessage(chat_id=update.message.chat_id, text=txt)


def addCalender(bot, update):
    """
    add event to google calender
    """
    service = getCred()
    txt = update.message.text.replace("/addcal", "")
    if not txt:
        txt_message = "Empty string, string should be /addcal eventname,yyyy-mm-dd,hh:mm,hh:mm"
        bot.sendMessage(chat_id=update.message.chat_id, text=txt_message)
    else:
        try:
            txt = txt.replace(" ", "")
            eventName, day, start, end = txt.split(",")
            _ = datetime.strptime(day, "%Y-%m-%d")
            _ = datetime.strptime(start, "%H:%M")
            _ = datetime.strptime(end, "%H:%M")
        except ValueError as err:
            err_message = "Wrong format, string should be /addcal eventname,yyyy-mm-dd,hh:mm,hh:mm"
            bot.sendMessage(chat_id=update.message.chat_id, text=err)
            bot.sendMessage(chat_id=update.message.chat_id, text=err_message)
        else:
            respond_msg = addEvent(service, day, start, end, eventName)
            bot.sendMessage(chat_id=update.message.chat_id, text=respond_msg)


def getNotionTasks(bot, update):
    """
    Get tasks from task list page from Notion
    """
    txt = update.message.text.replace("/gnotion", "")
    if not txt:
        boardName = "To DO - today"
        tasks = getToDOTask(boardName)
    else:
        try:
            txt = txt.replace(" ", "")
            boardName = txt.split(",")
        except ValueError as err:
            bot.sendMessage(chat_id=update.message.chat_id, text=err)
        else:
            tasks = getToDOTask(boardName)
    
    bot.sendMessage(chat_id=update.message.chat_id, text=boardName)
    for taskTitle in tasks:
        bot.sendMessage(chat_id=update.message.chat_id, text=taskTitle)


# TODO
# def Notion():
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('corona', coronaReg))
dispatcher.add_handler(CommandHandler('roger', rogerGame))
dispatcher.add_handler(CommandHandler('getcal', getCalender))
dispatcher.add_handler(CommandHandler('addcal', addCalender))
dispatcher.add_handler(CommandHandler('gnotion', getNotionTasks))
dispatcher.add_handler(MessageHandler(Filters.text, default))

# bot initiate
updater.start_polling()

# updater.stop()
