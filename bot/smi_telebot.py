# Спасибо за пример кода для бота Анне Сакоян!

from __future__ import unicode_literals

from telegram.ext import Updater, CommandHandler  # Библиотека python-telegram-bot для работы с API Телеграма

import bot_token  # файл, в котором содержится токен бота, полученный при его регистрации
import cs_media_contracts  # импорт модуля для работы с API "Госзатрат"


# ПОЛЯ, В КОТОРЫХ СОДЕРЖАТСЯ НУЖНЫЕ ДАННЫЕ
CONTRACT_URL = 'contract_url'  # URL карточки контракта на "Госзатратах"
CONTRACT_PRICE = 'contract_price'  # Общая сумма контракта
PRODUCT_DESCRIPTION = 'product_description'  # Описание конкретного продукта
PRODUCT_PRICE = 'product_price'  # Сумма по позиции конкретного продукта
NUM_PRODUCTS = 'num_products'  # Число продуктов в контракте


TOKEN = bot_token.BOT_TOKEN  # Токен телеграм-бота


def start(bot, update):
    '''
    Определение функции для команды /start
    Отправляет через API бота текст справки.
    '''
    text = u'Это бот для поиска среди контрактов указанного поставщика тех, которые связаны со сферой СМИ.\n' \
           'Для запроса вам потребуется ИНН интересующего вас поставщика.\n' \
           '- /inn [ИНН поставщика] - ищет, заключенные с этим поставщиком, в которых ' \
           'содержится хотя бы один предмет, имеющий отношение к СМИ, и выдает информацию об этом предмете.\n' \
           'Бот показывает до 10 последних контрактов, имеющих отношение к СМИ.'
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text=text)


def write_response(data):
    '''
    Сформировать отчет о полученных данных по контрактам поставщика.
    Данные формируются функцией s_media_contracts.get_contracts_by_inn
    и представляют собой tuple в формате:
    (НАЗВАНИЕ_ПОСТАВЩИКА, ЧИСЛО_ЕГО_КОНТРАКТОВ, СПИСОК_СЛОВАРЕЙ_ПО_РЕЛЕВАНТНЫМ_КОНТРАКТАМ)
    Возвращает текст отчета.
    '''
    supplier_name = data[0]
    total = data[1]
    media_contracts = data[2]

    text = u'Поставщик: {}\n'.format(supplier_name)
    text += u'Всего контрактов: {}.\n'.format(total)
    text += u'Вот {} из последних, имеющих отношение к СМИ.\n'.format(len(media_contracts))
    if len(media_contracts):
        text += u'\n'
        text += u'Предметы, имеющие отношение к СМИ: \n'
        for contract in media_contracts:
            text += u'\n'
            text += u'URL контракта: {}\n'.format(contract[CONTRACT_URL])
            text += u'- общая сумма: {}\n'.format(contract[CONTRACT_PRICE])
            text += u'- всего предметов: {}\n'.format(contract[NUM_PRODUCTS])
            text += u'- в том числе: {}\n'.format(contract[PRODUCT_DESCRIPTION])
            text += u'- по цене: {}\n'.format(contract[PRODUCT_PRICE])
    return text


def inn(bot, update):
    '''
    Обработать команду /inn ИНН_ПОСТАВЩИКА
    Сформировать и отправить пользователю ответ.
    '''
    query = update['message']['text']  # Получить команду
    target_inn = query.split(' ')  # Преобразовать команду из строки в список
    if len(target_inn) < 2:
        # Если в списке только 1 элемент, значит пользователь не ввел ИНН
        reply = u'Укажите ИНН. Например: /inn 7826159654'
    else:
        target_inn = target_inn[1].strip()  # ИНН, указанный в команде
        # print(target_inn)
        result = cs_media_contracts.get_contracts_by_inn(target_inn)  # Запустить фильтрацию данных по ИНН
        # Если запрос прошел успешно, то его результат представлен в виде tuple.
        if type(result) is not tuple:
            # Если результат не tuple, значит ответом будет уведомление о том, что получить искомое не удалось
            reply = result
        else:
            # Если все в порядке, то преобразуем данные в отчет
            reply = write_response(result)
    # Отправляем ответ
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text=reply)



if __name__ == '__main__':
    # Регистрация команд и запуск бота
    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    inn_handler = CommandHandler('inn', inn)
    help_handler = CommandHandler('help', start)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(inn_handler)
    dispatcher.add_handler(help_handler)
    updater.start_polling()
