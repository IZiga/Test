import apiai    # Для работы с DiologFlow
import telebot  # Для работы с телеграм Ботом
from telebot import types
import config   # FIXME
import json
import logging  # Для логов
import requests
import vector_fun



file_logg = "app.log"
dir_theory = 'Theory'
dir_vector = dir_theory + '/Vector/'
message_history = {}  # {chat_id: [(message_id, message), (message_id, message)]}
data_flag = {}


def communication_message(message: str) -> str:
    """
    Отвещает на сообщение, ответ продумывает через Dialogflow
    :param message: Сообщение, на которое требуется ответ
    :return: Ответ на сообщение
    """
    request = apiai.ApiAI('ec8ae2d24ad54ae7bb0da15c61d9c5c6').text_request()
    prog_logger.debug(request)
    request.lang = 'ru'
    request.session_id = 'session_1'
    request.query = message
    prog_logger.debug(request)
    response = json.loads(request.getresponse().read().decode('utf-8'))
    action = response['result']['action']
    speech = response['result']['fulfillment']['speech'] if action else "я тебя не понимаю"     # Ответ на сообщение
    prog_logger.debug(speech)
    return speech


# ----- Для Логов --------------------------------------------------------------------|
prog_logger = logging.getLogger("program")   # Имя логов
prog_logger.setLevel(logging.INFO)   # Уровень логирование
bot_logger = logging.getLogger("bot")
bot_logger.setLevel(logging.INFO)
user_logger = logging.getLogger("user")
user_logger.setLevel(logging.INFO)
fh = logging.FileHandler(file_logg, mode='w')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

prog_logger.addHandler(fh)
prog_logger.info("Program started")
bot_logger.addHandler(fh)
user_logger.addHandler(fh)
# --------------------------------------------------------------------------------------|

bot = telebot.TeleBot(config.TOKEN)






