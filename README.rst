HedgehogBot
===========

HedgehogBot - это бот для Telegramm, созданный для практики и для любования ежиками. Вы же любите ежиков???

Установка.
----------
Создайте вирутальное окружение и активируйте его. Далее, выполните в виртуальном окружении это:
.. code-block:: text
    pip install -r requirements.txt

Если вам недостаточно тех ежиков, что нашел я, вы можете пополнить коллекцию ежиков добавив фотки с ними в images/, название файлов должно начинаться с hedgehog, файлы должны быть в формате .jpg либо .jpeg Пример: hedgehog_50500.

Настройка
----------
Создайте файл settings.py и добавьте туда следующие настройки:
.. code-block:: python
    PROXY = {'proxy_url': 'socks5://ВАШ_SOCKS5_PROXY:1080',
            'urllib3_proxy_kwargs':{'username':'ЛОГИН','password':'ПАРОЛЬ'}
    }

    API_KEY = "API полученный от BotFather"

    USER_EMOJI = [':smiley_cat:', ':smiling_imp:', ':panda_face:', ':dog:', ':nerd_face:', 
                ':sunglasses:']

Запуск
------
В активированном виртуальном окружении выполните:
.. code-block:: text
    python bot.py
