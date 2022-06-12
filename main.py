import telebot
import config
import markups
import sqlite3

bot = telebot.TeleBot(config.TOKEN)

conn = sqlite3.connect('db/evroopt.db', check_same_thread=False)
cursor = conn.cursor()

def add_news_photo(message):
    fileID = message.photo[-1].file_id
    file = bot.get_file(fileID)
    downloaded_file = bot.download_file(file.file_path)
    bot.send_message(message.chat.id,
                     "Фото было успешно добавлено!\nСледующее ваше сообщение будет записано как текст публикации!")
    bot.register_next_step_handler(message, add_news_text, img=downloaded_file)

def add_news_text(message, img):
    cursor.execute('INSERT INTO news (news_text, news_img) VALUES (?, ?)',
                   (message.text, img))
    conn.commit()
    bot.send_message(message.chat.id, "Текст был успешно сохранен!\nВаша публикация добавлена в общий список!")

def add_promo_text(message, img):
    cursor.execute('INSERT INTO promo (promo_text, promo_img) VALUES (?, ?)',
                   (message.text, img))
    conn.commit()
    bot.send_message(message.chat.id, "Текст был успешно сохранен!\nВаша публикация добавлена в общий список!")

def add_promo_photo(message):
    fileID = message.photo[-1].file_id
    file = bot.get_file(fileID)
    downloaded_file = bot.download_file(file.file_path)
    bot.send_message(message.chat.id,
                     "Фото было успешно добавлено!\nСледующее ваше сообщение будет записано как текст публикации!")
    bot.register_next_step_handler(message, add_promo_text, img=downloaded_file)

def send_news(message):
    cursor.execute("SELECT * FROM news;")
    news = cursor.fetchall()
    for i in range(len(news)):
        bot.send_photo(message.chat.id, news[i][2], news[i][1])

def send_promo(message):
    cursor.execute("SELECT * FROM promo;")
    promo = cursor.fetchall()
    for i in range(len(promo)):
        bot.send_photo(message.chat.id, promo[i][2], promo[i][1])

def delete_news(message):
    sql_delete_query = f"DELETE FROM news WHERE ID = {int(message.text)}"
    cursor.execute(sql_delete_query)
    conn.commit()
    bot.send_message(message.chat.id, "Новость была успешно удалена!")

def delete_promo(message):
    sql_delete_query = f"DELETE FROM promo WHERE ID = {int(message.text)}"
    cursor.execute(sql_delete_query)
    conn.commit()
    bot.send_message(message.chat.id, "Акция была успешно удалена!")

@bot.message_handler(commands=["start"])
def start(m, res=False):
    # Добавляем две кнопки
    bot.send_message(m.chat.id, 'Добро пожаловать в бот "Евроопт Новости"! Что хотите посмотреть?',  reply_markup=markups.main_markup)

@bot.message_handler(commands=["admin"])
def admin(m, res=False):
    if m.chat.id in config.admin_id:
        bot.send_message(m.chat.id, 'Добро пожаловать в редактор бота!')
        bot.send_message(m.chat.id, 'Выберите действие', reply_markup=markups.admin_markup)
    else:
        bot.send_message(m.chat.id, f'У Вас нет прав администратора для доступа данной команды!')

