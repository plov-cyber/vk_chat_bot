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

    stats = vk.stats.get(group_id=group_id, stats_groups='reach')
    return render_template('stats.html', stats=stats)


if __name__ == '__main__':
    main()
