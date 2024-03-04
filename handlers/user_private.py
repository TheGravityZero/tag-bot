import os

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv(), override=True)

from aiogram import Bot, F, types, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import ChatJoinRequest, ContentType
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import orm_add_user

from filters.chat_types import ChatTypeFilter

from kbds.reply import get_keyboard
from database.orm_query import orm_get_user

from database.texts import texts

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, bot: Bot):
    text = texts["start"]
    photo_path = r"images\\preview.png"
    photo = types.FSInputFile(photo_path)
    await message.answer_photo(photo,
        caption=text,
        reply_markup=get_keyboard(
            "Забрать 🎁",
            "Хочу в закрытый тг",
            "Доступ на 1 счастливый месяц",
            "Доступ на 3 успешных месяца🔥",
            "Условия",
            placeholder="Что вас интересует?",
            sizes=(2, 2, 1)
        ),
        parse_mode=ParseMode.MARKDOWN
    )
    #await message.answer_photo(photo)



@user_private_router.message((F.text.lower().contains("забрать")))
async def locations_cmd(message: types.Message, session: AsyncSession):
    await message.answer("Загружаю подарок...")
    doc_path = r"images\\prize.pdf"
    doc = types.FSInputFile(doc_path)
    await message.answer_document(doc)


@user_private_router.message(F.text.lower() == "хочу в закрытый тг")
async def about_cmd(message: types.Message):
    text = texts["about"]
    await message.answer(text, parse_mode='Markdown')


@user_private_router.message(F.text.lower() == "доступ на 1 счастливый месяц")
async def subscriptions_cmd(message: types.Message, bot: Bot): 
    text = texts["month"]
    invoice = types.LabeledPrice(label='RUB', amount=10000)
    photo_path = r"images\\month.png"
    photo = types.FSInputFile(photo_path)

    await message.answer_photo(photo, caption=text, parse_mode='Markdown')
    result = await bot.send_invoice(
    message.chat.id,
    title="Доступ на месяц",
    description="Подписка действует с даты списания средств",
    provider_token=os.getenv('PAYMENTS_PROVIDER_TOKEN'),
    currency='RUB',
    need_phone_number=True,
    is_flexible=False, 
    prices=[invoice],
    start_parameter='test',
    payload='month'
    )


@user_private_router.message(F.text.lower() == "доступ на 3 успешных месяца🔥")
async def sub_3_months_cmd(message: types.Message, bot: Bot, session: AsyncSession):
    text = texts["months"]
    
    invoice = types.LabeledPrice(label='RUB', amount=10000)
    photo_path = r"images\\months.png"
    photo = types.FSInputFile(photo_path)
    
    await message.answer_photo(photo, caption=text, parse_mode='Markdown')
    await bot.send_invoice(
    message.chat.id,
    title="Доступ на 3 месяца",
    description="Подписка действует с даты списания средств",
    provider_token=os.getenv('PAYMENTS_PROVIDER_TOKEN'),
    currency='RUB',
    need_phone_number=True,
    is_flexible=False,
    prices=[invoice],
    start_parameter='test',
    payload='months'
    )


@user_private_router.message(F.text.lower() == "условия")
async def shipping_cmd(message: types.Message):
    text = "Контакты: @taglocation"
    await message.answer(text)


@user_private_router.pre_checkout_query()
async def pre_checkout_query_handler(query: types.PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(query.id, ok=True)


@user_private_router.message(F.successful_payment)
async def process_payment(message: types.Message, session: AsyncSession):
    user = await orm_get_user(session, message.from_user.id)
    if user is not None and user.subscribe:
        message.answer("Вы уже подписаны.")
    else:
        data = {
            "id": message.from_user.id,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
            "phone": message.successful_payment.order_info.phone_number,
            "subscribe": True,
            "start": message.date
        }
        if message.successful_payment.invoice_payload=="months":
            data["end"] = message.date + timedelta(days=90)
        else:
            data["end"] = message.date + timedelta(days=30)
        await orm_add_user(session, data)
        await message.answer(f"Сслыка в закрытый тг канал {os.getenv('INVITE_LINK')}")


@user_private_router.chat_join_request(F.chat.id==int(os.getenv('CHANNEL_ID')))
async def approve_request(chat_join: ChatJoinRequest, bot: Bot, session: AsyncSession):
    user = await orm_get_user(session, chat_join.from_user.id)
    if user is None or user == 0:
        await chat_join.decline()
        await bot.send_message(chat_id=chat_join.from_user.id, text="Вы не оплатили подписку.")
    else:
        print("good")
        await chat_join.approve()