@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text.strip() == "Акции 💯":
        send_promo(message)
    elif message.text.strip() == "Новости 📩":
        send_news(message)
    elif message.text.strip() == "Адреса магазинов 🗺":
        bot.send_message(message.chat.id, 'Выберите область', reply_markup=markups.city_markup)
    elif message.text.strip() == "Социальные сети 📱":
        bot.send_message(message.chat.id, config.sm)
    elif message.text.strip() == "Назад ↩":
        bot.send_message(message.chat.id, 'Добро пожаловать в бот "Евроопт Новости"! Что хотите посмотреть?', reply_markup=markups.main_markup)
    elif message.text.strip() == "Брестская обл.":
        bot.send_message(message.chat.id, "Адреса магазинов в Бресткой области представлены ниже:")
        bot.send_message(message.chat.id, config.brest_locs)
    elif message.text.strip() == "Витебская обл.":
        bot.send_message(message.chat.id, "Адреса магазинов в Витебской области представлены ниже:")
        bot.send_message(message.chat.id, config.vitebsk_locs)
    elif message.text.strip() == "Гомельская обл.":
        bot.send_message(message.chat.id, "Адреса магазинов в Гомельской области представлены ниже:")
        bot.send_message(message.chat.id, config.gomel_locs)
    elif message.text.strip() == "Гродненская обл.":
        bot.send_message(message.chat.id, "Адреса магазинов в Гродненской области представлены ниже:")
        bot.send_message(message.chat.id, config.grodno_locs)
    elif message.text.strip() == "Минская обл.":
        bot.send_message(message.chat.id, "Адреса магазинов в Минской области представлены ниже:")
        bot.send_message(message.chat.id, config.minsk_reg_locs)
    elif message.text.strip() == "Могилевская обл.":
        bot.send_message(message.chat.id, "Адреса магазинов в Могилевской области представлены ниже:")
        bot.send_message(message.chat.id, config.mogilev_locs)
    elif message.text.strip() == "Минск":
        bot.send_message(message.chat.id, "Адреса магазинов в Минске представлены ниже:")
        bot.send_message(message.chat.id, config.minsk_locs)
    elif message.text.strip() == "Добавить новость":
        if message.chat.id in config.admin_id:
            bot.send_message(message.chat.id,
                             "Отправьте фото, обязательно выберите 'Сжать фото'!\nФото должно быть формата '.jpg'")
            bot.register_next_step_handler(message, news_photo)
        else:
            bot.send_message(message.chat.id, "У вас нет доступа к команде")
    elif message.text.strip() == "Удалить новость":
        if message.chat.id in config.admin_id:
            cursor.execute("SELECT * FROM news;")
            news = cursor.fetchall()
            for i in range(len(news)):
                bot.send_message(message.chat.id, "Новость "+ str(news[i][0]) +":")
                bot.send_photo(message.chat.id, news[i][2], news[i][1])
            bot.send_message(message.chat.id, "Введите номер новости, которую хотите удалить.")
            bot.register_next_step_handler(message, delete_news)
        else:
            bot.send_message(message.chat.id, "У вас нет доступа к команде")
    elif message.text.strip() == "Добавить акцию":
        if message.chat.id in config.admin_id:
            bot.send_message(message.chat.id,
                             "Отправьте фото, обязательно выберите 'Сжать фото'!\nФото должно быть формата '.jpg'")
            bot.register_next_step_handler(message, promo_photo)
        else:
            bot.send_message(message.chat.id, "У вас нет доступа к команде")
    elif message.text.strip() == "Удалить акцию":
        if message.chat.id in config.admin_id:
            cursor.execute("SELECT * FROM promo;")
            promo = cursor.fetchall()
            for i in range(len(promo)):
                bot.send_message(message.chat.id, "Акция " + str(promo[i][0]) + ":")
                bot.send_photo(message.chat.id, promo[i][2], promo[i][1])
            bot.send_message(message.chat.id, "Введите номер акции, которую хотите удалить.")
            bot.register_next_step_handler(message, delete_promo)
        else:
            bot.send_message(message.chat.id, "У вас нет доступа к команде")
    elif message.text.strip() == "Назад в бота ↩":
        bot.send_message(message.chat.id, 'Добро пожаловать в бот "Евроопт Новости"! Что хотите посмотреть?', reply_markup=markups.main_markup)
    else:
        bot.send_message(message.chat.id, "Не понимаю о чем вы 😔. Пожалуйста, выберите пункт из предложенных.")

@bot.message_handler(content_types=['photo'])
def news_photo(message):
    add_news_photo(message)

def promo_photo(message):
    add_promo_photo(message)

bot.polling(none_stop=True, interval=0)