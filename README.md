# Xiaomi IMEI Checker Telegram Bot

Telegram bot built with [aiogram](https://github.com/aiogram/aiogram) that directly uses [Xiaomi API](https://www.mi.com/global/verify)
to check Xiaomi IMEI or S/N and get details like model, country, and manufacture date for your Xiaomi.  

### [Try here](https://t.me/XiaomiIMEIChecker_bot)

## Screenshot
<img width="200" height="297" alt="image" src="https://github.com/user-attachments/assets/0d5f985b-b1e1-44e5-a03c-f0db7be235da"/>

## Usage
1. Clone the repo
```bash
git clone https://github.com/repinek/XiaomiIMEICheckerTelegramBot.git
cd XiaomiIMEICheckerTelegramBot
```
2. Install dependencies using `uv`:
```bash
uv sync
```
or using `pip`
```bash
python -m venv .venv

# Using Linux/MacOS
source .venv/bin/activate 
# Using Windows
.venv/Scripts/activate

pip install -r requirements.txt
```
3. Create a `.env` file and add your token from [@BotFather](https://t.me/botfather)
```bash
cp .env.example .env
```
4. Run the bot:
```bash
# Using uv
uv run -m bot.main

# Using standart python
python -m bot.main
```

## How it works? 
1. Generates captcha using [buy.mi.com/en/other/getimage](https://buy.mi.com/en/other/getimage)
2. Using the same session, send a request to [buy.mi.com/en/other/checkimei](https://buy.mi.com/en/other/checkimei) with the following headers:
```json
"keyword": {imei},
"vcode": {captcha},
```

*For details regarding the 20-digit security code, please refer to the source code or use browser DevTools on the official site*
