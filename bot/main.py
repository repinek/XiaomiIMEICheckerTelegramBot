import asyncio
import datetime
import json
import logging
from typing import Final, cast

import aiohttp
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import (
    BOT_TOKEN,
    CAPTCHA_IMAGE_URL,
    CHECK_IMEI_URL,
    COUNTRY_MESSAGES,
    MESSAGES,
)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def back_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="‹ Menu", callback_data="menu")
    return builder.as_markup()


def menu_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Check IMEI or S/N", callback_data="check_imei")
    builder.button(text="Where I can find IMEI and S/N?", callback_data="imei_help")
    # builder.button(text="Check 20-digit security code", callback_data="security_code")
    builder.adjust(1)
    return builder.as_markup()


class IMEICheckState(StatesGroup):
    fill_imei: Final = State()
    """IMEI and also may be s/n"""
    fill_captcha: Final = State()


@dp.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    """
    I'm too lazy to add 20digit security code checking it so:
    Get captcha: https://captcha.hd.mi.com/captcha?style=digit
    Verify captcha and check security code: https://captcha.hd.mi.com/captcha/auth
    Check browser DevTools for headers.
    and also Product Types for it:
    ProductTypes={0:"Mi Adapter / Cable", 1:"Mi Power Bank", 2:"Mi Pad", 3:"Mi Bluetooth Headset", 4:"Mi Air Purifier Filter", 5:"Mi Water Purifier Filter", 6:"Mi Electric Toothbrush", 7:"Mi Electric Shaver"}
    """

    await message.answer(
        text=MESSAGES["greeting"],
        reply_markup=menu_keyboard(),
    )


@dp.callback_query(F.data == "menu")
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await cmd_start(callback.message)
    await callback.answer()


@dp.callback_query(StateFilter(None), F.data == "check_imei")
async def fill_imei(callback: types.CallbackQuery, state: FSMContext) -> None:
    # NOTE: Callback message may not available in special cases
    if callback.message is None:
        return

    await callback.message.reply(
        text=MESSAGES["enter_imei"],
        reply_markup=back_keyboard(),
    )
    await state.set_state(IMEICheckState.fill_imei)
    await callback.answer()


@dp.message(IMEICheckState.fill_imei)
async def fill_captcha(message: types.Message, state: FSMContext):
    # TODO: add logic or use aiogram filters
    if message.text is None:
        return

    imei = message.text.strip()

    # TODO: add validation (not necessary because s\n can have irregular format)
    # if not (len(imei) == 15 and imei.isdigit()):

    # You need the same session to generate captcha and send request to check IMEI
    session = aiohttp.ClientSession()
    await state.update_data(imei=imei, session=session)

    async with session.get(CAPTCHA_IMAGE_URL) as response:
        image = await response.read()
        await message.answer_photo(
            photo=BufferedInputFile(image, filename="captcha.png"),
            caption=MESSAGES["enter_captcha"],
            reply_markup=back_keyboard(),
        )
    await state.set_state(IMEICheckState.fill_captcha)


@dp.message(IMEICheckState.fill_captcha)
async def fill_captcha(message: types.Message, state: FSMContext):
    # TODO: add logic or use aiogram filters
    if message.text is None:
        return

    captcha = message.text.strip()
    user_data = await state.get_data()
    session = cast(aiohttp.ClientSession, user_data["session"])

    if len(captcha) != 4:
        await message.answer(
            text=MESSAGES["invalid_captcha"],
            reply_markup=back_keyboard(),
        )
        return

    params = {
        "keyword": user_data["imei"],
        "vcode": captcha,
    }

    async with session.get(CHECK_IMEI_URL, params=params) as response:
        text = await response.text()

    json_data = json.loads(text)
    code = int(json_data["code"])
    match code:
        case 1:
            device_data = json_data["data"]
            additional_text = COUNTRY_MESSAGES.get(
                device_data["country_text"], COUNTRY_MESSAGES[None]
            )
            converted_date = datetime.datetime.fromtimestamp(
                device_data["add_time"], datetime.timezone.utc
            ).strftime("%d/%m/%Y %H:%M:%S")
            await message.answer(
                text=f"Product name: {device_data[f'goods_name']}\nManufacture date: {converted_date}\nCounty: {device_data['country_text']}\n\n{additional_text}",
                reply_markup=back_keyboard(),
            )
        case 70011:
            await message.answer(
                text=MESSAGES["invalid_captcha"],
                reply_markup=back_keyboard(),
            )
        case 70013 | 70017:
            await message.answer(
                text=MESSAGES["imei_not_exist"],
                reply_markup=back_keyboard(),
            )
        case _:
            await message.answer(
                text=MESSAGES["server_busy"],
                reply_markup=back_keyboard(),
            )

    await session.close()
    await state.clear()


@dp.callback_query(F.data == "imei_help")
async def imei_help(callback: types.CallbackQuery) -> None:
    # NOTE: Callback message may not available in special cases
    if callback.message is None:
        return

    await callback.message.answer_photo(
        photo=FSInputFile(path="./media/imei-help.png"), # IDK about this path, you can use webfile from xiaomi serverss
        caption=MESSAGES["imei_help"],
    )


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
