import time

from flask import Flask, render_template
import vk_api

from data import PASSWORD, LOGIN

app = Flask(__name__)


def auth_handler():
    """ При двухфакторной аутентификации вызывается эта функция. """

    # Код двухфакторной аутентификации,
    # который присылается по смс или уведомлением в мобильное приложение
    key = input("Enter authentication code: ")
    # Если: True - сохранить, False - не сохранять.
    remember_device = True

    return key, remember_device


def main():
    app.run()


@app.route('/vk_stat/<int:group_id>')
def vk_stats(group_id):
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

    vk = vk_session.get_api()

    my_stats = {
        'ages': {
            '12-18': 0,
            '18-21': 0,
            '21-24': 0,
            '24-27': 0,
            '27-30': 0,
            '30-35': 0,
            '35-45': 0,
            '45-100': 0,
        }
    }

    stats = vk.stats.get(group_id=group_id, stats_groups='reach', interval='week', intervals_count=1)
    for elem in stats[0]['reach']['age']:
        my_stats['ages'][elem['value']] = elem['count']
    print(stats[0])
    return render_template('stats.html', stats=stats[0], my_stats=my_stats)


if __name__ == '__main__':
    main()
