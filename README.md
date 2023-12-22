# Telegram Bot Project

This project is a Telegram bot implemented in Python using the aiogram library. It is Dockerized for easy deployment.

## Setup

1. Clone the repository:

    ```bash
    git clone https://github.com/protesians/librarybot.git
    cd librarybot-project
    ```

2. Create a `.env` file in the project root and set the `TELEGRAM_BOT_TOKEN` variable:

    ```plaintext
    # .env
    BOT_TOKEN=your_bot_token_here
    ```

3. Build and run the Docker containers:

    ```bash
    docker-compose up -d
    ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
