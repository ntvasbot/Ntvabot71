import telebot
import requests
import json
import time
import threading
import schedule
from telebot import types
from datetime import datetime

# --- CONFIGURACOES DO BOT ---
TOKEN = '7686670285:AAE3WSKt8HoqYnm6m6aXmGMb6-Hue8VShX0'
ADMIN_ID = 6782574931
SMS_ACTIVATE_API = 'd93d557720A61172d34d946Ac610e7f3'

bot = telebot.TeleBot(TOKEN)

# --- BASES DE DADOS SIMPLES ---
usuarios = {}
saldos = {}
compras = {}
recargas_pendentes = {}

facebook_prontos = {
    "D - Diogo hortega (R$20)": {"login": "17982307535", "senha": "22setembro95@"},
    "H - Higor kalleb (R$20)": {"login": "12981783300", "senha": "22setembro95"},
    "M - Piu Santana (R$20)": {"login": "11980991935", "senha": "22setembro95."},
}

# --- /START ---
@bot.message_handler(commands=['start'])
def start(m):
    usuarios[m.from_user.id] = {'nome': m.from_user.first_name}
    if m.from_user.id not in saldos:
        saldos[m.from_user.id] = 0
    if m.from_user.id not in compras:
        compras[m.from_user.id] = 0
    menu_principal(m)

def menu_principal(m):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Facebook Pronto', 'Saldo / Recarga')
    bot.send_message(m.chat.id, 'Escolha uma opção abaixo:', reply_markup=markup)

# --- FACEBOOK PRONTO ---
@bot.message_handler(func=lambda m: m.text == 'Facebook Pronto')
def facebook_pronto(m):
    total = compras.get(m.from_user.id, 0)
    markup = types.InlineKeyboardMarkup()
    for nome in facebook_prontos:
        markup.add(types.InlineKeyboardButton(text=nome, callback_data=f"comprar_{nome}"))
    msg = f"*Contas disponíveis:*
\n" + "\n".join([f"• {nome}" for nome in facebook_prontos])
    msg += f"\n\n🎁 Promoção: Compre 7 e leve a 8ª grátis!\n📊 Você já comprou {total} Facebook(s)."
    bot.send_message(m.chat.id, msg, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("comprar_"))
def realizar_compra(call):
    user_id = call.from_user.id
    nome_conta = call.data.replace("comprar_", "")
    if saldos.get(user_id, 0) < 20:
        bot.answer_callback_query(call.id, "❌ Saldo insuficiente. Recarga mínima: R$20.")
        return
    if nome_conta not in facebook_prontos:
        bot.answer_callback_query(call.id, "❌ Conta não disponível.")
        return

    saldos[user_id] -= 20
    dados = facebook_prontos.pop(nome_conta)
    compras[user_id] += 1
    
    bot.send_message(call.message.chat.id, f"✅ Compra realizada!\n\n🔐 Login: `{dados['login']}`\n🔑 Senha: `{dados['senha']}`", parse_mode="Markdown")

    bot.send_message(ADMIN_ID, f"📦 Nova venda de Facebook!\n👤 {call.from_user.first_name} (ID: {user_id})\nConta: {nome_conta}")

    if compras[user_id] == 7:
        bot.send_message(user_id, "🎁 Você ganhou um Facebook pronto GRÁTIS!")
        bot.send_message(ADMIN_ID, f"🎉 {call.from_user.first_name} completou 7 compras e ganhou uma conta grátis!")

# --- RECARGA DE SALDO ---
@bot.message_handler(func=lambda m: m.text == 'Saldo / Recarga')
def menu_recarga(m):
    markup = types.InlineKeyboardMarkup()
    for valor in [20, 30, 40, 50, 75, 100]:
        markup.add(types.InlineKeyboardButton(f"R${valor}", callback_data=f"valor_{valor}"))
    bot.send_message(m.chat.id, "💸 Escolha o valor da recarga:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("valor_"))
def solicitar_dados_pagador(call):
    valor = call.data.split("_")[1]
    bot.send_message(call.message.chat.id, f"Digite o nome e banco do pagador para recarga de R${valor}:\n\nExemplo:\nJoão Silva\nBanco do Brasil")
    bot.register_next_step_handler(call.message, lambda m: processar_dados_pagador(m, valor))

def processar_dados_pagador(m, valor):
    linhas = m.text.split("\n")
    if len(linhas) != 2:
        return bot.send_message(m.chat.id, "❌ Formato inválido. Envie nome e banco em 2 linhas.")
    nome, banco = linhas
    user_id = m.from_user.id
    recargas_pendentes[user_id] = float(valor)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Confirmar Recarga", callback_data=f"confirmar_recarga_{user_id}"))

    bot.send_message(ADMIN_ID, f"🧾 Recarga pendente:\n👤 {nome}\n🏦 {banco}\n💰 R${valor}\nID: {user_id}", reply_markup=markup)
    bot.send_message(m.chat.id, f"Enviado ao ADM. Aguarde a liberação do saldo.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirmar_recarga_"))
def confirmar_recarga(call):
    user_id = int(call.data.split("_")[-1])
    valor = recargas_pendentes.get(user_id)
    if valor:
        saldos[user_id] = saldos.get(user_id, 0) + valor
        del recargas_pendentes[user_id]
        bot.send_message(user_id, f"✅ Recarga de R${valor:.2f} confirmada. Saldo liberado!")
        bot.send_message(ADMIN_ID, f"Saldo liberado para ID {user_id}.")
    else:
        bot.send_message(call.message.chat.id, "⚠️ Recarga não encontrada ou já confirmada.")

# --- INICIO DO BOT ---
bot.send_message(ADMIN_ID, "✅ BOT INICIADO COM SUCESSO!")
print("BOT rodando...")
bot.polling()
