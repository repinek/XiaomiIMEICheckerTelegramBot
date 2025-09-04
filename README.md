# Xiaomi IMEI Checker Telegram Bot

Telegram bot built with [aiogram](https://github.com/aiogram/aiogram) that directly uses [mi.com/global/verify](https://www.mi.com/global/verify) to check Xiaomi IMEI or S/N get details like model, country, and manufacture date for your Xiaomi. 

## Screenshots

## Usage
1. Clone the repo
```
git clone https://repinek/XiaomiIMEICheckerTelegramBot
cd XiaomiIMEICheckerTelegramBot
```
2. Install requirements:
```
pip install -r requirements.txt
```
3. Rename ```.env.EXAMPLE``` to ```.env``` and change to your token from [@BotFather](https://t.me/botfather)
4. Run:
```
python main.py
```

## How it works? 
1. Generate captcha using [buy.mi.com/en/other/getimage](https://buy.mi.com/en/other/getimage)
2. Using the same session, send a request to [buy.mi.com/en/other/checkimei](https://buy.mi.com/en/other/checkimei) with the following headers:
```
"keyword": {imei},
"vcode": {captcha},
```

for the 20-digit security code, please refer to the source code and use devtools