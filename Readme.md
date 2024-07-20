# Telegram Movies / Series Index Search Bot

This Telegram bot allows users to search for data via an API and provides the results as a Telegraph page. The bot responds to search commands, fetches data, and sends results back to the user.

## Features

- Responds to `/start` command with a welcome message.
- Searches for data based on user input.
- Posts search results to a Telegraph page.
- Supports both public and authorized modes.

## Prerequisites

1. **Python 3.8+**: Ensure you have Python 3.8 or higher installed on your system.
2. **Telegram Bot Token**: You need a Telegram Bot Token from [BotFather](https://t.me/botfather).
3. **API Endpoint**: The bot fetches data from an external API. Ensure the API URL is available.
4. **Telegraph API**: Used for posting search results. No additional setup is required beyond the provided account creation in the code.

## Setup

1. **Clone the Repository**

    ```bash
    git clone https://github.com/xskdnj/gdriveindexsearchbot.git
    cd gdriveindexsearchbot
    ```

2. **Create a Virtual Environment**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    ```

3. **Install Dependencies**

    ```bash
    pip3 install -r requirements.txt
    ```

4. **Edit `config.env` File**

    

    ```env
    TELEGRAM_BOT_TOKEN=your_telegram_bot_token
    PUBLIC_MODE=True
    MESSAGE_DELETION_TIME=10
    OWNER_ID=your_telegram_user_id
    AUTHORIZED_CHATS=comma_separated_list_of_chat_ids
    ```

5. **Run the Bot**

    ```bash
    nohup python3 bot.py &
    ```

## Usage

- **Start Command**: Send `/start` to the bot to receive a welcome message.
- **Search**: Send any text to the bot to initiate a search. The bot will respond with search results or an error message.

- a sample bot [Gdrive Index Search Bot](https://t.me/gdriveindexsearch1bot).


## Logging

Logs are available in the console. They include errors and other important messages.

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Create a new Pull Request.

---

- **Join our Telegram Channel**: For further support and updates, [Stark Media Hub](https://t.me/starkmediahub).
