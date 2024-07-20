import os
import aiohttp
import asyncio
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import Message
import logging
from telegraph.aio import Telegraph

# Load the bot token, API URL, public mode, owner ID, and message deletion time from the config.env file
load_dotenv('config.env')
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
API_URL = os.getenv('API_URL', 'https://apix.starktonyrestinpeace.tech/')
PUBLIC_MODE = os.getenv('PUBLIC_MODE', 'false').lower() == 'true'
OWNER_ID = int(os.getenv('OWNER_ID'))
AUTHORIZED_CHATS = list(map(int, os.getenv('AUTHORIZED_CHATS', '').split(',')))
MESSAGE_DELETION_TIME = int(os.getenv('MESSAGE_DELETION_TIME', '10'))  # Default to 10 seconds

if not TOKEN:
    raise ValueError("No TELEGRAM_BOT_TOKEN provided")
if not API_URL:
    raise ValueError("No API_URL provided")
if not OWNER_ID:
    raise ValueError("No OWNER_ID provided")

# Initialize the bot and Telegraph
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN)
telegraph = Telegraph()

async def init_telegraph():
    await telegraph.create_account(short_name='BotSharer', author_name='YourBotName', author_url='https://t.me/your_bot_username')

# Set up logging
logging.basicConfig(level=logging.INFO)

def is_authorized(chat_id):
    """Check if the chat is authorized."""
    return chat_id in AUTHORIZED_CHATS or chat_id == OWNER_ID

def should_respond(chat_id):
    """Determine if the bot should respond based on the mode."""
    if PUBLIC_MODE:
        return True
    return is_authorized(chat_id)

@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    if should_respond(message.chat.id):
        await message.reply_text('Hi! Send me a movies / series name and I will find results for you.')
    else:
        await message.reply_text('You are not authorized to use this bot.')

@app.on_message(filters.text)
async def search(client: Client, message: Message):
    if should_respond(message.chat.id):
        search_term = message.text
        async with aiohttp.ClientSession() as session:
            try:
                # Send an instant response indicating the search is in progress
                searching_message = await message.reply_text(f'Searching for "{search_term}"...')
                
                async with session.get(f'{API_URL}?search={aiohttp.helpers.quote(search_term)}') as response:
                    response.raise_for_status()
                    results = await response.json()

                if not results:
                    await searching_message.edit_text('No results found.')
                else:
                    # Build the content for the Telegraph page
                    content = []
                    for result in results:
                        content.append({'tag': 'h2', 'children': [f"Title: {result['title']}"]})
                        content.append({'tag': 'p', 'children': [f"Size: {result['size']}"]})
                        content.append({'tag': 'a', 'attrs': {'href': result['link']}, 'children': ['Link']})
                        content.append({'tag': 'hr'})

                    # Create a new Telegraph page
                    response = await telegraph.create_page(
                        title='Search Results',
                        content=content
                    )
                    page_url = f"https://telegra.ph/{response['path']}"

                    # Edit the searching message with the results URL
                    await searching_message.edit_text(f'Here are the results: {page_url}')

                    # Schedule the deletion of both the user's message and the bot's message after the specified time
                    await asyncio.sleep(MESSAGE_DELETION_TIME)
                    await delete_messages(message, searching_message)

            except aiohttp.ClientResponseError as e:
                logging.error(f'HTTP error occurred: {e}')
                await searching_message.edit_text('There was a problem retrieving the search results. Please try again later.')
            except aiohttp.ClientConnectorError as e:
                logging.error(f'Connection error occurred: {e}')
                await searching_message.edit_text('There was a connection error. Please check your internet connection and try again.')
            except asyncio.TimeoutError as e:
                logging.error(f'Timeout error occurred: {e}')
                await searching_message.edit_text('The request timed out. Please try again later.')
            except Exception as e:
                logging.error(f'An error occurred: {e}')
                await searching_message.edit_text('An error occurred while fetching data from the API.')
    else:
        await message.reply_text('You are not authorized to use this bot.')

async def delete_messages(user_message: Message, bot_message: Message):
    try:
        await user_message.delete()
        await bot_message.delete()
    except Exception as e:
        logging.error(f'Error deleting message: {e}')

if __name__ == '__main__':
    app.start()
    asyncio.run(init_telegraph())
    app.idle()
