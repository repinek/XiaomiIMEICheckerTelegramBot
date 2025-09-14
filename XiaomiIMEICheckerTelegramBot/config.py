import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

CAPTCHA_IMAGE_URL = "https://buy.mi.com/en/other/getimage"
"""generate captcha img url"""
CHECK_IMEI_URL = "https://buy.mi.com/en/other/checkimei"

MESSAGES = {
    "greeting": (
        "Hey! This is Xiaomi Product Authentication. "
        "With this bot you can check your IMEI or S/N and get details like model, country, "
        "and manufacture date for your Xiaomi.\n\n"
        "Working using https://www.mi.com/global/verify."
    ),
    "enter_imei": "Please enter IMEI or S/N:",
    "enter_captcha": "Please fill the captcha to continue",
    "invalid_captcha": "Invalid captcha, try again.",
    "imei_not_exist": "IMEI or S/N doesn't exist.",
    "server_busy": "Xiaomi server is busy, please try again later.",
    "imei_help": (
        "Method 1\nFind the code sticker on the back of device, or packaging box\n\n"
        "Method 2\nEnter *#06# on the dialpad to find your IMEI"
    ),
}

COUNTRY_MESSAGES = {
    "China": (
        "However, the device you purchased is a China version (CN), "
        "not the official GLOBAL one. This may affect supported languages, "
        "network bands, and overall user experience.\n"
        "If your phone shows a GLOBAL firmware with a locked bootloader, "
        "it means the device is running an unofficial, modified ROM."
    ),
    "Greenland": (
        "It seems that your device has been refurbished. "
        "This usually means it was previously returned, repaired or restored "
        "to working condition by the third-party service. "
        "Refurbished devices can still function well, but they may have replaced "
        "parts and won’t always match the original factory condition and description. "
        "For example, the color may be different from what is written here."
    ),
    None: "Congratulations! You can be assured the phone you have purchased is the official international version.",
}
