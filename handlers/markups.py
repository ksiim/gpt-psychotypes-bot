import asyncio

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

from bot import bot

from models.dbs.orm import Orm
from models.dbs.models import *

from .callbacks import *


waiting_text = "Принято, совсем скоро отвечу…"


async def generate_free_limit_updated_text():
    text = f"На ваш баланс зачислены бесплатные сообщения, в размере {await Orm.get_const('free_text_limit')} шт."
    return text

message_prompt_taken_message_text = "✅ Запрос принят. Генерирую изображение, это может занять 1-2 минуты..."

admin_panel_text = "Админ панель"
texts_text = "Тексты\n\nВыберите текст для изменения"
constants_text = "Константы\n\nВыберите константу для изменения"
psychotypes_settings_text = "Настройки психотипов. Выберите психотип для дальнейших настроек"
packages_settings_text = "Настройки пакетов. Выберите тип пакетов для настройки"

picture_packages_settings_text = "Нажмите для изменения настроек пакетов с картинками"
text_packages_settings_text = "Нажмите для изменения настроек пакетов с текстами"


packages_settings_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Текстовые",
                callback_data="text_packages_settings"
            ),
            InlineKeyboardButton(
                text="Картинки",
                callback_data="picture_packages_settings"
            )
        ],
    ]
)

confirmation_spam_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Да",
                callback_data="yes"
            ),
            InlineKeyboardButton(
                text="Нет",
                callback_data="no"
            )
        ]
    ]
)

admin_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Статистика",
                callback_data="stat"
            ),
            InlineKeyboardButton(
                text='Статистика психотипов',
                callback_data='psychotypes_stat'
            )
        ],
        [
            InlineKeyboardButton(
                text='Статистика всех функций',
                callback_data='func_stat'
            ),
        ],
        [
            InlineKeyboardButton(
                text="Рассылка",
                callback_data="spam"
            ),
            # InlineKeyboardButton(
            #     text="Рассылка бонусов",
            #     callback_data="bonus_spam"
            # )
        ],
        [
            # InlineKeyboardButton(
            #     text="Тексты",
            #     callback_data="texts"
            # ),
            InlineKeyboardButton(
                text="Константы",
                callback_data="constants"
            )
        ],
        [
            InlineKeyboardButton(
                text="Настройки психотипов",
                callback_data="psychotypes_settings"
            )
        ],
        [
            InlineKeyboardButton(
                text="Настройки пакетов",
                callback_data="packages_settings"
            )
        ],
        [
            InlineKeyboardButton(
                text="Добавить канал",
                callback_data="add_channel"
            ),
            InlineKeyboardButton(
                text="Удалить канал",
                callback_data="delete_channel"
            )
        ]
    ]
)


async def generate_delete_channels_markup():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=channel.name,
                    callback_data=f"dceletenel:{channel.id}"
                )
            ] for channel in await Orm.get_channels('bonus')
        ]
    )

bonus_spam_text = "Вы можете получить дополнительные генерации, подписавшись на каналы, указанные ниже\n\nПодписался, лови токены."


async def generate_bonus_markup():
    channels = await Orm.get_channels('bonus')
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=channel.name,
                    url=channel.url
                )
            ] for channel in channels
        ] + [[
            InlineKeyboardButton(
                text="Получить бонус",
                callback_data="get_bonus"
            )
        ]]
    )
    
async def send_bonus_message(telegram_id):
    await bot.send_message(
        chat_id=telegram_id,
        text=bonus_spam_text,
        reply_markup=await generate_bonus_markup()
    )

async def generate_func_statistic_text():
    func_statistic = await Orm.get_func_statistic()
    text = "Статистика функций\n\n"
    for function_name, count in func_statistic:
        text += f"{function_name}: {count}\n"
    return text


async def generate_psychotypes_settings_markup():
    psychotypes = await Orm.get_all_psychotypes()
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=psychotype.name,
                    callback_data=f"psychotype:{psychotype.id}"
                )
            ] for psychotype in psychotypes
        ] + [
            [InlineKeyboardButton(
                text="Добавить психотип",
                callback_data="add_psychotype"
            )]
        ]
    )


async def generate_text_packages_settings_markup():
    text_packages = await Orm.get_all_text_packages()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"{text_package.count} шт. || {text_package.price}₽",
                callback_data=f"sett_package:{text_package.id}"
            )] for text_package in text_packages
        ]
    )
    return keyboard


async def generate_package_settings_text(package_id):
    package = await Orm.get_package_by_id(int(package_id))
    return f"""Настройки пакета {'с текстами' if package.type_ == 'text' else 'с картинками'}

Количество: {package.count}
Цена: {package.price}"""


async def generate_buy_limits_markup():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Купить сообщения",
                    callback_data="buy_limits"
                )
            ]
        ]
    )


