import os

import requests
import vk_api
import json
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random

from data import TOKEN, group_id, PASSWORD, LOGIN

keyboard = {
    'one_time': True,
    'buttons': [[
        {
            'color': 'secondary',
            'action': {
                'type': 'text',
                'label': 'Спутник'
            }
        },
        {
            'color': 'secondary',
            'action': {
                'type': 'text',
                'label': 'Схема'
            }
        },
        {
            'color': 'secondary',
            'action': {
                'type': 'text',
                'label': 'Гибрид'
            }
        }
    ]],
    'inline': False
}

map_types = {
    'Схема': 'map',
    'Гибрид': 'sat,skl',
    'Спутник': 'sat',
}


def auth_handler():
    """ При двухфакторной аутентификации вызывается эта функция. """

    # Код двухфакторной аутентификации,
    # который присылается по смс или уведомлением в мобильное приложение
    key = input("Enter authentication code: ")
    # Если: True - сохранить, False - не сохранять.
    remember_device = True

    return key, remember_device


def login():
    login, password = LOGIN, PASSWORD
    vk_session = vk_api.VkApi(
        login, password,
        auth_handler=auth_handler
    )

    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    return vk_session


def get_photo_id(filename, vk_session):
    upload = vk_api.VkUpload(vk_session)
    photo = upload.photo_messages([filename])
    print(photo)
    vk_photo_id = f"photo{photo[0]['owner_id']}_{photo[0]['id']}_{photo[0]['access_key']}"
    return vk_photo_id


def main():
    user_session = login()
    vk_session = vk_api.VkApi(
        token=TOKEN)

    geo_server = "http://geocode-maps.yandex.ru/1.x/"
    map_server = "http://static-maps.yandex.ru/1.x/"
    first = True
    coordinates = None
    address = None

    longpoll = VkBotLongPoll(vk_session, group_id)

    for event in longpoll.listen():

        if event.type == VkBotEventType.MESSAGE_NEW:
            print(event)
            vk = vk_session.get_api()
            if first:
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message="Введите местность, которую вы хотели бы увидеть:",
                                 random_id=random.randint(0, 2 ** 64))
                first = False
            else:
                msg = event.obj.message
                try:
                    if msg['text'] in ['Схема', 'Спутник', 'Гибрид']:
                        map_params = {
                            'll': coordinates,
                            'l': map_types[msg['text']],
                            'z': '13'
                        }
                        response = requests.get(map_server, params=map_params)
                        if not response:
                            vk.messages.send(user_id=msg['from_id'],
                                             message="Произошла ошибка при отображении адреса!",
                                             random_id=random.randint(0, 2 ** 64))
                            continue
                        map_file = "map.png"
                        with open(map_file, "wb") as file:
                            file.write(response.content)
                        photo_id = get_photo_id('map.png', user_session)
                        os.remove('map.png')
                        vk.messages.send(user_id=msg['from_id'],
                                         message=f"Это {address}. Что вы еще хотите увидеть?",
                                         random_id=random.randint(0, 2 ** 64))
                        vk.messages.send(user_id=msg['from_id'],
                                         attachment=photo_id,
                                         random_id=random.randint(0, 2 ** 64))
                    else:
                        address = msg['text']
                        geo_params = {
                            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
                            "geocode": address,
                            "format": "json"
                        }
                        response = requests.get(geo_server, params=geo_params)
                        if not response:
                            vk.messages.send(user_id=msg['from_id'],
                                             message="Произошла ошибка при определении координат!",
                                             random_id=random.randint(0, 2 ** 64))
                            continue
                        response = response.json()
                        if response["response"]["GeoObjectCollection"]["featureMember"]:
                            toponym = response["response"]["GeoObjectCollection"][
                                "featureMember"][0]["GeoObject"]
                            coordinates = ','.join(toponym['Point']['pos'].split())
                            vk.messages.send(user_id=msg['from_id'],
                                             message="Выберите тип карты",
                                             random_id=random.randint(0, 2 ** 64),
                                             keyboard=json.dumps(keyboard))
                        else:
                            vk.messages.send(user_id=msg['from_id'],
                                             message="По вашему запросу ничего не найдено!",
                                             random_id=random.randint(0, 2 ** 64))
                            vk.messages.send(user_id=msg['from_id'],
                                             message="Введите новый адрес:",
                                             random_id=random.randint(0, 2 ** 64))
                except Exception as e:
                    print(e)
                    vk.messages.send(user_id=msg['from_id'],
                                     message="Произошла непредвиденная ошибка!",
                                     random_id=random.randint(0, 2 ** 64))


if __name__ == '__main__':
    main()
