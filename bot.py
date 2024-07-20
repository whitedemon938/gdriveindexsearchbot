import os
import requests
import telebot
from dotenv import load_dotenv
from telegraph import Telegraph
import logging
import threading

# Load the bot token, API URL, public mode, owner ID, and message deletion time from the config.env file
load_dotenv('config.env')
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
API_URL = os.getenv('API_URL', 'https://apix.starktonyrestinpeace.tech/')
PUBLIC_MODE = os.getenv('PUBLIC_MODE', 'false').lower() == 'true'
OWNER_ID = os.getenv('OWNER_ID')
AUTHORIZED_CHATS = os.getenv('AUTHORIZED_CHATS', '').split(',')
MESSAGE_DELETION_TIME = int(os.getenv('MESSAGE_DELETION_TIME', '10'))  # Default to 10 seconds

if not TOKEN:
    raise ValueError("No TELEGRAM_BOT_TOKEN provided")
if not API_URL:
    raise ValueError("No API_URL provided")
if not OWNER_ID:
    raise ValueError("No OWNER_ID provided")

# Initialize the bot and Telegraph
bot = telebot.TeleBot(TOKEN)
telegraph = Telegraph()
telegraph.create_account(short_name='BotSharer', author_name='YourBotName', author_url='https://t.me/your_bot_username')

# Set up logging
logging.basicConfig(level=logging.INFO)

def is_authorized(chat_id):
    """Check if the chat is authorized."""
    return str(chat_id) in AUTHORIZED_CHATS or str(chat_id) == OWNER_ID

def should_respond(chat_id):
    """Determine if the bot should respond based on the mode."""
    if PUBLIC_MODE:
        return True
    return is_authorized(chat_id)

@bot.message_handler(commands=['start'])
def start(message):
    if should_respond(message.chat.id):
        bot.reply_to(message, 'Hi! Send me a movies / series name and I will find results for you.')
    else:
        bot.reply_to(message, 'You are not authorized to use this bot.')

@bot.message_handler(func=lambda message: True)
def search(message):
    if should_respond(message.chat.id):
        search_term = message.text
        try:
            # Send an instant response indicating the search is in progress
            searching_message = bot.reply_to(message, f'Searching for "{search_term}"...')
            
            response = requests.get(f'{API_URL}?search={requests.utils.quote(search_term)}')
            response.raise_for_status()
            results = response.json()

            if not results:
                bot.edit_message_text('No results found.', chat_id=searching_message.chat.id, message_id=searching_message.message_id)
            else:
                # Build the content for the Telegraph page
                content = []
                for result in results:
                    content.append({
                        'tag': 'h2',
                        'children': [f"Title: {result['title']}"]}
                    )
                    content.append({
                        'tag': 'p',
                        'children': [f"Size: {result['size']}"]}
                    )
                    content.append({
                        'tag': 'a',
                        'attrs': {'href': result['link']},
                        'children': ['Link']
                    })
                    content.append({
                        'tag': 'hr'
                    })

                # Create a new Telegraph page
                response = telegraph.create_page(
                    title='Search Results',
                    content=content
                )
                page_url = f"https://telegra.ph/{response['path']}"

                # Edit the searching message with the results URL
                bot.edit_message_text(f'Here are the results: {page_url}', chat_id=searching_message.chat.id, message_id=searching_message.message_id)

                # Schedule the deletion of both the user's message and the bot's message after the specified time
                threading.Timer(MESSAGE_DELETION_TIME, lambda: delete_messages(message, searching_message)).start()

        except requests.exceptions.HTTPError as e:
            logging.error(f'HTTP error occurred: {e}')
            bot.edit_message_text('There was a problem retrieving the search results. Please try again later.', chat_id=searching_message.chat.id, message_id=searching_message.message_id)
        except requests.exceptions.ConnectionError as e:
            logging.error(f'Connection error occurred: {e}')
            bot.edit_message_text('There was a connection error. Please check your internet connection and try again.', chat_id=searching_message.chat.id, message_id=searching_message.message_id)
        except requests.exceptions.Timeout as e:
            logging.error(f'Timeout error occurred: {e}')
            bot.edit_message_text('The request timed out. Please try again later.', chat_id=searching_message.chat.id, message_id=searching_message.message_id)
        except requests.exceptions.RequestException as e:
            logging.error(f'An error occurred: {e}')
            bot.edit_message_text('An error occurred while fetching data from the API.', chat_id=searching_message.chat.id, message_id=searching_message.message_id)
    else:
        bot.reply_to(message, 'You are not authorized to use this bot.')

def delete_messages(user_message, bot_message):
    try:
        bot.delete_message(user_message.chat.id, user_message.message_id)
        bot.delete_message(bot_message.chat.id, bot_message.message_id)
    except telebot.apihelper.ApiException as e:
        logging.error(f'Error deleting message: {e}')

if __name__ == '__main__':
    bot.polling()