async def generate_buy_limits_by_type_markup(type_):
    packages = await Orm.get_all_packages_by_type(type_)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{package.count} шт. || {package.price}₽",
                    callback_data=f"bbbuy:{package.id}"
                )
            ] for package in packages
        ]
    )
    
async def generate_package_buy_text(package_id):
    package = await Orm.get_package_by_id(int(package_id))
    return f'Вы хотите купить {package.count} сообщений за {package.price}₽\n\nСовершите оплату по ссылке ниже, а затем нажмите на кнопку "Проверить"'


async def generate_payment_markup(payment_link, payment_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Оплатить",
                    url=payment_link,
                ),
                InlineKeyboardButton(
                    text="Проверить",
                    callback_data=f"cchecck:{payment_id}"
                )
            ]
        ]
    )

async def generate_package_settings_markup(package_id):
    package = await Orm.get_package_by_id(int(package_id))
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Изменить количество",
                    callback_data=f"pac_cp:count:{package.id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Изменить стоимость",
                    callback_data=f"pac_cp:price:{package.id}"
                )
            ]
        ]
    )


async def generate_picture_packages_settings_markup():
    picture_packages = await Orm.get_all_picture_packages()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"{picture_package.count} шт. || {picture_package.price}₽",
                callback_data=f"sett_package:{picture_package.id}"
            )] for picture_package in picture_packages
        ]
    )
    return keyboard


async def generate_current_psychotypes_text(user: User):
    if user.psychotype is None:
        return "У вас нет психотипа"
    return f"""Ваш текущий психотип: {user.psychotype.name}
Описание: {user.psychotype.description}

Выберите психотип для смены"""


async def generate_psychotype_settings_text(psychotype: Psychotype):
    return f"""Настройки психотипа

Психотип: {psychotype.name}
"""


async def generate_change_psychotype_markup(user: User):
    psychotypes = await Orm.get_all_psychotypes()
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=psychotype.name,
                    callback_data=f"change_psychotype:{psychotype.id}"
                )
            ] for psychotype in psychotypes
        ]
    )


async def generate_profile_text(user: User):
    free_text_limit_count = await Orm.get_const('free_text_limit')
    free_image_limit_count = await Orm.get_const('free_image_limit')
    return f"""Это ваш профиль
Имя: {user.full_name}
ID: {user.telegram_id}

Количество текстовых сообщений: {user.bought_text_limits_count if user.bought_text_limits_count else user.free_text_limits_count}
Количество изображений: {user.bought_image_limits_count if user.bought_image_limits_count else user.free_image_limits_count}
"""

confirm_reset_context_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Да",
                callback_data="resetcontext:yes"
            ),
            InlineKeyboardButton(
                text="Нет",
                callback_data="resetcontext:no"
            )
        ]
    ]
)

fuf_im_here_text = 'Фуф, я всё ещё здесь 🙂 и к твоим услугам 😉'


async def generate_edit_text_text(text: MessageText):
    return f"""Редактирование текста

Текст: {text.text}

Для редактирования текста отправьте мне новый текст"""


async def generate_edit_constant_text(constant: Const):
    return f"""Редактирование константы

Константа: {constant.name}
Значение: {constant.value}

Для редактирования значения отправьте мне новое значение"""


async def generate_psychotype_settings_markup(psychotype: Psychotype):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Изменить название",
                    callback_data=f"pt:change_name:{psychotype.id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Изменить описание",
                    callback_data=f"pt:change_description:{psychotype.id}"
                ),
                InlineKeyboardButton(
                    text="Изменить промпт",
                    callback_data=f"pt:change_prompt:{psychotype.id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Удалить психотип",
                    callback_data=f"pt:delete:{psychotype.id}"
                )
            ]
        ]
    )


async def generate_constants_markup():
    constants = await Orm.get_all_constants()
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=constant.name,
                    callback_data=f"constant:{constant.id}"
                )
            ] for constant in constants
        ]
    )


async def generate_texts_markup():
    texts = await Orm.get_all_texts()
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=text.name_en,
                    callback_data=f"text:{text.id}"
                )
            ] for text in texts
        ]
    )


async def generate_payment_keyboard(payment_link: str, payment_id: str, type_='rate'):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Оплатить",
                    url=payment_link,
                ),
                InlineKeyboardButton(
                    text="Проверить оплату",
                    callback_data=f"check_payment:{type_}:{payment_id}"
                )
            ]
        ]
    )


async def get_count_of_requests(model: str, user: User):
    count_of_requests = await Orm.get_count_of_requests(model, telegram_id=user.telegram_id)
    return count_of_requests


async def generate_current_models_text(user: User):
    return f"""
ChatGPT-4o:

🌟 Полноценная версия GPT-4, предоставляющая высокую точность в генерации ответов
🧠 Идеальна для сложных текстовых задач

ChatGPT-4o mini:

🎯 Подходит для простых задач, где не требуется высокая вычислительная мощность или сложная аналитика
    """


