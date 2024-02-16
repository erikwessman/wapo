# WAPO Bot

A bot that sends a link to today's Washington Post crossword puzzle (and a bit more)

- [WAPO Bot](#wapo-bot)
  - [Start the bot](#start-the-bot)
    - [.env file](#env-file)
    - [Start with kool.dev](#start-with-kooldev)
    - [Start manually](#start-manually)
  - [kool commands](#kool-commands)

## Start the bot

How to start the bot:

1. Setup the .env file as shown [here](#env-file)
2. Start with kool.dev as shown [here](#run-with-kooldev) _(recommended)_
3. OR, start manually, see [Start manually](#start-manually)

### .env file

```yml
DISCORD_TOKEN=your_token # REQUIRED

# OPTIONAL Only needed if running locally
# with non-default values
MONGO_HOST=your_hostname
MONGO_USER=your_username
MONGO_PASS=your_password
```

### Start with kool.dev

1. (Install kool.dev: `curl -fsSL https://kool.dev/install | bash`)
2. Run the following command: `kool run dev`
3. Start the bot with `python src/bot.py`

### Start manually

1. Setup the .env file
2. Install dependencies in `requirements.txt`
3. Start a MongoDB instance
4. Start the bot with `python src/bot.py`

## kool commands

> [!WARNING]
> Still in development, have not tested DB persistence yet. Use at your own risk 🤖

🚀 Start local dev environment:

```bash
kool run dev
```

🐚 Enter the shell of the dev environment (must be running)

```bash
kool run shell
```

🧹 Lint code:

```bash
kool run lint
```
