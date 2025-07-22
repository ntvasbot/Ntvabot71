import telebot
from telebot import types

TOKEN = '7686670285:AAE3WSKt8HoqYnm6m6aXmGMb6-Hue8VShX0'
ADMIN_ID = 6782574931

bot = telebot.TeleBot(TOKEN)

# Dados em memória
saldos = {}
compras = {}
facebook_prontos = {
    "D - Diogo hortega (R$20)": {"login": "17982307535", "senha": "22setembro95@"},
    "H - Higor kalleb (R$20)": {"login": "12981783300", "senha": "22setembro95"},
    "M - Piu Santana (R$20)": {"login": "11980991935", "senha": "22setembro95."},
}

@bot.message_handler(commands=['start'])
def send_welcome(m):
    uid = m.from_user.id
    if uid not in saldos:
        saldos[uid] = 40  # saldo inicial de teste
    if uid not in compras:
        compras[uid] = 0

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Facebook Pronto", "Ver Saldo")
    bot.send_message(m.chat.id, "✅ Bot iniciado com sucesso!\n\nEscolha uma opção abaixo:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "Ver Saldo")
def ver_saldo(m):
    saldo = saldos.get(m.from_user.id, 0)
    bot.send_message(m.chat.id, f"💰 Seu saldo: R${saldo:.2f}")

@bot.message_handler(func=lambda m: m.text == "Facebook Pronto")
def facebook_pronto(m):
    uid = m.from_user.id
    markup = types.InlineKeyboardMarkup()
    for nome in facebook_prontos:
        markup.add(types.InlineKeyboardButton(nome, callback_data=f"comprar_{nome}"))
    total = compras.get(uid, 0)
    texto = f"🛒 Contas disponíveis:\n\n"
    texto += "\n".join([f"• {nome}" for nome in facebook_prontos])
    texto += f"\n\n🎁 Promoção: Compre 7 e leve a 8ª grátis!\n📊 Você já comprou {total} Facebook(s)."
    bot.send_message(m.chat.id, texto, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("comprar_"))
def realizar_compra(call):
    uid = call.from_user.id
    nome_conta = call.data.replace("comprar_", "")

    if nome_conta not in facebook_prontos:
        bot.answer_callback_query(call.id, "❌ Conta não está mais disponível.")
        return

    if saldos.get(uid, 0) < 20:
        bot.send_message(call.message.chat.id, "❌ Saldo insuficiente. Recarga mínima: R$20.")
        return

    # Compra
    saldos[uid] -= 20
    compras[uid] += 1
    dados = facebook_prontos.pop(nome_conta)

    bot.send_message(call.message.chat.id,
        f"✅ Compra realizada!\n\n🔐 Login: `{dados['login']}`\n🔑 Senha: `{dados['senha']}`",
        parse_mode="Markdown")

    bot.send_message(ADMIN_ID,
        f"📦 Nova compra!\n👤 {call.from_user.first_name} (ID: {uid})\n📘 Conta: {nome_conta}\n🔐 Login: `{dados['login']}`",
        parse_mode="Markdown")

    if compras[uid] == 7:
        bot.send_message(uid, "🎁 Você ganhou um Facebook pronto GRÁTIS!")
        bot.send_message(ADMIN_ID, f"🎉 {call.from_user.first_name} completou 7 compras e ganhou uma conta grátis!")

bot.polling()