@bot.message_handler(commands=['start'])    # Реакции на сообытия при полущении команды /start
def welcome(event):
    user_name = event.chat.first_name
    chat_id = event.chat.id
    message = event.text
    del_flag(chat_id)
    message_bot = 'Здравствуй выбири что надо и пошли дальше'  # Сообщения бота
    keyboard = types.InlineKeyboardMarkup()
    key_zad = types.InlineKeyboardButton(text='⌨️ Калькулятор', callback_data='calculator')
    keyboard.add(key_zad)
    key_theory = types.InlineKeyboardButton(text='📚 Теория', callback_data='theory')
    keyboard.add(key_theory)
    bot_logger.info(f'to {user_name}: ({id}): {message_bot}')
    bot.send_message(chat_id, message_bot, reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def func1(event):
    # ms_json = event.json
    # print(json.dumps(ms_json, indent=2))
    user_name = event.chat.first_name
    chat_id = event.chat.id
    message = event.text
    if have_flag(chat_id, 'calc_angle_3D'):
        res, file_name = vector_fun.calc_angel_3D(message)
        message_bot =f'Угол равен {res}°'
        photo = open(file_name, 'rb')
        bot.send_photo(chat_id, photo, caption=message_bot)
        del_flag(chat_id)
    message_bot = communication_message(message)  # Сообщения бота
    user_logger.info(f'{user_name}: ({chat_id}): {message}')
    bot_logger.info(f'to {user_name}: ({chat_id}): {message_bot}')
    try:
        message_history[chat_id].append((event.id, message))
    except KeyError:
        message_history[chat_id] = [(event.id, message)]
    bot.send_message(event.chat.id, message_bot)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):  # Если нажали на одну из кнопок
    event = call.message
    user_name = event.chat.first_name
    chat_id = event.chat.id
    message = call.data
    user_logger.info(f'{user_name}: ({id}): {message}')
    del_flag(chat_id)

    # ----------------------------------------Калькулятор---------------------------------------------------------------
    if call.data == 'calculator':
        keyboard_calculator = types.InlineKeyboardMarkup()
        key_calc_angle_3D = types.InlineKeyboardButton(text='Угол между векторами в 3D', callback_data='calc_angle_3D')
        keyboard_calculator.add(key_calc_angle_3D)
        message_bot = 'Пока выбор не большой:'  # Сообщения бота
        bot_logger.info(f'to {user_name}: ({id}): {message_bot}')
        bot.send_message(chat_id, message_bot, reply_markup=keyboard_calculator)

    if call.data == 'calc_angle_3D':
        add_flag(chat_id, message)
        message_bot = 'Вычисляет угол между векторами. Вектора записывать a=(1,3,4) b=(5,6,7) и тогда будет ЗБС.' \
                      'По другому не настроен'  # Сообщения бота
        bot.send_message(chat_id, message_bot)

    # ------------------------------------------------------------------------------------------------------------------

    # ----------------------------------------Теория--------------------------------------------------------------------
    if call.data == 'theory':
        keyboard_theory = types.InlineKeyboardMarkup()
        # Vector
        key_vector = types.InlineKeyboardButton(text='Вектора', callback_data='Vector')
        keyboard_theory.add(key_vector)
        # Complex_number
        key_сomplex_num = types.InlineKeyboardButton(text='Комплексные числа', callback_data='сomplex_num')
        keyboard_theory.add(key_сomplex_num)

        key_ = types.InlineKeyboardButton(text='......', callback_data='_')
        keyboard_theory.add(key_)
        message_bot = 'Это теории:'  # Сообщения бота
        bot_logger.info(f'to {user_name}: ({id}): {message_bot}')
        bot.send_message(chat_id, message_bot, reply_markup=keyboard_theory)

    # ********************************************* Теория о векторах **************************************************
    if call.data == 'Vector':
        keyboard_vector = types.InlineKeyboardMarkup()
        key_base = types.InlineKeyboardButton(text='Вектор', callback_data='base_vector')
        keyboard_vector.add(key_base)
        key_direction_vector = types.InlineKeyboardButton(text='Определение направляющих косинусов', callback_data='direction_vector')
        keyboard_vector.add(key_direction_vector)
        key_orthogonal = types.InlineKeyboardButton(text='Ортогональность векторов ', callback_data='orthogonal')
        keyboard_vector.add(key_orthogonal)
        key_collinear = types.InlineKeyboardButton(text='Коллинеарность векторов', callback_data='collinear')
        keyboard_vector.add(key_collinear)
        key_coplanar = types.InlineKeyboardButton(text='Компланарность векторов', callback_data='coplanar')
        keyboard_vector.add(key_coplanar)
        key_angle = types.InlineKeyboardButton(text='Угол между векторами', callback_data='angle')
        keyboard_vector.add(key_angle)
        key_projection = types.InlineKeyboardButton(text='Проекция вектора', callback_data='projection')
        keyboard_vector.add(key_projection)
        key_scalar_product = types.InlineKeyboardButton(text='Скалярное произведение векторов', callback_data='scalar_product')
        keyboard_vector.add(key_scalar_product)
        key_vector_product = types.InlineKeyboardButton(text='Векторное произведение векторов', callback_data='vector_product')
        keyboard_vector.add(key_vector_product)
        key_mixed_product = types.InlineKeyboardButton(text='Смешанное произведение векторов', callback_data='mixed_product')
        keyboard_vector.add(key_mixed_product)
        key_linearly_vectors = types.InlineKeyboardButton(text='Линейно зависимые и линейно независимые вектора', callback_data='linearly_vectors')
        keyboard_vector.add(key_linearly_vectors)
        key_decomposition = types.InlineKeyboardButton(text='Разложение вектора по базису', callback_data='decomposition')
        keyboard_vector.add(key_decomposition)
        message_bot = 'В физике и математике вектор - это величина, которая характеризуется своим численным значением и направлением.В геометрии вектором называется любой направленный отрезок. Графически вектора изображаются в виде направленных отрезков прямой определенной длины.'
        bot_logger.info(f'to {user_name}: ({id}): {message_bot}')
        bot.send_message(chat_id, message_bot, reply_markup=keyboard_vector)
    if call.data == 'base_vector':
        photos = []
        photos.append(types.InputMediaPhoto(open(dir_vector + 'Определение_вектора.png', 'rb')))
        photos.append(types.InputMediaPhoto(open(dir_vector + 'Длина_вектора.png', 'rb')))
        photos.append(types.InputMediaPhoto(open(dir_vector + 'Коллинеарные_вектора.png', 'rb')))
        photos.append(types.InputMediaPhoto(open(dir_vector + 'Компланарные_вектора.png', 'rb')))
        photos.append(types.InputMediaPhoto(open(dir_vector + 'Направленость_вектора.png', 'rb')))
        photos.append(types.InputMediaPhoto(open(dir_vector + 'Нулевой_вектор.png', 'rb')))
        photos.append(types.InputMediaPhoto(open(dir_vector + 'Равный_вектор.png', 'rb')))
        bot.send_media_group(chat_id, photos)
    if call.data == 'direction_vector':
        photos = []
        photos.append(types.InputMediaPhoto(open(dir_vector + 'Определение_направляющих_косинусов.png', 'rb')))
        photos.append(types.InputMediaPhoto(open(dir_vector + 'Формула_направляющих_косинусов.png', 'rb')))
        bot.send_media_group(chat_id, photos)
    if call.data == 'orthogonal':
        photos = []
        photos.append(types.InputMediaPhoto(open(dir_vector + 'Ортогональность.png', 'rb'), ))
        bot.send_media_group(chat_id, photos)
    if call.data == 'collinear':
        photos = []
        photos.append(types.InputMediaPhoto(open(dir_vector + 'Коллинеарность.png', 'rb')))
        bot.send_media_group(chat_id, photos)
    if call.data == 'coplanar':
        photos = []
        photos.append(types.InputMediaPhoto(open(dir_vector + 'Компланарность.png', 'rb')))
        bot.send_media_group(chat_id, photos)
    if call.data == 'angle':
        photos = []
        photos.append(types.InputMediaPhoto(open(dir_vector + 'Угол между векторами.png', 'rb')))
        bot.send_media_group(chat_id, photos)
    if call.data == 'projection':
        photos = []
        photos.append(types.InputMediaPhoto(open(dir_vector + 'проекция вектора.png', 'rb')))
        bot.send_media_group(chat_id, photos)
    if call.data == 'scalar_product':
        photos = []
        photos.append(types.InputMediaPhoto(open(dir_vector + 'Скалярное произведение-1.png', 'rb')))
        photos.append(types.InputMediaPhoto(open(dir_vector + 'Скалярное произведение-2.png', 'rb')))
        bot.send_media_group(chat_id, photos)
    if call.data == 'vector_product':
        photos = []
        photos.append(types.InputMediaPhoto(open(dir_vector + 'Векторное произведение-1.png', 'rb')))
        photos.append(types.InputMediaPhoto(open(dir_vector + 'Векторное произведение-2.png', 'rb')))
        bot.send_media_group(chat_id, photos)
    if call.data == 'mixed_product':
        photos = []
        photos.append(types.InputMediaPhoto(open(dir_vector + 'Смешанное произведение-1.png', 'rb')))
        photos.append(types.InputMediaPhoto(open(dir_vector + 'Смешанное произведение-2.png', 'rb')))
        bot.send_media_group(chat_id, photos)
    if call.data == 'linearly_vectors':
        photos = []
        photos.append(types.InputMediaPhoto(open(dir_vector + 'Линейные вектора.png', 'rb')))
        bot.send_media_group(chat_id, photos)
    if call.data == 'decomposition':
        photos = []
        photos.append(types.InputMediaPhoto(open(dir_vector + 'Разложения по базису.png', 'rb')))
        photos.append(types.InputMediaPhoto(open(dir_vector + 'Разложения по базису-1.png', 'rb')))
        bot.send_media_group(chat_id, photos)
    # ******************************************************************************************************************

    # ********************************************* Комплексные числа **************************************************
    if call.data == 'сomplex_num':
        keyboard_сomplex_num = types.InlineKeyboardMarkup()
        key_base = types.InlineKeyboardButton(text='Комплексные числа', callback_data='сomplex_base')
        keyboard_сomplex_num.add(key_base)
        key_geometric_complex = types.InlineKeyboardButton(text='Геометрическое представления комплексных чисел', callback_data='geometric_complex')
        keyboard_сomplex_num.add(key_geometric_complex)
        key_actions_complex = types.InlineKeyboardButton(text='действия с комплексными числами', callback_data='actions_complex')
        keyboard_сomplex_num.add(key_actions_complex)
        key_complex_tfn_efn = types.InlineKeyboardButton(text='Комплексные числа тригонометрической и показательной формах записи', callback_data='complex_tfn_efn')
        keyboard_сomplex_num.add(key_complex_tfn_efn)
        message_bot = 'Выбери из списка'
        bot_logger.info(f'to {user_name}: ({id}): {message_bot}')
        bot.send_message(chat_id, message_bot, reply_markup=keyboard_сomplex_num)
    if call.data == 'сomplex_base':
        message_bot = 'https://telegra.ph/Kompleksnoe-chislo-02-07'
        bot.send_message(chat_id, message_bot,)
    if call.data == 'geometric_complex':
        message_bot = 'https://telegra.ph/Geometricheskoe-predstavleniya-kompleksnyh-chisel-02-08'
        bot.send_message(chat_id, message_bot,)
    if call.data == 'actions_complex':
        message_bot = 'https://telegra.ph/Dejstvie-s-kompleksnymi-chislami-02-08'
        bot.send_message(chat_id, message_bot,)
    if call.data == 'complex_tfn_efn':
        message_bot = 'https://telegra.ph/Kompleksnye-chisla-v-trigonometricheskoj-i-pokazatelnoj-forme-zapisi-02-08'
        bot.send_message(chat_id, message_bot,)


def add_flag(user_id, flag: str):
    data_flag[user_id] = flag


def have_flag(user_id, flag: str):
    return data_flag.get(user_id) == flag


def del_flag(chat_id):
    data_flag.pop(chat_id, None)


try:
    # RUN
    bot.polling(none_stop=True)
except requests.exceptions.ReadTimeout as e:
    prog_logger.error(e)








