import vk_api
import numpy as np
from collections import Counter
import json
from config import *


vk_session = vk_api.VkApi(VK_EMAIL, VK_PASSWORD, api_version='5.126')
try:
    vk_session.auth()
except vk_api.AuthError as error_msg:
    print(error_msg)

vk = vk_session.get_api()


def get_ids_like(user_id: int, item_id: int, type: str = "photo", filter: str = "likes", friends_only: (0, 1) =0) -> list:
    """
    Возврачает id-ползователей котоые поставили Like у ползователя(user_id) на объекте(item_id)
    :param user_id: идентификатор владельца Like-объекта: id пользователя, id сообщества (со знаком «минус»)
    или id приложения. Если параметр type равен sitepage, то в качестве owner_id необходимо передавать id приложения.
    Если параметр не задан, то считается, что он равен либо идентификатору текущего пользователя,
    либо идентификатору текущего приложения (если type равен sitepage).
    :param item_id: идентификатор Like-объекта. Если type равен sitepage, то параметр item_id может содержать
    значение параметра page_id, используемый при инициализации
    :param type: тип объекта
    :param filter: указывает, следует ли вернуть всех пользователей, добавивших объект в список "Мне нравится"
    или только тех, которые рассказали о нем друзьям. Параметр может принимать следующие значения:
        likes — возвращать информацию обо всех пользователях;
        copies — возвращать информацию только о пользователях, рассказавших об объекте друзьям.
    По умолчанию возвращается информация обо всех пользователях.
    :param friends_only: указывает, необходимо ли возвращать только пользователей,
    которые являются друзьями текущего пользователя. Параметр может принимать следующие значения:
        0 — возвращать всех пользователей в порядке убывания времени добавления объекта;
        1 — возвращать только друзей текущего пользователя в порядке убывания времени добавления объекта;
    Если метод был вызван без авторизации или параметр не был задан, то считается, что он равен 0.
    :return: Список id-ползователей поставивших лайк
    """

    id_users = []   # id-ползователей поставивших лайк
    likes = vk.likes.getList(
        type=type,
        owner_id=user_id,
        item_id=item_id,
        filter=filter,
        friends_only=friends_only,
        extended=0,
        offset=0,
        count=1000)
    count_likes = likes['count']
    id_users.extend(likes["items"])
    count_step = count_likes // 1000    # Количество шогов для прохождение по всем лайкнувшим пользователям
    if count_step > 0:
        for i in range(count_step):    # Max 1000
            likes = vk.likes.getList(type="photo",
                                     owner_id=user_id,
                                     item_id=item_id,
                                     filter="likes",
                                     friends_only=0,
                                     extended=0,
                                     offset=(1000+i*1000),
                                     count=1000)
            id_users.extend(likes["items"])
    return id_users


def get_photos_ids(user_id: int, no_service_albums: (0, 1) = 0, skip_hidden: (0, 1) = 0) -> list:
    """
    Возвращает идинтефекатор всех фотографии у ползователя user_id
    :param user_id: идентификатор пользователя или сообщества, фотографии которого нужно получить.
    :param no_service_albums: 0 — вернуть все фотографии, включая находящиеся в сервисных альбомах,
    таких как "Фотографии на моей стене" (по умолчанию);
        1 — вернуть фотографии только из стандартных альбомов пользователя или сообщества.
    :param skip_hidden: 1 — не возвращать фотографии, скрытые из блока над стеной пользователя
     (параметр учитывается только при owner_id > 0, параметр no_service_albums игнорируется).
    :return: Список идинтефекаторов фотографии
    """
    id_photos = []
    photos = vk.photos.getAll(owner_id=user_id, extended=0, offset=0, count=200,
                              no_service_albums=no_service_albums, need_hidden=0, skip_hidden=skip_hidden)
    count_photos = photos['count']
    id_photos.extend(photo[id] for photo in photos['items'])
    count_step = count_photos//200
    if count_step > 0:
        for i in range(count_step):    # Max 1000
            photos = vk.photos.getAll(owner_id=user_id, extended=0, offset=(200+i*200), count=200,
                                      no_service_albums=no_service_albums, need_hidden=0, skip_hidden=skip_hidden)
            id_photos.extend(photo[id] for photo in photos['items'])
    return id_photos


def get_all_ids_like(user_id: int, no_service_albums: (0, 1) = 0, skip_hidden: (0, 1) = 0) -> Counter:
    """
    Возвращает все идентефекаторы ползователей лайкнувших фотографии у ползователя user_id
    :param user_id: идентификатор пользователя или сообщества, фотографии которого нужно получить.
    :param type: тип объекта
    :param no_service_albums: 0 — вернуть все фотографии, включая находящиеся в сервисных альбомах,
    таких как "Фотографии на моей стене" (по умолчанию);
        1 — вернуть фотографии только из стандартных альбомов пользователя или сообщества.
    :param skip_hidden: 1 — не возвращать фотографии, скрытые из блока над стеной пользователя
     (параметр учитывается только при owner_id > 0, параметр no_service_albums игнорируется).
    :return: Список идинтефекаторов пользователей
    """

    id_all_likes = []
    photos = vk.photos.getAll(owner_id=user_id, extended=0, offset=0, count=200,
                              no_service_albums=no_service_albums, need_hidden=0, skip_hidden=skip_hidden)
    count_photos = photos['count']
    id_all_likes.extend(get_ids_like(user_id=user_id, item_id=photo['id']) for photo in photos['items'])
    count_step = count_photos//200
    if count_step > 0:
        for i in range(count_step):    # Max 1000
            photos = vk.photos.getAll(owner_id=user_id, extended=0, offset=(200+i*200), count=200,
                                      no_service_albums=0, need_hidden=0, skip_hidden=0)
            id_all_likes.extend(get_ids_like(user_id=user_id, item_id=photo['id']) for photo in photos['items'])
    return Counter(i for j in id_all_likes for i in j)


def get_trend_like(user_id: int, top: int = 10,) -> list:
    """
    Вовращает список людей поставивших несколько лайков у user_id
    :param user_id: id-ползователя у которого фото
    :param top: возврвщает самых самых
    :return: список котежей
    """

    users_like = []
    data_like = get_all_ids_like(user_id=user_id,).most_common(top)
    for user_id, count in data_like:
        user = vk.users.get(user_ids=user_id)[0]
        users_like.append(tuple(('https://vk.com/id'+str(user['id']),
                                 user['id'],
                                 (user['first_name'] + ' ' + user['last_name']),
                                 count)))

    return users_like


print(get_trend_like(226368442, 25))
