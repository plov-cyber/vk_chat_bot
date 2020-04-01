import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random

from data import TOKEN, group_id

m_codes = {
    1: 1,
    2: 4,
    3: 4,
    4: 0,
    5: 2,
    6: 5,
    7: 0,
    8: 3,
    9: 6,
    10: 1,
    11: 4,
    12: 6,
}
shift_codes = [6, 4, 2, 0]
week_days = {
    2: 'Понедельник',
    3: 'Вторник',
    4: 'Среда',
    5: 'Четверг',
    6: 'Пятница',
    0: 'Суббота',
    1: 'Воскресенье',
}


def main():
    vk_session = vk_api.VkApi(
        token=TOKEN)

    first = True
    longpoll = VkBotLongPoll(vk_session, group_id)

    for event in longpoll.listen():

        if event.type == VkBotEventType.MESSAGE_NEW:
            vk = vk_session.get_api()
            if first:
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message="Я могу сказать вам день недели в определённую дату.",
                                 random_id=random.randint(0, 2 ** 64))
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message="Введите дату в формате YYYY-MM-DD",
                                 random_id=random.randint(0, 2 ** 64))
                first = False
            else:
                try:
                    date = event.obj.message['text'].split('-')
                    year = int(date[0])
                    month = int(date[1])
                    day = int(date[2])
                    m_code = m_codes[month]
                    year_code = (shift_codes[abs(year // 100 - 20) % 4] + year % 100 + (year % 100) // 4) % 7
                    week_day = week_days[(day + m_code + year_code) % 7]
                    vk.messages.send(user_id=event.obj.message['from_id'],
                                     message=f"Отличная дата! День недели в эту дату - {week_day}",
                                     random_id=random.randint(0, 2 ** 64))
                    vk.messages.send(user_id=event.obj.message['from_id'],
                                     message=f"Вы можете ввести новую дату...",
                                     random_id=random.randint(0, 2 ** 64))
                except Exception:
                    vk.messages.send(user_id=event.obj.message['from_id'],
                                     message=f"Вы ввели дату в неверном формате либо такой даты не существует :(",
                                     random_id=random.randint(0, 2 ** 64))


if __name__ == '__main__':
    main()