async def generate_psychotypes_statistic_text():
    psychotypes_statistic = await Orm.get_psychotypes_statistic()
    text = "Статистика психотипов\n\n"
    for psychotype in psychotypes_statistic:
        text += f"{psychotype.name.capitalize()}: {psychotype.count_of_usage} ({f'+{psychotype.statistics}' if psychotype.statistics >= 0 else psychotype.statistics})\n"
    return text


async def generate_statistic_text():
    yesterday, today, all_users_count, online_count = await asyncio.gather(
        Orm.get_yesterday_count(),
        Orm.get_today_count(),
        Orm.get_all_users_count(),
        Orm.get_online_count(),
    )

    try:
        diff = int((today / yesterday - 1) * 100)
    except ZeroDivisionError:
        diff = 0

    arrow_text = f"↑{diff}%" if diff >= 0 else f"↓{diff}%"
    return f"""📈 Статистика

✅ Сегодня в бота пришло {today} чел. ({arrow_text})
✅ Вчера в бота пришло {yesterday} чел.

🔥 Всего пользователей: {all_users_count}

👉 онлайн {online_count}
"""


async def generate_start_text(message):
    return f"""Приветствую тебя, {message.from_user.full_name}! 🎉

Я - Telegram бот ChatGPT + DALL-E, и я здесь, чтобы помочь тебе! Я могу создавать уникальные изображения по твоим сообщениям, генерировать текст, соответствующий твоим предпочтениям, а также улучшать и придавать креативность твоему тексту, делая его более интересным.

Не стесняйся задавать мне любые вопросы, просто напиши, и я с радостью помогу! 😉  
Чтобы узнать подробнее о моих возможностях, просто напиши /help"""

get_image_description_text = "Опиши изображение которое нужно сгенерировать:"

back_to_menu_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text="Назад",
            callback_data="back_to_menu"
        )]
    ]
)


help_text = """
Этот бот предоставляет тебе доступ к передовым нейросетям, таким как ChatGPT и DALL-E, для создания текста и изображений.

Я могу стать для тебя кем угодно: учёным, юмористом, консерватором, поэтом, философом, программистом или заботливым другом. Просто выбери в меню, каким именно я должен стать.

Вот что я умею:

1. Отвечаю на вопросы: 
   Предоставляю информацию по самым различным темам — от науки до истории и технологий.

2. Помогаю с учебой: 
   Объясняю сложные концепции, решаю задачи и помогаю с написанием эссе.

3. Создаю и редактирую тексты: 
   Помогаю в написании текстов, проверяю грамматику и стилистику. Это могут быть пожелания на открытке, публикации для соцсетей, инструкции или поэтические произведения.

4. Даю советы 🙂и рекомендации: 
   Помогаю в ответах на вопросы в диалоге с конкретными людьми, консультирую по повседневным вопросам, таким как планирование, продуктивность или общение.

5. Развлекаю: 
   Рассказываю шутки, истории и предоставляю краткие описания книг и фильмов.

Если у тебя есть конкретные вопросы или задачи, не скромничай — обращайся!

✍️ Для текстового ответа просто напишите свой вопрос в чат.

🌅 Для создания изображения с DALL-E в меню выберете команду /dalle, далее опишите картинку, которую хочешь видеть (например — кот в сапогах).

🔄 Чтобы очистить контекст диалога, используйте команду /reset — я забуду всё, о чем мы говорили.

Команды:
- /start — Узнать о возможностях чат-бота
- /profile — Просмотреть профиль пользователя
- /packages — Купить пакеты запросов
- /reset — Сбросить контекст
- /psychotype — Выбрать психотип
- /dalle — Создать изображение
- /help — Получить помощь
"""

close_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Закрыть", callback_data="close")
        ]
    ]
)

buy_premium_text = "Чтобы отправлять сообщения ChatGPT-4o нужно оформить подписку Plus или PRO по команде /premium"


async def generate_model_markup(user: User):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅" + e.value if user.chat_model.value == e.value else "" + e.value,
                    callback_data=f"change_to:{e.name}"
                )
            ] for e in ChatModelEnum
        ]
    )
    
like_dislike_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="👍",
                callback_data="like"
            ),
            InlineKeyboardButton(
                text="👎",
                callback_data="dislike"
            )
        ]
    ]
)

dislike_reply_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Добавь к ответу креатива")
        ],
        [
            KeyboardButton(text="Добавь к ответу юмора")
        ],
        [
            KeyboardButton(text="Добавь к ответу консерватизма")
        ],
        [
            KeyboardButton(text="Добавь к ответу философии")
        ],
        [
            KeyboardButton(text="Добавь к ответу легкомысленности")
        ]
    ],
    one_time_keyboard=True,
    resize_keyboard=True
)


choose_type_of_package_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Текстовые",
                callback_data="pacccckages:text"
            ),
            InlineKeyboardButton(
                text="Изображения",
                callback_data="pacccckages:picture"
            )
        ]
    ]
)