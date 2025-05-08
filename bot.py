from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, BotCommand, MenuButtonCommands
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import csv
import requests
from io import StringIO

BOT_TOKEN = "7777734579:AAEO2DgIr9BlRGAF3FgKAa0Oh6Z-EPS_II4"
CHANNEL_LINK = "https://t.me/+Lt160mnKTPhjZDY0"
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT-xCUDsB9J9VHBQE6XCz-6W7pampRwj3kKcvYNRrSCTfTMkituw2_4vIzk1Xy02mTHLzmiOX-Ol3B5/pub?gid=2124569128&single=true&output=csv"  # Replace with your real published CSV link

# ✅ Pull live offers from the public Google Sheet (CSV)
def get_offers_by_geo(geo: str):
    response = requests.get(CSV_URL)
    csv_data = response.content.decode('utf-8')
    reader = csv.DictReader(StringIO(csv_data))

    # Filter only rows matching the GEO
    filtered = [row for row in reader if row['Geo'].strip().upper() == geo.strip().upper()]

    if not filtered:
        return f"No offers found for {geo.upper()}."

    # Build the message
    msg = f"💎 Offers for {geo.upper()}:\n\n"
    for offer in filtered:
        brand = offer.get('Brand', 'Unnamed Brand').strip()
        bonus = offer.get('Bonus', '').strip()
        link = offer.get('Link', '').strip()

        msg += f"🎰 *{brand}*🎰\n💵 {bonus}\n✅ [Get Bonus]({link})\n\n"        

    return msg.strip()


# 🚀 /start command — sends initial GEO menu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇬🇧 UK", callback_data='GEO_UK'),
         InlineKeyboardButton("🇺🇸 US", callback_data='GEO_US')],
        [InlineKeyboardButton("🇵🇹 PT", callback_data='GEO_PT'),
         InlineKeyboardButton("🇩🇪 DE", callback_data='GEO_DE')],
        [InlineKeyboardButton("🇳🇱 NL", callback_data='GEO_NL')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Please choose your GEO to see available offers:",
        reply_markup=reply_markup
    )

# ⬅️ Show GEO menu again (on back)
async def show_geo_menu(query):
    keyboard = [
        [InlineKeyboardButton("🇬🇧 UK", callback_data='GEO_UK'),
         InlineKeyboardButton("🇺🇸 US", callback_data='GEO_US')],
        [InlineKeyboardButton("🇵🇹 PT", callback_data='GEO_PT'),
         InlineKeyboardButton("🇩🇪 DE", callback_data='GEO_DE')],
        [InlineKeyboardButton("🇳🇱 NL", callback_data='GEO_NL')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "Please choose your GEO to see available offers:",
        reply_markup=reply_markup
    )

# 📦 Show offers for selected GEO + Join Channel + Back
async def show_offers(query, geo):
    geo_code = geo.upper()

    # Get offers from CSV
    message_text = get_offers_by_geo(geo_code)

    buttons = [
        [InlineKeyboardButton("🔔 Join our channel for updates", url=CHANNEL_LINK)],
        [InlineKeyboardButton("← Back", callback_data='BACK')]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    await query.edit_message_text(
        text=message_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# 🧠 Handle all button clicks
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("GEO_"):
        geo = data.split("_")[1]
        await show_offers(query, geo)
    elif data == "BACK":
        await show_geo_menu(query)
    elif data == "offer_click":
        await query.answer("✅ Offer clicked!")

# 📋 Set command menu + persistent Menu button
async def set_menu(app):
    await app.bot.set_my_commands([
        BotCommand("start", "Choose GEO"),        
        BotCommand("help", "Get help"),
    ])
    await app.bot.set_chat_menu_button(
        menu_button=MenuButtonCommands()
    )

# 🏁 Run the bot
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.post_init = set_menu

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
