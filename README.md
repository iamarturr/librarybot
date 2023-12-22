# Librarybot

This project is a telegram bot library for viewing books.

## Setup

1. Clone the repository:

    ```bash
    git clone https://github.com/iamarturr/librarybot.git
    cd librarybot
    ```

2. Create a `.env` file in the project root and set the `BOT_TOKEN` variable:

    ```plaintext
    BOT_TOKEN=your_bot_token_here
    ```
    For example:
    ```bash
    echo "BOT_TOKEN=your_bot_token_here" > .env
    ```

3. Build and run the Docker containers:

    ```bash
    docker-compose up -d
    ```

4. Command to turn off the bot
    ```bash
    docker-compose down
    ```
## Windows Setup

1. Download [Python 3.9+](https://www.python.org/downloads/release/python-390/)
2. Download [this repository](https://github.com/iamarturr/librarybot).
3. Create .env file in the project root
   ```plaintext
   BOT_TOKEN=your_bot_token_here
   ```
5. Install requirements
    ```bash
    python -r app/requirements.txt
    ```
6. Run bot
    ```bash
    python app/loader.py
    ```
## License

[MIT](LICENSE)
