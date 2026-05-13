# 📦 INSTALE ANTES: pip install pyTelegramBotAPI requests beautifulsoup4
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import requests
from bs4 import BeautifulSoup
import re

# 🔴 SEUS DADOS JÁ PRONTOS 🔴
SEU_TOKEN = "7813790292:AAHlQ-Yf9xcNhbt6nGSg9wtz2b_9Vz_ICbM"
SEU_ID_TELEGRAM = 7852499146

bot = telebot.TeleBot(SEU_TOKEN)

# 🛡️ BLOQUEIO: SÓ VOCÊ USA
@bot.middleware_handler(update_types=['message'])
def verificar_acesso(bot_instance, message):
    if message.chat.id != SEU_ID_TELEGRAM:
        bot.send_message(message.chat.id, "🚫 Acesso negado! Esse bot é exclusivo.")
        raise Exception("Acesso não autorizado")

# 📌 MENU
def menu_principal():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.row(KeyboardButton("🔍 Consultar OAB"), KeyboardButton("❓ Ajuda"))
    return markup

# 🔍 CONSULTA OFICIAL OAB
def consulta_detalhada_oab(numero_oab, uf):
    try:
        url = f"https://www.oab.org.br/ConsultaInscricao/Consulta?numero={numero_oab}&uf={uf.upper()}"
        headers = {"User-Agent": "Mozilla/5.0", "Accept-Language": "pt-BR,pt;q=0.9"}
        resposta = requests.get(url, headers=headers, timeout=15)
        resposta.raise_for_status()
        soup = BeautifulSoup(resposta.text, "html.parser")

        dados = {}
        dados["nome"] = soup.find("span", {"id": "nome"}).get_text(strip=True) if soup.find("span", {"id": "nome"}) else "Não informado"
        dados["inscricao"] = f"{numero_oab}/{uf.upper()}"
        dados["situacao"] = soup.find("span", {"id": "situacao"}).get_text(strip=True) if soup.find("span", {"id": "situacao"}) else "Não informado"
        dados["ano"] = soup.find("span", {"id": "anoInscricao"}).get_text(strip=True) if soup.find("span", {"id": "anoInscricao"}) else "Não informado"
        dados["municipio"] = soup.find("span", {"id": "municipio"}).get_text(strip=True) if soup.find("span", {"id": "municipio"}) else "Não informado"

        especialidades = soup.find("span", {"id": "especialidades"})
        dados["especialidades"] = ", ".join([e.get_text(strip=True) for e in especialidades.find_all("li")]) if especialidades else "Nenhuma cadastrada"

        ocorrencias = soup.find("span", {"id": "ocorrencias"})
        dados["ocorrencias"] = ", ".join([o.get_text(strip=True) for o in ocorrencias.find_all("li")]) if ocorrencias else "Nenhuma ocorrência"

        dados["caa"] = soup.find("span", {"id": "caa"}).get_text(strip=True) if soup.find("span", {"id": "caa"}) else "Não informado"

        if dados["nome"] == "Não informado":
            return {"erro": "❌ Nenhum advogado encontrado com esse número/UF."}
        return dados

    except Exception as e:
        return {"erro": f"⚠️ Erro na consulta: {str(e)}"}

# 🟢 COMANDOS
@bot.message_handler(commands=['start'])
def iniciar(message):
    bot.send_message(message.chat.id, "👋 Olá! Bem-vindo ao seu *Consulta OAB Exclusivo*\n\nUse o menu para consultar.", parse_mode="Markdown", reply_markup=menu_principal())

@bot.message_handler(func=lambda message: True)
def responder(message):
    texto = message.text.strip()

    if texto == "🔍 Consultar OAB":
        bot.send_message(message.chat.id, "📝 Envie: `NÚMERO UF`\nExemplo: `14513 MT`", parse_mode="Markdown")

    elif texto == "❓ Ajuda":
        bot.send_message(message.chat.id, "❓ *COMO USAR:*\n🔹 Formato: `14513 MT`\n🔹 Dados: Nome, Situação, Ano, Cidade, Especialidades, Ética", parse_mode="Markdown")

    else:
        padrao = re.match(r"^(\d+)\s+([A-Za-z]{2})$", texto)
        if not padrao:
            bot.reply_to(message, "❌ Formato errado! Use: `14513 MT`", parse_mode="Markdown")
            return

        numero, uf = padrao.groups()
        bot.send_message(message.chat.id, "🔎 Buscando dados na OAB...")
        res = consulta_detalhada_oab(numero, uf)

        if "erro" in res:
            bot.send_message(message.chat.id, res["erro"])
            return

        msg = f"""📋 *DADOS COMPLETOS OAB {res['inscricao']}*

👤 *Nome:* {res['nome']}
✅ *Situação:* {res['situacao']}
📅 *Ano:* {res['ano']}
📍 *Cidade:* {res['municipio']}

⚖️ *Especialidades:*
{res['especialidades']}

📝 *Ocorrências:*
{res['ocorrencias']}

🏥 *CAA:*
{res['caa']}
"""
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")

# 🚀 INICIAR
if __name__ == "__main__":
    print("✅ BOT EXCLUSIVO RODANDO")
    bot.polling(none_stop=True, interval=0)
    