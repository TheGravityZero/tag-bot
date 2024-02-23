import os

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from aiogram import Bot, F, types, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, or_f
from aiogram.utils.formatting import (
    as_list,
    as_marked_section,
    Bold,
)
from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import orm_get_products  # Italic, as_numbered_list и тд

from filters.chat_types import ChatTypeFilter

from kbds.reply import get_keyboard

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, bot: Bot):
    text = """
Залы фотостудий уже все знают наизусть, а на улице еще грязно, чтобы снимать кайфовый streetstyle?

В нашем тг-канале и на сайте вас ждет более 150 стильных мест Екатеринбурга, в которых можно провести съемки.

Поэтому сейчас самое время забрать подарочную подборку необычных локаций в феврале!

Для этого в меню нужно нажать «Локации🎁»"""
    photo_path = r"images\\preview.png"
    photo = types.FSInputFile(photo_path)
    await message.answer_photo(photo,
        caption=text,
        reply_markup=get_keyboard(
            "Забрать 🎁",
            "Хочу в закрытый тг",
            "Доступ на 1 счастливый месяц",
            "Доступ на 3 успешных месяца🔥",
            "Задать вопрос",
            placeholder="Что вас интересует?",
            sizes=(2, 2, 1)
        ),
    )
    #await message.answer_photo(photo)


# @user_private_router.message(F.text.lower() == "меню")
@user_private_router.message(or_f(Command("locations"), (F.text.lower().contains("локации"))))
async def locations_cmd(message: types.Message, session: AsyncSession):
#    for product in await orm_get_products(session):
#        await message.answer_photo(
#            product.image,
#            caption=f"<strong>{product.name}\
#                    </strong>\n{product.description}\nСтоимость: {round(product.price, 2)}",
#        )
    text = "локации:"
    await message.answer(text)


@user_private_router.message(F.text.lower() == "хочу в закрытый тг")
@user_private_router.message(Command("about"))
async def about_cmd(message: types.Message):
    text = """Совсем скоро весна и мы все начнем проводить съемки на улицах

В нашем тг-канале и на сайте тебя ждет более 100 стильных мест Екатеринбурга, в которых можно провести съемки прямо сейчас.

Все локации мы распределяем по удобным тегам для БЫСТРОГО поиска

И каждый месяц мы добавляем новые места (от парковок до ресторанов)

Ну и конечно везде мы пишем наши комментарии: сколько стоит аренда, как договориться, кому писать и так далее!

КНОПКА «доступ на 3 успешных месяца» + ссылка на оплату 3-ех месяцев

- _Подписка будет активна ровно 3 календарных месяца со дня оплаты в боте (или 1 месяц, в зависимости от тарифа). Например, если вы оплатили 15 февраля, следующее продление будет 15 мая по тарифу «3 успешных месяца» К этому моменту на канале уже появятся новые интересные локации для вас!_

- _За 1 день до окончания подписки наш бот вам напомнит о списании, поэтому не блокируйте нас_"""
    await message.answer(text, parse_mode='Markdown')


@user_private_router.message(F.text.lower() == "доступ на 1 счастливый месяц")
@user_private_router.message(Command("sub_month"))
async def subscriptions_cmd(message: types.Message, bot: Bot):
    text = """Для креаторов, smm-специалистов, блогеров, продюсеров и творческих экспертов

Более 150 локаций для проведения съемок
Информация по согласованию съемок на локации
Быстрый поиск локации по разделам #тегам
Новые локации каждый месяц
"""
    invoice = types.LabeledPrice(label='RUB', amount=10000)
    photo_path = r"images\\month.png"
    photo = types.FSInputFile(photo_path)
    
    await message.answer_photo(photo)
    await bot.send_invoice(
    message.chat.id,
    title="Доступ на месяц",
    description=text,
    provider_token=os.getenv('PAYMENTS_PROVIDER_TOKEN'),
    currency='RUB',
    #photo_url=TIME_MACHINE_IMAGE_URL,
    #photo_height=512,  # !=0/None, иначе изображение не покажется
    #photo_width=512,
    #photo_size=512,
    is_flexible=False,  # True если конечная цена зависит от способа доставки
    prices=[invoice],
    start_parameter='test',
    payload='your_custom_payload'
    )


@user_private_router.message(F.text.lower() == "доступ на 3 успешных месяца🔥")
@user_private_router.message(Command("sub_3_months"))
async def sub_3_months_cmd(message: types.Message, bot: Bot):
    text = "Совсем скоро весна и мы все начнем проводить съемки на улицах Екатеринбурга\n\n\
Именно поэтому тариф на 3 месяца просто маст хев для каждого креатора!"
    invoice = types.LabeledPrice(label='RUB', amount=10000)
    photo_path = r"images\\months.png"
    photo = types.FSInputFile(photo_path)
    
    await message.answer_photo(photo)
    await bot.send_invoice(
    message.chat.id,
    title="Доступ на месяц",
    description=text,
    provider_token=os.getenv('PAYMENTS_PROVIDER_TOKEN'),
    currency='RUB',
    #photo_url=TIME_MACHINE_IMAGE_URL,
    #photo_height=512,  # !=0/None, иначе изображение не покажется
    #photo_width=512,
    #photo_size=512,
    is_flexible=False,  # True если конечная цена зависит от способа доставки
    prices=[invoice],
    start_parameter='test',
    payload='your_custom_payload'
    )


@user_private_router.message(F.text.lower() == "задать вопрос")
@user_private_router.message(Command("questions"))
async def shipping_cmd(message: types.Message):
    text = "Контакты: @taglocation"
    await message.answer(text)



@user_private_router.pre_checkout_query()
async def pre_checkout_query_handler(query: types.PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(query.id, ok=True)

# @user_private_router.message(F.contact)
# async def get_contact(message: types.Message):
#     await message.answer(f"номер получен")
#     await message.answer(str(message.contact))


# @user_private_router.message(F.location)
# async def get_location(message: types.Message):
#     await message.answer(f"локация получена")
#     await message.answer(str(message.location))
