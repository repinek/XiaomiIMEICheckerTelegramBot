import datetime
import asyncio
import aiohttp
import logging
import json
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

load_dotenv()
logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.getenv("BOT_TOKEN")) # from .env file
dp = Dispatcher()

class IMEICheckState(StatesGroup):
    fill_imei = State() # also may be s/m
    fill_captcha = State()

def return_keyboard(text):
    builder = InlineKeyboardBuilder()
    builder.button(text=text, callback_data="return_to_start")
    return builder.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="Check IMEI or S/N", callback_data="check_imei")
    # builder.button(text="Check 20-digit security code", callback_data="security_code")
    builder.button(text="Where I can find IMEI and S/N?", callback_data="find_imei_sn_help")
    builder.adjust(1)

    await message.answer(
        "Hey! This is Xiaomi Product Authentication. With this bot you can check your IMEI or S/N and get details like model, country, and manufacture date for your Xiaomi.\n\nWorking using https://www.mi.com/global/verify.",
        reply_markup=builder.as_markup()
    )

# Cancel handler
@dp.callback_query(F.data == "return_to_start")
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await cmd_start(callback.message)
    await callback.answer()

# Check IMEI FSM
@dp.callback_query(StateFilter(None), F.data == "check_imei")
async def fill_imei(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(text="Please enter IMEI or S/N:", reply_markup=return_keyboard("Cancel"))
    await state.set_state(IMEICheckState.fill_imei)
    await callback.answer()

@dp.message(IMEICheckState.fill_imei)
async def fill_captcha(message: types.Message, state: FSMContext):
    imei = message.text.strip() # it also may be s/n, so you can't put check for 15 symbols length lmao

    # You need the same session to generate captcha and send request to check IMEI
    session = aiohttp.ClientSession()
    await state.update_data(imei=imei, session=session) # save imei and session to state

    captcha_image_url = f"https://buy.mi.com/en/other/getimage" # generate captcha img
    path_to_captcha_image = "media/captcha.png" # download message cuz I can't figure how to use the same session for answer_photo
    async with session.get(captcha_image_url) as response:
        image = await response.read()
        with open(path_to_captcha_image, "wb") as f:
            f.write(image)

    await message.answer_photo(types.FSInputFile(path=path_to_captcha_image), caption="Please fill the captcha to continue", reply_markup=return_keyboard("Cancel"))
    await state.set_state(IMEICheckState.fill_captcha)


@dp.message(IMEICheckState.fill_captcha)
async def fill_captcha(message: types.Message, state: FSMContext):
    captcha = message.text.strip()
    user_data = await state.get_data()
    session = user_data["session"]

    if len(captcha) == 4:
        url = "https://buy.mi.com/en/other/checkimei"
        params = {
            "jsonpcallback": "JSON_CALLBACK",
            "keyword": user_data["imei"],
            "vcode": captcha,
        }

        async with session.get(url, params=params) as response:
            text = await response.text()
            print(text)

        # remove uhhh
        start = text.find("JSON_CALLBACK(")
        end = text.rfind(");")
        # parse
        json_text = text[start + len("JSON_CALLBACK("):end]
        json_data = json.loads(json_text)
        code = int(json_data["code"])
        match code:
            case 1:
                device_data = json_data["data"]
                match device_data["country_text"]:
                    case "China":
                        additional_text = (
                            "However, the device you purchased is a China version (CN), "
                            "not the official GLOBAL one. This may affect supported languages, "
                            "network bands, and overall user experience."
                            "\nIf your phone shows a GLOBAL firmware with a locked bootloader, "
                            "it means the device is running an unofficial, modified ROM."
                        )

                    case "Greenland":
                        additional_text = (
                            "It seems that your device has been refurbished. "
                            "This usually means it was previously returned, repaired or restored "
                            "to working condition by the third-party service. "
                            "Refurbished devices can still function well, but they may have replaced "
                            "parts and won’t always match the original factory condition and description. "
                            "For example, the color may be different from what is written here."
                        )
                    case _:
                        additional_text = "Congratulations! You can be assured the phone you have purchased is the official international version."

                converted_date = datetime.datetime.fromtimestamp(device_data["add_time"], tz=datetime.timezone.utc).strftime('%d/%m/%Y %H:%M:%S')
                await message.answer(f"Product name: {device_data[f"goods_name"]}\nManufacture date: {converted_date}\nCounty: {device_data["country_text"]}\n\n{additional_text}", reply_markup=return_keyboard("Return to Menu"))
            case 70011:
                await message.answer("Invalid Captcha, Try again.", reply_markup=return_keyboard("Return to Menu"))
            case 70013 | 70017:
                await message.answer("IMEI or S/N doesn't exist.", reply_markup=return_keyboard("Return to Menu"))
            case _:
                await message.answer("Xiaomi Server is busy, please try again later.", reply_markup=return_keyboard("Return to Menu"))
    else:
        await message.answer("Invalid Captcha, Try again.", reply_markup=return_keyboard("Return to Menu"))

    await session.close()
    await state.clear()

@dp.callback_query(F.data == "find_imei_sn_help")
async def find_imei_sn_help(callback: types.CallbackQuery):
    await callback.message.answer_photo(types.FSInputFile(path="media/imei-help.png"), caption="Method 1\nFind the code sticker on the back of device, or packaging box\n\n"
                                                                                               "Method 2\nEnter *#06# on the dialpad to find your IMEI")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())