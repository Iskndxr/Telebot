from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

updater = Updater(token=config["TELEGRAM"]["TOKEN"], use_context=True)
dispatcher = updater.dispatcher

def start(update, context):
    keyboard = [[KeyboardButton("Formal Confession"), KeyboardButton("Informal Confession")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to Confession Bot! Please choose the type of confession:", reply_markup=reply_markup)

def confession_type(update, context):
    query = update.callback_query
    confession_type = query.data

    if confession_type == 'formal':
        context.bot.send_message(chat_id=update.effective_chat.id, text="You chose to make a formal confession. Please enter the recipient of the confession:")
        # Update conversation state to capture recipient
        context.user_data['confession_type'] = confession_type
        context.user_data['next_step'] = 'recipient'
    elif confession_type == 'informal':
        context.bot.send_message(chat_id=update.effective_chat.id, text="You chose to make an informal confession. Please send your informal confession.")
        # Update conversation state to capture confession directly
        context.user_data['confession_type'] = confession_type
        context.user_data['next_step'] = 'confession'

def handle_input(update, context):
    if 'confession_type' in context.user_data and 'next_step' in context.user_data:
        confession_type = context.user_data['confession_type']
        next_step = context.user_data['next_step']

        if next_step == 'recipient':
            recipient = update.message.text
            context.user_data['recipient'] = recipient
            context.bot.send_message(chat_id=update.effective_chat.id, text="Please send your formal confession.")
            context.user_data['next_step'] = 'confession'
        elif next_step == 'confession':
            confession_text = update.message.text
            recipient = context.user_data['recipient']
            context.bot.send_message(chat_id=update.effective_chat.id, text="Your formal confession has been received anonymously.")
            context.bot.send_message(chat_id='@your_channel_username', text=f"New Formal Confession:\nRecipient: {recipient}\nConfession:\n{confession_text}")
            # Reset conversation state
            del context.user_data['confession_type']
            del context.user_data['next_step']
            del context.user_data['recipient']
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please start the bot and choose the confession type.")

start_handler = CommandHandler('start', start)
formal_handler = CallbackQueryHandler(confession_type, pattern='formal')
informal_handler = CallbackQueryHandler(confession_type, pattern='informal')
input_handler = MessageHandler(Filters.text & (~Filters.command), handle_input)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(formal_handler)
dispatcher.add_handler(informal_handler)
dispatcher.add_handler(input_handler)

updater.start_polling()
