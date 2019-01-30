import logging
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater, CallbackQueryHandler
from telegram import ChatAction, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
import img2pdf
import os

DEBUG = False

TOKEN = "You can locate you token here"
PATH = "/home/user/bot/"
CHAR = '/'
FILE_NAME = "out.pdf"
NUM_FILE_NAME = "stats"
MY_ID = 16399547
MAX = 10000000

WELCOME_MESSAGE = "Download a .jpg to add a file to a queue\n" \
                  "The bot converts jpg(png)->pdf\n" \
                  "Using:\n" \
                  "1) Download files .jpg or .png \n" \
                  "2) Press \"convert\" command(or write it on your own) \n" \
                  "3) Get your pdf \n" \
                  "For any questions(ads, etc.), @kokhnovich \n"


# Delete all files from user-s dir
def clear(bot, update):
    if DEBUG:
        send(bot, update, "clear::start")
    os.chdir(getPath(update))
    data = [i for i in os.listdir(os.getcwd()) if i.endswith(".jpg")]
    for file in data:
        os.remove(file)
    if DEBUG:
        send(bot, update, "clear::end")


def getPath(update):
    return PATH + str(update.message.chat_id) + CHAR


# send text_ message
def send(bot, update, text_):
    bot.send_message(chat_id=update.message.chat_id, text=text_)


def info(bot, update, to_send=True):
    number = -1
    with open(getPath(update) + NUM_FILE_NAME, 'r') as file:
        number = int(file.readline())
    if to_send:
        send(bot, update, "You have downloaded " + str(number - MAX) + " pictures")
    return number


# using img2pdf
# all .jpg to pdf
# .jpg is just a sign, a lib work with each picture format
def convert(bot, update):
    if DEBUG:
        send(bot, update, "convert::start")
    os.chdir(getPath(update))
    with open(getPath(update) + FILE_NAME, "wb") as f:
        f.write(img2pdf.convert([i for i in sorted(os.listdir(os.getcwd())) if i.endswith(".jpg")]))
    bot.send_document(chat_id=update.message.chat_id, document=open(getPath(update) + FILE_NAME, 'rb'))
    clear(bot, update)
    if DEBUG:
        send(bot, update, "convert::end")


def help(bot, update):
    send(bot, update, WELCOME_MESSAGE)


# def callback_handler(bot, update):
#     query = update.callback_query

#     if query.data == 'help':
#         help(bot, query)
#     elif query.data == 'info':
#         info(bot, query)
#     elif query.data == 'convert':
#         convert(bot, query)
#     else:
#         send(bot, query, query.data)

#     start(bot, query)


# def is_work(bot, update):
#     bot.send_message(chat_id=update.message.chat_id, text="It works fine:)")

def start(bot, update):
    # create user's dir using dialog_id
    if not os.path.exists(getPath(update)):
        # send(bot, update, "can't find file. Create one just for you!")
        os.makedirs(getPath(update))
        with open(getPath(update) + NUM_FILE_NAME, 'w+') as file:
            file.write(str(MAX))  # never do like this - works for <10000000 pictures
    else:
        # send(bot, update, "file already exist, ok!")
        pass

    # custom_keyboard = [['Convert', 'Show info', 'help']]
    keyboard = [[InlineKeyboardButton("convert", callback_data='convert'),
                 InlineKeyboardButton("info", callback_data='info'),
                 InlineKeyboardButton("help", callback_data='help'),
                 InlineKeyboardButton("clear", callback_data='clear')]]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    bot.send_message(chat_id=update.message.chat_id,
                     text="What to do?",
                     reply_markup=reply_markup)


def text(bot, update):
    if update.message.text == 'convert':
        convert(bot, update)
    elif update.message.text == 'info':
        info(bot, update)
    elif update.message.text == 'help':
        help(bot, update)
    elif update.message.text == 'clear':
        clear(bot, update)
    else:
        send(bot, update, "Ya do not ponimatb you")


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def get_and_inc(bot, update):
    number = info(bot, update, False)
    with open(getPath(update) + NUM_FILE_NAME, 'w') as file:
        file.write(str(number + 1))
    return number


def get_image(bot, update):
    cur = get_and_inc(bot, update)

    file_id = update.message.photo[-1].file_id
    new_file = bot.get_file(file_id)
    new_file.download(getPath(update) + str(cur + 1) + ".jpg")


updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger()

logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)

# dispatcher.add_handler(CommandHandler('ok', is_work))
# dispatcher.add_handler(CommandHandler('help', start))
# updater.dispatcher.add_handler(CallbackQueryHandler(callback_handler))
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(Filters.text, text))
updater.dispatcher.add_error_handler(error)
dispatcher.add_handler(MessageHandler(Filters.photo, get_image))

updater.start_polling()

x = "The easiest way to work with this in PyCharm:)"
while x != "close":
    x = input()
updater.stop()
