# Twitch Chat Bot

## About

This is a simple Twitch chat bot that I will continue to add more features to. It's main purpose is for my own Twitch chat but I thought I would share the source for anyone that wishes to use it.

Requires Python 3.6 to run.

## How to use

Simply run main.py and enter the on-screen prompts. You can find your Twitch oauth key via [Twitch Apps](https://twitchapps.com/tmi/).

Once the bot is up and running in your chat, the following commands are currently available:
- !add <prompt> <response>: Adds a new bot response with the specificied command prompt.
- !addmod <prompt> <response>: Adds a new bot response that can only be triggered by a chat moderator.
- !remove <prompt>: Removes a previously added command.
