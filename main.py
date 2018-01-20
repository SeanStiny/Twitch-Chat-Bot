import Bot

log = True

channel = input("Enter the Twitch channel to join: ")
bot = Bot.Bot(channel)
bot.start(log)
