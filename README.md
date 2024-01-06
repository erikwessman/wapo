# WAPO Bot

A bot that sends a link to today's Washington Post crossword puzzle (and a bit more)

- [WAPO Bot](#wapo-bot)
  - [Setup](#setup)
    - [Run with kool.dev 😎 🤙](#run-with-kooldev--)
    - [Run with Docker 😬](#run-with-docker-)
      - [Run a Clean Installation](#run-a-clean-installation)


## Setup

Create and setup .env file:

```
DISCORD_TOKEN=your_token
```

### Run with kool.dev 😎 🤙

(Install kool.dev: `curl -fsSL https://kool.dev/install | bash`)

```bash
kool run dev
```

### Run with Docker 😬

I dunno search it up, but you can do it

#### Run a Clean Installation

⚠️ ONLY FOR DEV, WILL RESET IT ⚠️

```bash
docker stop $(docker ps -aq) && docker rm $(docker ps -aq) && docker-compose up --build
```
