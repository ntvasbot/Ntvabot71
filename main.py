import telebot

TOKEN = '7686670285:AAE3WSKt8HoqYnm6m6aXmGMb6-Hue8VShX0'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "✅ Bot iniciado com sucesso!\nSeja bem-vindo ao NTVA-BOT!")

bot.polling()
