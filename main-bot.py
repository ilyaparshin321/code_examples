import requests
import telebot
import config
import random
import sqlite3
import sql_etc as s
import os
import sys
import base64
from datetime import datetime
import pytz
import time
import math
import json
import requests

from req_to_ofd import check_processing
from telebot import types as ty

admin_list = ["ilyaparshin321", "ivan_tikholaz", "the7th_aigeluh", "shaurlandia"]
admin_id_list = {"ilyaparshin321": '107992797', "ivan_tikholaz": '637287849', "the7th_aigeluh": '452470174', "shaurlandia":config.admin_tg_id}
bot = telebot.TeleBot(config.TOKEN)


# feedback_group_id = '-1001869223231'
class cafe:  # класс для информации о точках сети
    name = ""
    description = ""
    location = ""
    photo = ""

    def __init__(self, n, d, l, p):
        self.name = n
        self.description = d
        self.location = l
        self.photo = p


class markup:  # класс для удобного объявления объектов типа types.ReplyKeyboardMarkup в подходящих для этого случаях
    m = ty.ReplyKeyboardMarkup()

    def __init__(self, a):
        self.m = ty.ReplyKeyboardMarkup()
        for i in a: self.m.add(ty.KeyboardButton(str(i)))


class good:  # класс для информации о товаре
    name = ""
    description = ""
    price = ""
    cat = ""

    def __init__(self, n, d, p, c):
        self.name = n
        self.description = d
        self.price = p
        self.cat = c

    def description_info(self):  # функция для вывода информации о товаре
        s_description = f"<b>Название товара: </b>{self.name}\n\n<b>Описание: </b>{self.description}" + "\n\n<b>Стоимость: </b>" + str(
            self.price) + '₽'
        return s_description


# объявление глобальных переменных
current_time = datetime.now().strftime("%H:%M")
right_now_rek_test = []
binary_markup = ty.ReplyKeyboardMarkup()
binary_markup.add("Да", "Нет")
rek_passed_users = {}
che1 = False
new_good_info = []
global new_good_to_review
new_good_to_review = [""]
rev_check_markup_array = []
markup_admin_wishlists_array = []
markup_admin_delete_order_list = []
checker_for_restart1 = False
markup_for_a_menu_array = []
markup_to_del_good_menu_array = []
markup5 = markup([""])
markup_to_red_good_menu_array = []
markup_put_smth_in_wishlist = []
additional_markup_put_etc = []
new_menu_markup_in_array = []
comment1 = ['здесь будет комментарий']
just_lk_markup = ty.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
just_lk_markup.add(ty.KeyboardButton("Личный Кабинет"))
markup_put_smth_in_wishlist_again = []
global menu_id
time_choice = ['']
zakaz_id = ['']


def writeTofile(data, filename):  # запись BLOB в файл-изображение
    with open(filename, 'wb') as file:
        file.write(data)
    #print("Data placed in: ", filename, "\n")


def check_username_wishlist(message):  # проверка того, есть ли user_id пользователя в таблице БД для виш-листов
    checker1 = False
    for i in s.w:
        if i[1] == message.from_user.id:
            checker1 = True
            break
    if checker1 == True:
        return True
    else:
        return False


def check_username_order(message):  # проверка того, есть ли у пользователя активный заказ
    checker1 = False
    for i in s.o:
        if i[1] == message.from_user.id:
            checker1 = True
            break
    if checker1 == True:
        return True
    else:
        return False


def search_username_wishlist(message):  # поиск номера строки в таблице БД для виш-листов по user_id пользователя
    for i in s.w:
        if i[1] == message.from_user.id:
            return s.w.index(i)


def search_good_line_in_menu(something):  # поиск номера строки в таблице БД для товаров по названию товара
    for i in s.d:
        if i[1] == something:
            return s.d.index(i)

def search_good_line_in_menu_by_idx(idx):  # поиск номера строки в таблице БД для товаров по названию товара
    for i in s.d:
        if i[0] == idx:
            return s.d.index(i)

def search_good_line_no_price_in_menu(something):  # поиск номера строки в таблице БД для товаров по названию товара
    for i in s.d:
        if i[6] == something:
            return s.d.index(i)


def search_username_order(user_id):  # поиск номера строки в таблице БД для заказов по user_id пользователя
    for i in s.o:
        if i[1] == user_id: return s.o.index(i)

def search_username_new_order(user_id, where):
    for i in where:
        if i[1] == user_id: return where.index(i)

def search_username_promo(user_id):  # поиск номера строки в таблице БД для акций по user_id пользователя
    for i in s.promo:
        if i[0] == str(user_id):
            return s.promo.index(i)


def search_username_menu_ids(user_id):  # поиск номера строки в таблице БД для акций по user_id пользователя
    for i in s.menu_ids:
        if str(i[0]) == str(user_id):
            return s.menu_ids.index(i)


def search_username_choice_ids(user_id):  # поиск номера строки в таблице БД для акций по user_id пользователя
    for i in s.choice_ids:
        if str(i[0]) == str(user_id):
            return s.choice_ids.index(i)


def search_omc_by_user_id(user_id):  # поиск номера строки в таблице БД для заказов по user_id пользователя
    for i in s.osi2:
        if i[2] == user_id: return s.osi2.index(i)


def search_free_time(array_with_time):  # фильтр еще не занятого другими заказами времени среди всех слотов времени
    s.time1 = s.sql.execute("SELECT * FROM time")
    s.t = s.sql.fetchall()
    for i in s.o:
        if i[12] in array_with_time: array_with_time.remove(i[12])
    for i in s.t:
        if i[1] in array_with_time: array_with_time.remove(i[1])
    return array_with_time


def search_for_last_free_db_space(
        message):  # поиск последней свободной ячейки в строке таблицы БД для виш-листов для конкретного пользователя
    the_checker = False
    what_to_find = 2
    for i in s.w[search_username_wishlist(message)][2:12]:
        if i == '':
            the_checker = True
            what_to_find = s.w[search_username_wishlist(message)].index(i)
    if the_checker == False:
        what_to_find = 11
    if what_to_find == 2: return 'good1'
    if what_to_find == 3: return 'good2'
    if what_to_find == 4: return 'good3'
    if what_to_find == 5: return 'good4'
    if what_to_find == 6: return 'good5'
    if what_to_find == 7: return 'good6'
    if what_to_find == 8: return 'good7'
    if what_to_find == 9: return 'good8'
    if what_to_find == 10: return 'good9'
    if what_to_find == 11:
        return 'good10'
    else:
        return 'good10'


def last_unfree_db_space(
        message):  # поиск последней свободной ячейки в строке таблицы БД для виш-листов для конкретного пользователя
    the_checker = False
    what_to_find = 2
    for i in s.w[search_username_wishlist(message)][2:12]:
        if i == '':
            the_checker = True
            what_to_find = s.w[search_username_wishlist(message)].index(i)
    if the_checker == False:
        what_to_find = 2
    if what_to_find == 2: return 'good10'
    if what_to_find == 3: return 'good1'
    if what_to_find == 4: return 'good2'
    if what_to_find == 5: return 'good3'
    if what_to_find == 6: return 'good4'
    if what_to_find == 7: return 'good5'
    if what_to_find == 8: return 'good6'
    if what_to_find == 9: return 'good7'
    if what_to_find == 10: return 'good8'
    if what_to_find == 11:
        return 'good9'
    else:
        return 'good10'


def search_user_id_and_shaurma_name_line(user_id,
                                         shaurma_name):  # поиск номера строки в таблице БД для добавок по user_id и shaurma_name
    for i in s.p:
        if i[1] == user_id and i[2] == shaurma_name: return s.p.index(i)


def search_for_last_free_dobavki_space(
        message):  # поиск последней свободной ячейки в строке таблицы БД для виш-листов для конкретного пользователя
    the_checker = False
    what_to_find = 12
    for i in s.w[search_username_wishlist(message)][12:]:
        if i == '' or i == ' ':
            #print('ok, ')
            the_checker = True
            what_to_find = s.w[search_username_wishlist(message)][12:].index(i) + 12
    #print('what to find', what_to_find)
    if the_checker == False:
        what_to_find = 12
    if what_to_find == 12: return 'd1'
    if what_to_find == 13: return 'd2'
    if what_to_find == 14: return 'd3'
    if what_to_find == 15: return 'd4'
    if what_to_find == 16: return 'd5'
    if what_to_find == 17: return 'd6'
    if what_to_find == 18: return 'd7'
    if what_to_find == 19: return 'd8'
    if what_to_find == 20: return 'd9'
    if what_to_find == 21: return 'd10'
    if what_to_find == 22: return 'd11'
    if what_to_find == 23: return 'd12'
    if what_to_find == 24: return 'd13'
    if what_to_find == 25: return 'd14'
    if what_to_find == 26: return 'd15'
    if what_to_find == 27: return 'd16'
    if what_to_find == 28: return 'd17'
    if what_to_find == 29: return 'd18'
    if what_to_find == 30: return 'd19'
    if what_to_find == 31: return 'd20'
    if what_to_find == 32: return 'd21'
    if what_to_find == 33: return 'd22'
    if what_to_find == 34: return 'd23'
    if what_to_find == 35: return 'd24'
    if what_to_find == 36: return 'd25'
    if what_to_find == 37: return 'd26'
    if what_to_find == 38: return 'd27'
    if what_to_find == 39: return 'd28'
    if what_to_find == 40: return 'd29'
    if what_to_find == 41:
        return 'd30'
    else:
        return 'd1'


def clear_wishlist(message):  # очистка виш-листа
    string_about_goods = 'good1'
    for i in range(2, 42):
        if i == 2: string_about_goods = 'good1'
        if i == 3: string_about_goods = 'good2'
        if i == 4: string_about_goods = 'good3'
        if i == 5: string_about_goods = 'good4'
        if i == 6: string_about_goods = 'good5'
        if i == 7: string_about_goods = 'good6'
        if i == 8: string_about_goods = 'good7'
        if i == 9: string_about_goods = 'good8'
        if i == 10: string_about_goods = 'good9'
        if i == 11: string_about_goods = 'good10'
        if i == 12: string_about_goods = 'd1'
        if i == 13: string_about_goods = 'd2'
        if i == 14: string_about_goods = 'd3'
        if i == 15: string_about_goods = 'd4'
        if i == 16: string_about_goods = 'd5'
        if i == 17: string_about_goods = 'd6'
        if i == 18: string_about_goods = 'd7'
        if i == 19: string_about_goods = 'd8'
        if i == 20: string_about_goods = 'd9'
        if i == 21: string_about_goods = 'd10'
        if i == 22: string_about_goods = 'd11'
        if i == 23: string_about_goods = 'd12'
        if i == 24: string_about_goods = 'd13'
        if i == 25: string_about_goods = 'd14'
        if i == 26: string_about_goods = 'd15'
        if i == 27: string_about_goods = 'd16'
        if i == 28: string_about_goods = 'd17'
        if i == 29: string_about_goods = 'd18'
        if i == 30: string_about_goods = 'd19'
        if i == 31: string_about_goods = 'd20'
        if i == 32: string_about_goods = 'd21'
        if i == 33: string_about_goods = 'd22'
        if i == 34: string_about_goods = 'd23'
        if i == 35: string_about_goods = 'd24'
        if i == 36: string_about_goods = 'd25'
        if i == 37: string_about_goods = 'd26'
        if i == 38: string_about_goods = 'd27'
        if i == 39: string_about_goods = 'd28'
        if i == 40: string_about_goods = 'd29'
        if i == 41: string_about_goods = 'd30'

        s.sql.execute(f"""UPDATE wishlist SET '{string_about_goods}' = '' WHERE username = '{message.from_user.id}'""")
        s.db.commit()


def pos_time():  # формирование списка слотов времени
    tz = pytz.timezone('Europe/Moscow')
    curr_time = datetime.now(tz).strftime("%H:%M")
    possible_time = []

    if curr_time[:2] in ['0' + i for i in '0123456789']:
        curr_hour = int(curr_time[1])
    else:
        curr_hour = int(curr_time[:2])
    curr_minute = curr_time[-2:]
    if curr_minute == "00":
        curr_minute_int = 0
    elif curr_minute == "05":
        curr_minute_int = 5
    else:
        curr_minute_int = int(curr_minute)
    #print(curr_hour)
    #print(curr_minute_int)
    for j in range(0, 24):
        for i in range(0, 60, 5):
            if (curr_minute_int + 5 < i and curr_hour == j) or (curr_hour < j):
                if j in range(0, 10):
                    res_j = '0' + str(j)
                else:
                    res_j = str(j)
                if i in range(0, 10):
                    res_i = '0' + str(i)
                else:
                    res_i = str(i)

                possible_time.append((res_j) + ':' + str(res_i))
    #print(curr_time)
    for i in ['20:25', '20:30', '20:35', '20:40', '20:45', '20:50', '20:55', '21:00', '21:05']:
        try:
            possible_time.remove(i)
        except ValueError:
            pass
    return search_free_time(possible_time)


def comments_handler(message, user_id):  # функиця, принимающая комментарии пользователя к заказу
    if str(user_id) != str(message.from_user.id):
        return 0
    elif message.text == "Изменить содержимое заказа":
        bot.send_message(message.chat.id, "Чтобы добавить новый товар в корзину, "
                                          "зайдите в раздел меню. Чтобы удалить товар из корзины, "
                                          "нажмите соответствующую кнопку в разделе Корзина",
                         reply_markup=markup(["Вернуться в Меню", "Перейти в Корзину"]).m)
        return 0
    elif message.text == 'Отменить и очистить заказ':
        clear_wishlist(message)
        bot.send_message(message.chat.id, "Заказ отменен и корзина очищена. Ждем вас снова!",
                         reply_markup=just_lk_markup)
        os.execv(sys.executable, [sys.executable] + sys.argv)
        return 0
    else:
        if len(pos_time()) == 0:
            bot.send_message(message.chat.id,
                             "Извините, но свободного временного слота на заказ на сегодня не осталось. Попробуйте еще раз завтра или приходите сделать заказ вживую",
                             reply_markup=markup(["Вернуться в Личный Кабинет"]).m)
            return 0
        comment1.clear()
        comment1.append(message.text)
        ch_2(message=message, user_id=user_id)


def ch_2(message, user_id):  # функция для выбора времени выдачи заказа
    if str(user_id) != str(message.from_user.id):
        return 0
    global start_time
    markup_with_time = markup(['Изменить содержимое заказа', 'Отменить и очистить заказ'] + [i for i in pos_time()])
    from_comments_to_time = bot.send_message(message.chat.id,
                                             "Выберите время, в которое Вам будет удобно забрать заказ",
                                             reply_markup=markup_with_time.m)
    start_time = time.time()
    bot.register_next_step_handler(from_comments_to_time, time_handler, user_id)

def check_user_id(message):  # проверка товаров и добавок в корзине
    g_1 = s.w[search_username_wishlist(message)][2]
    g_2 = s.w[search_username_wishlist(message)][3]
    g_3 = s.w[search_username_wishlist(message)][4]
    g_4 = s.w[search_username_wishlist(message)][5]
    g_5 = s.w[search_username_wishlist(message)][6]
    g_6 = s.w[search_username_wishlist(message)][7]
    g_7 = s.w[search_username_wishlist(message)][8]
    g_8 = s.w[search_username_wishlist(message)][9]
    g_9 = s.w[search_username_wishlist(message)][10]
    g_10 = s.w[search_username_wishlist(message)][11]
    d_1 = s.w[search_username_wishlist(message)][12]
    d_2 = s.w[search_username_wishlist(message)][13]
    d_3 = s.w[search_username_wishlist(message)][14]
    d_4 = s.w[search_username_wishlist(message)][15]
    d_5 = s.w[search_username_wishlist(message)][16]
    d_6 = s.w[search_username_wishlist(message)][17]
    d_7 = s.w[search_username_wishlist(message)][18]
    d_8 = s.w[search_username_wishlist(message)][19]
    d_9 = s.w[search_username_wishlist(message)][20]
    d_10 = s.w[search_username_wishlist(message)][21]

    d_11 = s.w[search_username_wishlist(message)][22]
    d_12 = s.w[search_username_wishlist(message)][23]
    d_13 = s.w[search_username_wishlist(message)][24]
    d_14 = s.w[search_username_wishlist(message)][25]
    d_15 = s.w[search_username_wishlist(message)][26]
    d_16 = s.w[search_username_wishlist(message)][27]
    d_17 = s.w[search_username_wishlist(message)][28]
    d_18 = s.w[search_username_wishlist(message)][29]
    d_19 = s.w[search_username_wishlist(message)][30]
    d_20 = s.w[search_username_wishlist(message)][31]

    d_21 = s.w[search_username_wishlist(message)][32]
    d_22 = s.w[search_username_wishlist(message)][33]
    d_23 = s.w[search_username_wishlist(message)][34]
    d_24 = s.w[search_username_wishlist(message)][35]
    d_25 = s.w[search_username_wishlist(message)][36]
    d_26 = s.w[search_username_wishlist(message)][37]
    d_27 = s.w[search_username_wishlist(message)][38]
    d_28 = s.w[search_username_wishlist(message)][39]
    d_29 = s.w[search_username_wishlist(message)][40]
    d_30 = s.w[search_username_wishlist(message)][41]

    d_and_g_array = [g_1, g_2, g_3, g_4, g_5, g_6, g_7, g_8, g_9, g_10,
                     d_1, d_2, d_3, d_4, d_5, d_6, d_7, d_8, d_9, d_10,
                     d_11, d_12, d_13, d_14, d_15, d_16, d_17, d_18, d_19, d_20,
                     d_21, d_22, d_23, d_24, d_25, d_26, d_27, d_28, d_29, d_30]

    return s.w[search_username_wishlist(message)][2:42] == d_and_g_array


def time_handler(message, user_id):  # функция, принимающая выбранное время и отправляющая инвойс
    if str(user_id) != str(message.from_user.id):
        return 0
    if message.text == "Изменить содержимое заказа":
        bot.send_message(message.chat.id, "Чтобы добавить новый товар в корзину, "
                                          "зайдите в раздел меню. Чтобы удалить товар из корзины, "
                                          "нажмите соответствующую кнопку в разделе Корзина",
                         reply_markup=markup(["Вернуться в Меню", "Перейти в Корзину"]).m)
        return 0
    elif message.text == 'Отменить и очистить заказ':
        clear_wishlist(message)
        bot.send_message(message.chat.id, "Заказ отменен и корзина очищена. Ждем вас снова!",
                         reply_markup=just_lk_markup)
        os.execv(sys.executable, [sys.executable] + sys.argv)
        return 0
    global start_time
    if message.text not in pos_time():
        bot.send_message(message.chat.id,
                         "Похоже, вы выбрали время, которое сейчас недоступно."
                         "Пожалуйста, попробуйте выбрать другое время")
        ch_2(message=message)
        return 0

    s.sql.execute(f"""INSERT INTO time(user_id, times)
                                           VALUES('{message.from_user.id}', '{message.text}');""")
    s.db.commit()

    g_1 = s.w[search_username_wishlist(message)][2]
    g_2 = s.w[search_username_wishlist(message)][3]
    g_3 = s.w[search_username_wishlist(message)][4]
    g_4 = s.w[search_username_wishlist(message)][5]
    g_5 = s.w[search_username_wishlist(message)][6]
    g_6 = s.w[search_username_wishlist(message)][7]
    g_7 = s.w[search_username_wishlist(message)][8]
    g_8 = s.w[search_username_wishlist(message)][9]
    g_9 = s.w[search_username_wishlist(message)][10]
    g_10 = s.w[search_username_wishlist(message)][11]
    d_1 = s.w[search_username_wishlist(message)][12]
    d_2 = s.w[search_username_wishlist(message)][13]
    d_3 = s.w[search_username_wishlist(message)][14]
    d_4 = s.w[search_username_wishlist(message)][15]
    d_5 = s.w[search_username_wishlist(message)][16]
    d_6 = s.w[search_username_wishlist(message)][17]
    d_7 = s.w[search_username_wishlist(message)][18]
    d_8 = s.w[search_username_wishlist(message)][19]
    d_9 = s.w[search_username_wishlist(message)][20]
    d_10 = s.w[search_username_wishlist(message)][21]

    d_11 = s.w[search_username_wishlist(message)][22]
    d_12 = s.w[search_username_wishlist(message)][23]
    d_13 = s.w[search_username_wishlist(message)][24]
    d_14 = s.w[search_username_wishlist(message)][25]
    d_15 = s.w[search_username_wishlist(message)][26]
    d_16 = s.w[search_username_wishlist(message)][27]
    d_17 = s.w[search_username_wishlist(message)][28]
    d_18 = s.w[search_username_wishlist(message)][29]
    d_19 = s.w[search_username_wishlist(message)][30]
    d_20 = s.w[search_username_wishlist(message)][31]

    d_21 = s.w[search_username_wishlist(message)][32]
    d_22 = s.w[search_username_wishlist(message)][33]
    d_23 = s.w[search_username_wishlist(message)][34]
    d_24 = s.w[search_username_wishlist(message)][35]
    d_25 = s.w[search_username_wishlist(message)][36]
    d_26 = s.w[search_username_wishlist(message)][37]
    d_27 = s.w[search_username_wishlist(message)][38]
    d_28 = s.w[search_username_wishlist(message)][39]
    d_29 = s.w[search_username_wishlist(message)][40]
    d_30 = s.w[search_username_wishlist(message)][41]

    goods_and_prices = []
    d_and_g_array = [g_1, g_2, g_3, g_4, g_5, g_6, g_7, g_8, g_9, g_10,
                     d_1, d_2, d_3, d_4, d_5, d_6, d_7, d_8, d_9, d_10,
                     d_11, d_12, d_13, d_14, d_15, d_16, d_17, d_18, d_19, d_20,
                     d_21, d_22, d_23, d_24, d_25, d_26, d_27, d_28, d_29, d_30]

    for i in range(len(d_and_g_array)):
        if d_and_g_array[i] not in [' ', '']:
            d_current = d_and_g_array[i]
            #print(d_current)
            if i >= 10:
                d_current = d_current[:-6]
                #print('i am at d_current 2: ', d_current)
                if d_current[-1] == "g" or d_current[-1] == " ":
                    d_current = d_current[:-1]
                #print('aaa', d_current)
            goods_and_prices.append([d_current, s.d[search_good_line_no_price_in_menu(d_current)][3]])
    #print(goods_and_prices)

    if (time.time() - start_time) < 60:
        time_choice[0] = message.text
        '''s.sql.execute(
            f"""UPDATE order_string_id SET only = '{1}' WHERE only = '{s.order_string_id - 1}'""")
        s.order_string_id = 1'''
        # if else
        tz = pytz.timezone('Europe/Moscow')
        global zakaz_id
        zakaz_id[0] = str(datetime.now(tz).strftime("%d-%m-%Y:")) + (4 - len(str(s.order_string_id)))*'0' + str(s.order_string_id)


        '''
        s.sql.execute(
            f"""UPDATE promo_usage SET free_tea = {0}
                                                    WHERE username = '{message.from_user.id}'""")
        '''

        # tut oplata
        bot.send_message(message.chat.id, 'Время успешно выбрано! Осталость только оплатить заказ.')

        # (sum_price([i for i in s.o[markup_admin_wishlists_array.index(message.text)][2:12]]) + summa_order) * 100
        keyboard = ty.InlineKeyboardMarkup()
        # Создание кнопки оплаты
        pay_button = ty.InlineKeyboardButton(text="Оплатить", pay=True)
        # Добавление кнопки на клавиатуру
        keyboard.add(pay_button)

        global invoice_id
        price_list = []
        total = 0
        for i in goods_and_prices:
            price_list.append(ty.LabeledPrice(label=i[0], amount=(i[1] * 100)))
            total += (i[1] * 100)
        #print(goods_and_prices)

        #[['Шаурма Японская', 219], ['Шаурма Московская', 179], ['Соус "карри"', 29], ['Укроп', 19], ['Острый соус', 0], ['Салат айсберг', 29], ['Фасоль', 39], ['Курица', 69], ['Острый соус', 0], ['Кинза', 19]]

        # if check_user_id(message):
        bot.send_message(message.chat.id, "Чтобы мы успели приготовить заказ вовремя, убедительно просим Вас оплатить заказ не позже, чем за 5 минут до выбранного времени выдачи")
        invoice_message = bot.send_invoice(chat_id=message.chat.id, title='Оплата заказа',
                                           description='Приятного аппетита!',
                                           provider_token=config.PAYMENTS_TOKEN, currency='RUB',
                                           photo_url="https://lh3.googleusercontent.com/pw/AJFCJaVnXcw22VxIJ2FcQUvbbm29hDgkA5L5PP54a12MQlS0aoFK7-pU5XN7ndLnWN2hiGwr_MCCNji2c6T0YwsEFM2K1a6fJfCUkMJfNT3NPLBcOT2TEQwCHSBo-u0Ctd9jM18l23QyRQGLIDrK7_C34d-mZ5LpQTuVsJqPiHI73YYRcK3sGVEOrKuCec055bmsumi_q4Nl3Ex9UZ_PZy9tBjgOEn2cQOYZLRjEZQDF6xUlqjRETVDwAc4SoRSbw7e6ZhKCLpWHxzgfj47K_HTV7bIofqdBVFCZFj_efcJEj0tL1xdMOiVQK1Y3JyEHFP2GPwcp5BG4nMpFnsI76sQQ-VdvMio-yVw-2tD2-WyOOXFBdEZrBs7IU4zWbtOln_KMmEnJTRhjTW5rzYCYfEe6smJxJmSEHhYS5Dyq4Pjaek16Eq78YsJxdoGINLRebTXblAzB3QeYv6TI76a-PBocU_CCM6XMVkanX_9PHGJV-Z2F8L0g2JhzyziLPV5hnYn4Y1zSbb-ONcroKRyv1gqgJzsXxvgvkrwqJrd2C2zoZXN9dqwAUIVkqFXgvPgsVNZbCUKs20WnrLV1ks7Ullv9YV6q_m4dt9LPdxYhMDVGKbESfeNZQT3mGJUSyqI8VkqkHb1KmeH_mTaLlCT29izQEOTqNQYKGtipb_87TZSnghSETYmL-pRzBFj8zVZUNE0OtNI5n3lYrjBsVQ00cnuQyBcNlajxdwhpGHZtIAYwEWVJPCxqNapegbjst3GqsCKHN4QUnHqEko1QTfD7P72FsY8uo_uEop4DetVXXAAed6UqYlI_zCJGLhVpOCSi9MDpOzofMdas9Fk_nFsb_Yx7eSqObnFY4uVjwFZSIXoQmrRluj1KIUsOhZC2H0qcUUtlgQsBVKwUQv_-jhpgCLh8A3j0hzt5jRHEBsgBhVdCMrlpg1-Yj5KsUqTNLJhH_C12U-feJJwKlMRHvLyemtVyiQG6P4896g=w640-h640-s-no?authuser=0",
                                           photo_height=256, photo_width=256, need_phone_number=True, need_email=True,
                                           prices=price_list,
                                           start_parameter='invoice-payment', invoice_payload='HIDDEN_PAYLOAD',
                                           reply_markup=keyboard)
        #print(invoice_message)
        '''
        max_tip_amount = int(total),
        suggested_tip_amounts = [(math.ceil(total / 10000) * 100),
                                 (math.ceil(total / 10000) * 500),
                                 (math.ceil(total / 10000) * 1000),
                                 (math.ceil(total / 10000) * 1500)],
        '''

        invoice_id = invoice_message.message_id

        bot.send_message(message.chat.id, "Чтобы оплатить заказ, восполользуйтесь кнопкой сверху",
                         reply_markup=markup(["Изменить содержимое заказа", "Отменить и очистить заказ"]).m)

    else:
        bot.send_message(message.chat.id,
                         "Кажется вы выбирали время слишком долго. Пожалуйста, выберите заново время, в которое Вам будет удобно забрать заказ")
        ch_2(message=message)


@bot.pre_checkout_query_handler(func=lambda query: True)
def pre_checkout_query(pre_checkout_q: ty.PreCheckoutQuery):
    bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@bot.message_handler(content_types=['successful_payment'])
def process_pay(message: telebot.types.Message):  # обработка оплаты и фиксирование заказа
    g_1 = s.w[search_username_wishlist(message)][2]
    g_2 = s.w[search_username_wishlist(message)][3]
    g_3 = s.w[search_username_wishlist(message)][4]
    g_4 = s.w[search_username_wishlist(message)][5]
    g_5 = s.w[search_username_wishlist(message)][6]
    g_6 = s.w[search_username_wishlist(message)][7]
    g_7 = s.w[search_username_wishlist(message)][8]
    g_8 = s.w[search_username_wishlist(message)][9]
    g_9 = s.w[search_username_wishlist(message)][10]
    g_10 = s.w[search_username_wishlist(message)][11]
    d_1 = s.w[search_username_wishlist(message)][12]
    d_2 = s.w[search_username_wishlist(message)][13]
    d_3 = s.w[search_username_wishlist(message)][14]
    d_4 = s.w[search_username_wishlist(message)][15]
    d_5 = s.w[search_username_wishlist(message)][16]
    d_6 = s.w[search_username_wishlist(message)][17]
    d_7 = s.w[search_username_wishlist(message)][18]
    d_8 = s.w[search_username_wishlist(message)][19]
    d_9 = s.w[search_username_wishlist(message)][20]
    d_10 = s.w[search_username_wishlist(message)][21]

    d_11 = s.w[search_username_wishlist(message)][22]
    d_12 = s.w[search_username_wishlist(message)][23]
    d_13 = s.w[search_username_wishlist(message)][24]
    d_14 = s.w[search_username_wishlist(message)][25]
    d_15 = s.w[search_username_wishlist(message)][26]
    d_16 = s.w[search_username_wishlist(message)][27]
    d_17 = s.w[search_username_wishlist(message)][28]
    d_18 = s.w[search_username_wishlist(message)][29]
    d_19 = s.w[search_username_wishlist(message)][30]
    d_20 = s.w[search_username_wishlist(message)][31]

    d_21 = s.w[search_username_wishlist(message)][32]
    d_22 = s.w[search_username_wishlist(message)][33]
    d_23 = s.w[search_username_wishlist(message)][34]
    d_24 = s.w[search_username_wishlist(message)][35]
    d_25 = s.w[search_username_wishlist(message)][36]
    d_26 = s.w[search_username_wishlist(message)][37]
    d_27 = s.w[search_username_wishlist(message)][38]
    d_28 = s.w[search_username_wishlist(message)][39]
    d_29 = s.w[search_username_wishlist(message)][40]
    d_30 = s.w[search_username_wishlist(message)][41]

    goods_and_prices = []
    d_and_g_array = [g_1, g_2, g_3, g_4, g_5, g_6, g_7, g_8, g_9, g_10,
                     d_1, d_2, d_3, d_4, d_5, d_6, d_7, d_8, d_9, d_10,
                     d_11, d_12, d_13, d_14, d_15, d_16, d_17, d_18, d_19, d_20,
                     d_21, d_22, d_23, d_24, d_25, d_26, d_27, d_28, d_29, d_30]

    for i in range(len(d_and_g_array)):
        if d_and_g_array[i] not in [' ', '']:
            d_current = d_and_g_array[i]
            # print(d_current)
            if i >= 10:
                d_current = d_current[:-6]
                # print('i am at d_current 2: ', d_current)
                if d_current[-1] == "g" or d_current[-1] == " ":
                    d_current = d_current[:-1]
                # print('aaa', d_current)
            goods_and_prices.append([d_current, s.d[search_good_line_no_price_in_menu(d_current)][3]])
    if message.successful_payment.invoice_payload == 'HIDDEN_PAYLOAD':

        #message.successful_payment.order_info.email
        #message.successful_payment.order_info.phone_number

        #print(message.successful_payment.order_info)
        # {'name': None, 'phone_number': '79660273275', 'email': 'teoman_oztemel@mail.ru', 'shipping_address': None}
        msg = message.successful_payment.order_info
        phone = msg.phone_number
        mail = msg.email

        check_result = check_processing(phone_number = phone, email = mail, order_id = zakaz_id[0], w_list = goods_and_prices)

        p_markup = ty.ReplyKeyboardMarkup()
        p_markup.add("Вернуться в Личный Кабинет")
        p_markup.add("Оставить отзыв")

        g_1 = s.w[search_username_wishlist(message)][2]
        g_2 = s.w[search_username_wishlist(message)][3]
        g_3 = s.w[search_username_wishlist(message)][4]
        g_4 = s.w[search_username_wishlist(message)][5]
        g_5 = s.w[search_username_wishlist(message)][6]
        g_6 = s.w[search_username_wishlist(message)][7]
        g_7 = s.w[search_username_wishlist(message)][8]
        g_8 = s.w[search_username_wishlist(message)][9]
        g_9 = s.w[search_username_wishlist(message)][10]
        g_10 = s.w[search_username_wishlist(message)][11]
        d_1 = s.w[search_username_wishlist(message)][12]
        d_2 = s.w[search_username_wishlist(message)][13]
        d_3 = s.w[search_username_wishlist(message)][14]
        d_4 = s.w[search_username_wishlist(message)][15]
        d_5 = s.w[search_username_wishlist(message)][16]
        d_6 = s.w[search_username_wishlist(message)][17]
        d_7 = s.w[search_username_wishlist(message)][18]
        d_8 = s.w[search_username_wishlist(message)][19]
        d_9 = s.w[search_username_wishlist(message)][20]
        d_10 = s.w[search_username_wishlist(message)][21]

        d_11 = s.w[search_username_wishlist(message)][22]
        d_12 = s.w[search_username_wishlist(message)][23]
        d_13 = s.w[search_username_wishlist(message)][24]
        d_14 = s.w[search_username_wishlist(message)][25]
        d_15 = s.w[search_username_wishlist(message)][26]
        d_16 = s.w[search_username_wishlist(message)][27]
        d_17 = s.w[search_username_wishlist(message)][28]
        d_18 = s.w[search_username_wishlist(message)][29]
        d_19 = s.w[search_username_wishlist(message)][30]
        d_20 = s.w[search_username_wishlist(message)][31]

        d_21 = s.w[search_username_wishlist(message)][32]
        d_22 = s.w[search_username_wishlist(message)][33]
        d_23 = s.w[search_username_wishlist(message)][34]
        d_24 = s.w[search_username_wishlist(message)][35]
        d_25 = s.w[search_username_wishlist(message)][36]
        d_26 = s.w[search_username_wishlist(message)][37]
        d_27 = s.w[search_username_wishlist(message)][38]
        d_28 = s.w[search_username_wishlist(message)][39]
        d_29 = s.w[search_username_wishlist(message)][40]
        d_30 = s.w[search_username_wishlist(message)][41]

        s.time1 = s.sql.execute("SELECT * FROM time")
        s.t = s.sql.fetchall()

        user_time_choice = s.t[search_time_line(message)][1]

        if s.order_string_id > 998:
            s.sql.execute(
                f"""UPDATE order_string_id SET only = '{1}' 
                                                WHERE only = '{s.order_string_id}'""")
        else:
            s.sql.execute(
                f"""UPDATE order_string_id SET only = '{s.order_string_id + 1}' 
                                WHERE only = '{s.order_string_id}'""")
        s.db.commit()
        s.osi = (s.sql.execute("SELECT * FROM order_string_id"))
        s.osi2 = s.sql.fetchall()  # osi = Order String ID
        s.order_string_id = s.osi2[0][0]

        # print('time choice ', user_time_choice)
        # print('ord s id', s.order_string_id)

        s.sql.execute(f"""INSERT INTO orders(id, username, good1, good2, good3, good4, good5, good6, good7, good8,
                         good9, good10, time, surplus, d1, d2, d3, d4, d5, d6, d7, d8, d9, d10,
                         d11, d12, d13, d14, d15, d16, d17, d18, d19, d20, d21, d22, d23, d24, d25, d26, d27, d28, d29, d30)
                         VALUES('{str(s.order_string_id)}', '{message.from_user.id}', '{g_1}', '{g_2}', '{g_3}', '{g_4}', '{g_5}',
                          '{g_6}', '{g_7}', '{g_8}', '{g_9}', '{g_10}', '{user_time_choice}', '{str(comment1[0])}',
                           '{d_1}', '{d_2}', '{d_3}', '{d_4}', '{d_5}', '{d_6}', '{d_7}', '{d_8}', '{d_9}', '{d_10}',
                           '{d_11}', '{d_12}', '{d_13}', '{d_14}', '{d_15}', '{d_16}', '{d_17}', '{d_18}', '{d_19}', '{d_20}',
                           '{d_21}', '{d_22}', '{d_23}', '{d_24}', '{d_25}', '{d_26}', '{d_27}', '{d_28}', '{d_29}', '{d_30}');""")

        # s.sql.execute(f"""INSERT INTO orders_statistics(id, username, good1, good2, good3, good4, good5, good6, good7, good8,
        # good9, good10, time, surplus, d1, d2, d3, d4, d5, d6, d7, d8, d9, d10,
        # d11, d12, d13, d14, d15, d16, d17, d18, d19, d20, d21, d22, d23, d24, d25, d26, d27, d28, d29, d30)
        # VALUES('{str(s.order_string_id)}', '{message.from_user.id}', '{g_1}', '{g_2}', '{g_3}', '{g_4}', '{g_5}',
        # '{g_6}', '{g_7}', '{g_8}', '{g_9}', '{g_10}', '{user_time_choice}', '{str(comment1[0])}',
        #  '{d_1}', '{d_2}', '{d_3}', '{d_4}', '{d_5}', '{d_6}', '{d_7}', '{d_8}', '{d_9}', '{d_10}',
        #  '{d_11}', '{d_12}', '{d_13}', '{d_14}', '{d_15}', '{d_16}', '{d_17}', '{d_18}', '{d_19}', '{d_20}',
        #  '{d_21}', '{d_22}', '{d_23}', '{d_24}', '{d_25}', '{d_26}', '{d_27}', '{d_28}', '{d_29}', '{d_30}');""")

        # print('i am here 2')

        s.db.commit()

        c_current = (s.sql.execute("SELECT * FROM orders"))
        o_current = s.sql.fetchall()  # o = Orders

        order_number = str(o_current[search_username_new_order(message.from_user.id, o_current)][0])

        # print('order_number', order_number)

        text_to_new_order = 'Появился новый заказ под номером ' + order_number + '\n' + 'Чтобы посмотреть содержимое заказа зайдите в админ-панель и выберите ' + order_number + ' заказ в появившемся списке.'

        # print('i am here 4')

        bot.send_message(message.chat.id,
                         f"Номер вашего заказа - {order_number}! Администратор вскоре его рассмотрит и приготовит",
                         reply_markup=p_markup)
        bot.send_message(message.chat.id,
                         "Также просим вас забрать свой заказ не позже чем через 5 минут от выбранного вами времени!\nМы ценим каждого нашего клиента и хотим обеспечить быстрое обслуживание для всех.",
                         reply_markup=p_markup)
        for i in admin_list:
            bot.send_message(chat_id=admin_id_list[i], text=text_to_new_order)

        s.sql.execute(
            f"""DELETE FROM time WHERE user_id = '{message.from_user.id}';""")
        clear_wishlist(message)
        s.db.commit()
        os.execv(sys.executable, [sys.executable] + sys.argv)


def check_for_search_function1(message):  # поиск товара в меню по сообщению
    markup_for_a_menu_array_formated = [str(i.lower()) for i in markup_for_a_menu_array]
    for i in range(len(markup_for_a_menu_array_formated)):
        if str(message.text.lower()) in markup_for_a_menu_array_formated[i]:
            i_current = search_good_line_in_menu(markup_for_a_menu_array[i])
            good_n = good(s.d[i_current][6], s.d[i_current][2], s.d[i_current][3], s.d[i_current][5])
            return [True, i, good_n]
    return [False, 0, 0]

def check_for_search_function2(call):  # поиск товара в меню по call
    markup_for_a_menu_array_formated = [str(i.lower()) for i in markup_for_a_menu_array]
    for i in range(len(markup_for_a_menu_array_formated)):
        if str(call.data.lower()) in markup_for_a_menu_array_formated[i]:
            i_current = search_good_line_in_menu(markup_for_a_menu_array[i])
            good_n = good(s.d[i_current][6], s.d[i_current][2], s.d[i_current][3], s.d[i_current][5])
            return [True, i, good_n]
    return [False, 0, 0]


def search_function1(message):  # вывод найденного по поиску товара / информирование о том, что товар не найден
    markup_for_search_function1 = ty.ReplyKeyboardMarkup()
    markup_for_search_function1.add(ty.KeyboardButton("Вернуться в Меню"))
    message_formated = str(message.text.lower())
    check_result = check_for_search_function1(message)
    if check_result[0]:  # раздел товара
        markup_for_every_good = ty.ReplyKeyboardMarkup(row_width=1)
        i_current = search_good_line_in_menu(markup_for_a_menu_array[check_result[1]])
        markup_for_every_good.add(ty.KeyboardButton(f"Добавить {s.d[i_current][6]} в корзину"),
                                  ty.KeyboardButton("Вернуться в Меню"),
                                  ty.KeyboardButton("Вернуться в Личный Кабинет"))

        good_line = search_good_line_no_price_in_menu(check_result[2].name)

        if s.d[good_line][4] != None:
            photoimage = s.d[good_line][4]
            writeTofile(photoimage, 'photoo.jpg')
            bot.send_photo(message.chat.id, open('photoo.jpg', 'rb'))

        bot.send_message(message.chat.id, check_result[2].description_info(), reply_markup=markup_for_every_good,
                         parse_mode="html")
    else:
        bot.send_message(message.chat.id,
                         "К сожалению, товара с таким названием в нашем меню нет. Но вы можете зайти в раздел меню и выбрать что-нибудь похожее",
                         reply_markup=markup_for_search_function1)


def sum_price(array_of_goods_ordered):  # функция для подсчета итоговой суммы заказа для администратора
    summary = 0
    for i in array_of_goods_ordered:
        if str(i) == "" or str(i) == " ": continue
        if '/' in str(s.d[search_good_line_no_price_in_menu(i)][3]):
            return int(0)
    for i in array_of_goods_ordered:
        if str(i) == "" or str(i) == " ": continue
        summary += int(s.d[search_good_line_no_price_in_menu(i)][3])
    return summary


def good_name_by_id(id1):  # поиск названия товара по его id в таблице БД для товаров
    for i in s.d:
        if str(i[0]) == str(id1): return i[1]
    return 0


def translate_sql_good_to_index(s):  # перевод названий столбцов в БД в индексы
    if s == 'good1': return 2
    if s == 'good2': return 3
    if s == 'good3': return 4
    if s == 'good4': return 5
    if s == 'good5': return 6
    if s == 'good6': return 7
    if s == 'good7': return 8
    if s == 'good8': return 9
    if s == 'good9': return 10
    if s == 'ood10': return 11


def correct_goods_sequence(message):  # правка последовательности товаров в корзине в БД после удаления товара из корзины
    main_b = (s.sql.execute("SELECT * FROM wishlist"))
    main_w = s.sql.fetchall()
    a = list(main_w[search_username_wishlist(message=message)][2:12])
    b = list(main_w[search_username_wishlist(message=message)][12:])
    #print(a)
    wishlist_converted = ['good1', 'good2', 'good3', 'good4', 'good5', 'good6', 'good7', 'good8', 'good9', 'good10']
    d_converted = ['d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9', 'd10',
                   'd11', 'd12', 'd13', 'd14', 'd15', 'd16', 'd17', 'd18', 'd19', 'd20',
                   'd21', 'd22', 'd23', 'd24', 'd25', 'd26', 'd27', 'd28', 'd29', 'd30']
    l, r, = 0, 0
    while r < len(a):
        if l < r:
            if a[l] in ['', ' '] and a[r] not in ['', ' ']:
                a[l] = a[r]
                s.sql.execute(f"""UPDATE wishlist SET {wishlist_converted[l]} = '{a[r]}'
                                                WHERE username = '{message.from_user.id}'""")
                for j in range(len(b)):
                    #print('b[j] =', b[j], ';   ', 'wishlist_converted[r] =', wishlist_converted[r], 'l =', l)
                    if b[j][-5:] in ['good1', 'good2', 'good3', 'good4', 'good5', 'good6', 'good7', 'good8', 'good9']:
                        if b[j][-5:] == wishlist_converted[r]:
                            #print('d_converted[j] =', d_converted[j])
                            #print('change_good_number_in_dobavka =', change_good_number_in_dobavka(s=b[j], l=l))
                            s.sql.execute(
                                f"""UPDATE wishlist SET {d_converted[j]} = '{change_good_number_in_dobavka(s=b[j], l=l)}'
                            WHERE username = '{message.from_user.id}'""")
                    elif b[j][-6:] == 'good10':
                        if b[j][-6:] == wishlist_converted[r]:
                            s.sql.execute(f"""UPDATE wishlist SET {d_converted[j]} =
                                                        '{change_good_number_in_dobavka(s=b[j], l=l)}'
                                                        WHERE username = '{message.from_user.id}'""")
                a[r] = ''
                s.sql.execute(f"""UPDATE wishlist SET {wishlist_converted[r]} = ''
                                                            WHERE username = '{message.from_user.id}'""")
                l += 1
                r += 1
            elif a[l] in ['', ' '] and a[r] in ['', ' ']:
                r += 1
            elif a[l] not in ['', ' '] and a[r] in ['', ' ']:
                l += 1
                r += 1
            elif a[l] not in ['', ' '] and a[r] not in ['', ' ']:
                l += 1
        else:
            r += 1

    s.db.commit()
    # после каждого использования этой функции
    # нужно прописывать os.execv(sys.executable, [sys.executable] + sys.argv)


def feedback_from_shaurmen(message):  # отправка разработчикам отзывов от сотрудников
    txt = "@" + str(admin_list[0]) + " @" + str(admin_list[1]) + " @" + str(
        admin_list[2]) + "\n\n" + 'Фидбек от шаурменов:\n\n' + message.text
    bot.send_message(chat_id='-1001869223231', text=txt)


def feedback_from_user(message):  # отправка разработчикам отзывов от клиентов
    txt = "@" + str(admin_list[0]) + " @" + str(admin_list[1]) + " @" + str(
        admin_list[2]) + "\n\n" + 'Фидбек от юзеров:\n\n' + message.text
    bot.send_message(chat_id='-1001869223231', text=txt)


def correct_dobavki_sequence(message):  # правка последовательности добавок в корзине в БД после удаления товара из корзины
    main_b = (s.sql.execute("SELECT * FROM wishlist"))
    main_w = s.sql.fetchall()
    a = list(main_w[search_username_wishlist(message=message)][12:])
    d_converted = ['d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9', 'd10',
                   'd11', 'd12', 'd13', 'd14', 'd15', 'd16', 'd17', 'd18', 'd19', 'd20',
                   'd21', 'd22', 'd23', 'd24', 'd25', 'd26', 'd27', 'd28', 'd29', 'd30']
    l, r, = 0, 0
    while r < len(a):
        if l < r:
            if a[l] in ['', ' '] and a[r] not in ['', ' ']:
                a[l] = a[r]
                s.sql.execute(f"""UPDATE wishlist SET {d_converted[l]} = '{a[r]}'
                                                WHERE username = '{message.from_user.id}'""")
                a[r] = ''
                s.sql.execute(f"""UPDATE wishlist SET {d_converted[r]} = ''
                                                            WHERE username = '{message.from_user.id}'""")
                l += 1
                r += 1
            elif a[l] in ['', ' '] and a[r] in ['', ' ']:
                r += 1
            elif a[l] not in ['', ' '] and a[r] in ['', ' ']:
                l += 1
                r += 1
            elif a[l] not in ['', ' '] and a[r] not in ['', ' ']:
                l += 1
        else:
            r += 1

    s.db.commit()
    # после каждого использования этой функции
    # нужно прописывать os.execv(sys.executable, [sys.executable] + sys.argv)


def change_good_number_in_dobavka(s, l):  # формирование названия столбца в БД для l в функции правки последовательности товаров
    if s[-5:] in ['good1', 'good2', 'good3', 'good4', 'good5', 'good6', 'good7', 'good8', 'good9']:
        return s[:-1] + str(l + 1)
    if s[-6:] == 'good10':
        return s[:-2] + str(l + 1)


def del_from_wishlist(message):  # удаление товара из корзины
    cnt_of_goods = wishlist_count(message=message)
    wishlist_converted = ['good1', 'good2', 'good3', 'good4', 'good5', 'good6', 'good7', 'good8', 'good9', 'good10']
    d_converted = ['d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9', 'd10',
                   'd11', 'd12', 'd13', 'd14', 'd15', 'd16', 'd17', 'd18', 'd19', 'd20',
                   'd21', 'd22', 'd23', 'd24', 'd25', 'd26', 'd27', 'd28', 'd29', 'd30']
    a = list(s.w[search_username_wishlist(message=message)][12:])
    b = list(s.w[search_username_wishlist(message=message)][2:12])
    if message.text == 'Я передумал удалять товар из корзины':
        bot.send_message(message.chat.id, "Хорошо!",
                         reply_markup=markup(['Перейти в Корзину']).m)
    else:
        try:
            idx = int(message.text)

            s.sql.execute(f"""UPDATE wishlist SET '{wishlist_converted[idx - 1]}' = ''
                                                        WHERE username = '{message.from_user.id}'""")
            s.db.commit()
            correct_goods_sequence(message=message)
            b3 = (s.sql.execute("SELECT * FROM wishlist"))
            w3 = s.sql.fetchall()  # w = Wishlist

            for i in range(len(d_converted)):
                if wishlist_converted[idx - 1] in [a[i][-5:], a[i][-6:]]:
                    s.sql.execute(f"""UPDATE wishlist SET '{d_converted[i]}' = ''
                         WHERE username = '{message.from_user.id}'""")
                    a[i] = ''
            s.db.commit()
            correct_dobavki_sequence(message=message)
            bot.send_message(message.chat.id, "Товар удален из корзины!",
                             reply_markup=markup(['Перейти в Корзину']).m)
            s.db.commit()

            os.execv(sys.executable, [sys.executable] + sys.argv)
        except:
            try_choosing_again = bot.send_message(message.chat.id,
                                                  "Похоже, товара с таким номером нет в вашей корзине. "
                                                  "Попробуйте выбрать другой номер",
                                                  reply_markup=markup(['Я передумал удалять товар из корзины'] +
                                                                      [str(i) for i in range(1, cnt_of_goods + 1)]).m)
            bot.register_next_step_handler(try_choosing_again, del_from_wishlist)


def wishlist_count(message):  # подсчет количества товаров в корзине
    return len([i for i in s.w[search_username_wishlist(message)][2:12] if i not in ['', ' ']])


def search_time_line(message):  # поиск в БД time строки с временем заказа пользователя по id пользователя
    s.time1 = s.sql.execute("SELECT * FROM time")
    s.t = s.sql.fetchall()
    for i in s.t:
        if i[0] == str(message.from_user.id):
            return s.t.index(i)


def dobavki_max_is_not_met(message, bd_good_number):  # проверка недостижения максимального количества добавок к шаурме
    d_converted = ['d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9', 'd10',
                   'd11', 'd12', 'd13', 'd14', 'd15', 'd16', 'd17', 'd18', 'd19', 'd20',
                   'd21', 'd22', 'd23', 'd24', 'd25', 'd26', 'd27', 'd28', 'd29', 'd30']
    a = list(s.w[search_username_wishlist(message=message)][12:])
    #print('this is a =', a)
    cnt = 0
    for i in range(len(d_converted)):
        if bd_good_number in [a[i][-5:], a[i][-6:]]:
            cnt += 1
        if cnt >= 5:
            return False
    return True


def shaurma_max_is_not_met(message):  # проверка недостижения максимального количества шаурм в корзине
    a = list(s.w[search_username_wishlist(message=message)][2:12])
    cnt = 0
    for i in a:
        if 'Шаурма' in i:
            cnt += 1
        if cnt >= 5:
            return False
    return True


def zakaz_goods_only_sum(message):  # вычисление суммарной стоимости только товаров в корзине
    goods_ordered = s.w[search_username_wishlist(message)][2:12]
    goods_ordered = [i for i in goods_ordered if i not in ['', ' ']]
    prices = [s.d[search_good_line_no_price_in_menu(i)][3] for i in goods_ordered]
    return sum(prices)


@bot.message_handler(commands=['start'])
def start_message(a):  # реакиця на команду start
    choice_ids12 = (s.sql.execute("SELECT * FROM choice_ids"))
    choice_ids2 = s.sql.fetchall()
    try:
        bot.delete_message(chat_id=a.chat.id,
                           message_id=choice_ids2[search_username_choice_ids(a.from_user.id)][1])
    except:
        pass

    markup1 = ty.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    menu1 = ty.KeyboardButton("Меню")
    menu2 = ty.KeyboardButton("Информация")
    menu3 = ty.KeyboardButton("Корзина")
    markup1.add(menu1, menu2, menu3)
    if a.chat.username == 'shaurlandia':
        print(a.from_user.id)
    bot.send_message(a.chat.id,
                     'Привет, {0.first_name}! Я - телеграм-бот <b>Шаурляндии</b>. Добро пожаловать в чат со мной. Что Вас интересует?'.format(
                         a.from_user, bot.get_me()), parse_mode="html",
                     reply_markup=markup1)  # второй аргумент - то, что отправляет бот.
    if a.from_user.id not in [i[2] for i in s.osi2]:
        s.sql.execute(f"""INSERT INTO order_string_id(only, shaurma_name_for_dobavki, user_id)
                                       VALUES('{s.order_string_id}', '', '{a.from_user.id}');""")
        s.db.commit()
        os.execv(sys.executable, [sys.executable] + sys.argv)


@bot.message_handler(commands=['admin'])
def admin_panel(m):  # реакция на команду admin
    choice_ids12 = (s.sql.execute("SELECT * FROM choice_ids"))
    choice_ids2 = s.sql.fetchall()
    try:
        bot.delete_message(chat_id=m.chat.id,
                           message_id=choice_ids2[search_username_choice_ids(m.from_user.id)][1])
    except:
        pass
    bot.send_message(m.chat.id, "Пароль:".format(m.from_user, bot.get_me()))
    markup_admin_wishlists = ty.ReplyKeyboardMarkup(row_width=1)
    for i in range(len(list(s.o))):
        markup_admin_wishlists.add(ty.KeyboardButton(f"Заказ №{s.o[i][0]} - {s.o[i][12]}"))
    markup_admin_wishlists.add(ty.KeyboardButton("Вернуться в Админ-Панель"))


@bot.message_handler(content_types=['text'])
def reply_to_text(message):  # реакция на любой текст, присылаемый пользователем
    choice_ids12 = (s.sql.execute("SELECT * FROM choice_ids"))
    choice_ids2 = s.sql.fetchall()
    try:
        bot.delete_message(chat_id=message.chat.id,
                           message_id=choice_ids2[search_username_choice_ids(message.from_user.id)][1])
    except:
        pass
    global che1
    global menu_id
    markup2 = ty.ReplyKeyboardMarkup(row_width=1)
    wishlist_string_id = 3

    markup2.add(ty.KeyboardButton("Поиск по названию товара"))
    for i in s.d:
        markup_for_a_menu_array.append(ty.KeyboardButton(f"{str(i[1])}").text)
        markup2.add(ty.KeyboardButton(str(i[1])))
        markup_put_smth_in_wishlist.append(ty.KeyboardButton(f"Добавить {s.d[search_good_line_in_menu(str(i[1]))][6]}"
                                                             f" в корзину").text)
        #print(markup_put_smth_in_wishlist)
        markup_put_smth_in_wishlist_again.append(ty.KeyboardButton(f"Повторно добавить"
                                                                   f" {s.d[search_good_line_in_menu(str(i[1]))][6]}"
                                                                   f" в корзину").text)

    markup2.add(ty.KeyboardButton("Вернуться в Личный Кабинет"))
    address = [message.from_user.id, '']

    if check_username_wishlist(message) == False:  # заведение корзины в случае, если у пользователя ее еще нет
        s.sql.execute(f"""INSERT INTO wishlist(id, username, good1, good2, good3, good4, good5, good6, good7, good8, good9, good10, d1, d2, d3, d4, d5,
           d6, d7, d8, d9, d10,
    d11, d12, d13, d14, d15, d16, d17, d18, d19, d20, d21, d22, d23, d24, d25, d26, d27, d28, d29, d30)
                          VALUES('{s.w[-1][0] + 1}', '{message.from_user.id}', '', '', '', '', '', '', '', '', '',
                           '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                           '', '', '', '', '', '', '', '', '', '', '', '', '', '', '');""")
        s.db.commit()
        s.b = (s.sql.execute("SELECT * FROM wishlist"))
        s.w = s.sql.fetchall()

    if message.chat.type == 'private':
        if message.text == "Меню" or message.text == "Вернуться в Меню":  # раздел меню
            s.a = (s.sql.execute("SELECT * FROM goods"))
            s.d = s.sql.fetchall()

            menu_ids12 = (s.sql.execute("SELECT * FROM menu_ids"))
            menu_ids2 = s.sql.fetchall()
            try:
                bot.delete_message(chat_id=message.chat.id,
                                   message_id=menu_ids2[search_username_menu_ids(message.from_user.id)][1])
            except:
                pass

            new_menu_markup = ty.InlineKeyboardMarkup(row_width=2)
            new_everything_else_in_menu_markup = ty.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            new_everything_else_in_menu_markup.add(ty.KeyboardButton("Личный Кабинет"))
            new_everything_else_in_menu_markup.add(ty.KeyboardButton("Поиск"))
            for i in s.d:
                if str(i[5]) != "Добавки":
                    if str(i[5]) in ["Горячие блюда из птицы", "Вегетарианское меню"]:
                        new_menu_markup.add(ty.InlineKeyboardButton(str(i[1]), callback_data=str(i[0])))
                    new_menu_markup_in_array.append(str(i[0]))
            new_menu_markup.add(
                ty.InlineKeyboardButton("🍗 Горячие блюда из птицы", callback_data='hot_dishes_with_chicken'))
            new_menu_markup.add(
                ty.InlineKeyboardButton("🌱 Вегетарианское меню", callback_data='vegan_menu'))
            new_menu_markup.add(
                ty.InlineKeyboardButton("☕️ Горячие напитки", callback_data='hot_drinks'))
            new_menu_markup.add(
                ty.InlineKeyboardButton("🥤 Холодные напитки", callback_data='cold_drinks'))

            menu = bot.send_message(message.chat.id, "Наше меню:", reply_markup=new_menu_markup)
            menu_id = int(str(menu).split(',')[2].split(' ')[-1])

            checker_menu_id = False
            for i in s.menu_ids:
                if str(i[0]) == str(message.from_user.id):
                    checker_menu_id = True
            if not checker_menu_id:
                s.sql.execute(f"""INSERT INTO menu_ids(username, menu_id)
                                                               VALUES('{message.from_user.id}', {menu_id});""")
                s.db.commit()
            else:
                s.sql.execute(
                    f"""UPDATE menu_ids SET menu_id = {menu_id} WHERE username = '{message.from_user.id}'""")
                s.db.commit()

            bot.send_message(message.chat.id,
                             "Вы также можете найти конкретный товар с помощью кнопки в нижней части экрана",
                             reply_markup=new_everything_else_in_menu_markup)

            wishlist_string_id += 1

        elif message.text in ["Поиск по названию товара", "Поиск"]:  # начало поиска по названию товара
            search_p1 = bot.send_message(message.chat.id, "Введите название товара, который вы хотите найти",
                                         reply_markup=ty.ReplyKeyboardRemove())
            bot.register_next_step_handler(search_p1, search_function1)

        elif message.text == 'Я передумал удалять товар из корзины':  # отмена удаления товара из корзины
            bot.send_message(message.chat.id, "Хорошо!", reply_markup=markup(['Перейти в Корзину']).m)

        elif message.text in ["Вернуться в Личный Кабинет", "Выйти из Админ-Панели", "Личный Кабинет"]:  # возвращение в личный кабинет
            menu_ids12 = (s.sql.execute("SELECT * FROM menu_ids"))
            menu_ids2 = s.sql.fetchall()
            try:
                bot.delete_message(chat_id=message.chat.id,
                                   message_id=menu_ids2[search_username_menu_ids(message.from_user.id)][1])
            except:
                pass
            markup1 = ty.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
            menu1 = ty.KeyboardButton("Меню")
            menu2 = ty.KeyboardButton("Информация")
            menu3 = ty.KeyboardButton("Корзина")
            markup1.add(menu1, menu2, menu3)
            bot.send_message(message.chat.id, "Вы находитесь в Личном Кабинете. Выберите действие:", parse_mode="html",
                             reply_markup=markup1)
        elif message.text == 'Оставить отзыв':  # если пользователь хочет написать отзыв
            msg = bot.reply_to(message, "Напишите ваш отзыв сообщением в чат")
            bot.register_next_step_handler(msg, feedback_from_user)
        elif message.text == "Информация":  # раздел с информацией о точке
            place_info = cafe("Москва, улица Шаболовка, 30/12",
                              "<b>Время работы:</b> \nКруглосуточно \n \n<b>Контакты:</b> "
                              "\nНомер телефона: +7 (925) 051-80-91 \n\n<b>Как пройти:</b>",
                              open('location.jpeg', 'rb'), open('food_photo.jpeg', 'rb'))
            bot.send_message(message.chat.id, place_info.description, parse_mode="html", reply_markup=just_lk_markup)
            bot.send_photo(message.chat.id, place_info.location)

        elif message.text == "Удалить товар из корзины":  # удаление товара из корзины
            cnt_of_goods = wishlist_count(message=message)
            number_choice = bot.send_message(message.chat.id,
                                             "Пожалуйста, выберите номер товара, который вы хотите удалить "
                                             "(номер отображается в корзине)",
                                             reply_markup=markup(
                                                 ['Я передумал удалять товар из корзины'] + [str(i) for i in range(1,
                                                                                                                   cnt_of_goods + 1)]).m)
            bot.register_next_step_handler(number_choice, del_from_wishlist)

        elif message.text in ['Корзина', 'Перейти в Корзину']:  # раздел виш-листа (списка "избранное" / корзины)
            just_menu_markup = ty.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            just_menu_markup.add(ty.KeyboardButton("Меню"))
            just_menu_markup.add(ty.KeyboardButton("Личный Кабинет"))
            if check_username_wishlist(message) == False:
                bot.send_message(message.chat.id, 'Ваша корзина пуста\nЧтобы добавить товар, зайдите в раздел "Меню"',
                                 reply_markup=just_menu_markup)
                os.execv(sys.executable, [sys.executable] + sys.argv)
            markup4 = markup(["Очистить корзину", "Удалить товар из корзины",
                              "Сделать заказ", "Личный Кабинет"])
            wishlist_in_string = ''
            summa_korzina = 0
            for k in range(2, 12):
                i = s.w[search_username_wishlist(message)][k]
                if i == '' or i == ' ': continue
                wishlist_in_string += f'{k - 1}. ' + str(i)
                current_i_price = int(s.d[search_good_line_no_price_in_menu(i)][3])
                summa_korzina += current_i_price
                wishlist_in_string += ' ' + str(current_i_price) + '₽'
                wishlist_in_string += '\n'
                for j in s.w[search_username_wishlist(message)][12:]:
                    if translate_sql_good_to_index(j[-5:]) == k:
                        dobavka = j[:-5]
                        #print(dobavka)
                        if dobavka[-1] == 'g':
                            dobavka = dobavka[:-2]
                        else:
                            dobavka = dobavka[:-1]
                        wishlist_in_string += '     ' + str(dobavka) + ' ' + \
                                              str(s.d[search_good_line_no_price_in_menu(
                                                  s.d[search_good_line_no_price_in_menu(dobavka)][6])][3]) + '₽\n'
                        summa_korzina += int(
                            s.d[search_good_line_no_price_in_menu(s.d[search_good_line_no_price_in_menu(dobavka)][6])][
                                3])
            if wishlist_in_string == '' or wishlist_in_string == ' ':
                bot.send_message(message.chat.id, 'Ваша корзина пуста\nЧтобы добавить товар, зайдите в раздел "Меню"',
                                 reply_markup=just_menu_markup)
            else:
                wishlist_in_string = '<b>Товары в корзине:</b>\n' + wishlist_in_string
                wishlist_in_string += f'\n<b>Итого:</b> {summa_korzina}₽'
                bot.send_message(message.chat.id, wishlist_in_string, reply_markup=markup4.m, parse_mode="html")
            os.execv(sys.executable, [sys.executable] + sys.argv)

        elif message.text in markup_put_smth_in_wishlist or message.text in markup_put_smth_in_wishlist_again:  # добавление товара в корзину
            #print('AOAOAOAOOAOA')
            if message.text in markup_put_smth_in_wishlist:
                good_name_from_m_text = message.text[9:-10]
            else:
                good_name_from_m_text = message.text[18:-10]
            if wishlist_count(message=message) >= 10:
                bot.send_message(message.chat.id, "Вы уже добавили в корзину максимальное число товаров (10)")
            else:
                if 'Шаурма' in message.text:
                    if shaurma_max_is_not_met(message=message):
                        new_yes_or_no_markup = ty.InlineKeyboardMarkup()
                        new_yes_or_no_markup.add(ty.InlineKeyboardButton('Да', callback_data='yes_choice'))
                        new_yes_or_no_markup.add(ty.InlineKeyboardButton('Нет', callback_data='no_choice'))
                        yes_or_no_choice = bot.send_message(message.from_user.id, "Хотите выбрать добавки к шаурме?",
                                                            reply_markup=new_yes_or_no_markup)
                        s.sql.execute(
                            f"""UPDATE order_string_id SET shaurma_name_for_dobavki = '{good_name_from_m_text}'
                            WHERE user_id = '{message.from_user.id}'""")
                        s.db.commit()
                        s.sql.execute(
                            f"""UPDATE wishlist SET {search_for_last_free_db_space(message)} = '{good_name_from_m_text}'
                             WHERE username = '{message.from_user.id}'""")

                        s.db.commit()

                        choice_id = int(str(yes_or_no_choice).split(',')[2].split(' ')[-1])
                        checker_choice_id = False
                        for i in s.choice_ids:
                            if str(i[0]) == str(message.from_user.id):
                                checker_choice_id = True
                        if not checker_choice_id:
                            s.sql.execute(f"""INSERT INTO choice_ids(username, choice_id)
                                                    VALUES('{message.from_user.id}', {choice_id});""")
                            s.db.commit()
                        else:
                            s.sql.execute(
                                f"""UPDATE choice_ids SET choice_id = {choice_id}
                                WHERE username = '{message.from_user.id}'""")
                            s.db.commit()

                        os.execv(sys.executable, [sys.executable] + sys.argv)
                    else:
                        bot.send_message(message.chat.id, "Вы выбрали максимальное число порций шаурмы (5)")
                else:
                    markup_for_every_good = ty.ReplyKeyboardMarkup(row_width=1)
                    markup_for_every_good.add(ty.KeyboardButton(f"Повторно добавить"
                                                                f" {s.d[search_good_line_no_price_in_menu(good_name_from_m_text)][6]}"
                                                                f" в корзину"),
                                              ty.KeyboardButton("Вернуться в Меню"),
                                              ty.KeyboardButton("Вернуться в Личный Кабинет"),
                                              ty.KeyboardButton("Перейти в Корзину"))

                    s.sql.execute(
                        f"""UPDATE wishlist SET {search_for_last_free_db_space(message)} = '{good_name_from_m_text}'
                        WHERE username = '{message.from_user.id}'""")
                    s.db.commit()

                    bot.send_message(message.chat.id, "Готово!", reply_markup=markup_for_every_good)
                    menu_ids12 = (s.sql.execute("SELECT * FROM menu_ids"))
                    menu_ids2 = s.sql.fetchall()
                    try:
                        bot.delete_message(chat_id=message.chat.id,
                                           message_id=menu_ids2[search_username_menu_ids(message.from_user.id)][1])
                    except:
                        pass
                    os.execv(sys.executable, [sys.executable] + sys.argv)

        elif message.text == "Завершить выбор добавок":  # пользователь обозначает, что больше не будет выбирать добавки к текущему товару
            menu_or_lk_markup = markup(['Меню', 'Вернуться в Личный Кабинет', 'Перейти в Корзину'])
            bot.send_message(message.chat.id, "Готово! Шаурма и добавки к ней уже в вашей корзине",
                             reply_markup=menu_or_lk_markup.m)
            menu_ids12 = (s.sql.execute("SELECT * FROM menu_ids"))
            menu_ids2 = s.sql.fetchall()
            try:
                bot.delete_message(chat_id=message.chat.id,
                                   message_id=menu_ids2[search_username_menu_ids(message.from_user.id)][1])
            except:
                pass
            os.execv(sys.executable, [sys.executable] + sys.argv)

        elif message.text == "Очистить корзину":  # начало процесса очистки виш-листа
            clear_wishlist(message)
            bot.send_message(message.chat.id, "Корзина очищена", reply_markup=just_lk_markup)
            s.db.commit()
            os.execv(sys.executable, [sys.executable] + sys.argv)

        elif message.text == "Изменить содержимое заказа":  # изменение списка товаров в корзине
            if wishlist_count(message=message) == 0:
                bot.send_message(message.chat.id, 'Ваша корзина пуста\nЧтобы добавить товар, зайдите в раздел "Меню"',
                                 reply_markup=markup(["Меню"]).m)
            else:
                bot.send_message(message.chat.id, "Чтобы добавить новый товар в корзину, "
                                                  "зайдите в раздел меню. Чтобы удалить товар из корзины, "
                                                  "нажмите соответствующую кнопку в разделе Корзина",
                                 reply_markup=markup(["Вернуться в Меню", "Перейти в Корзину"]).m)
            try:
                #print('ok')
                #print(invoice_message)
                bot.delete_message(chat_id=message.chat.id,
                                   message_id=invoice_message)
            except:
                pass
        elif message.text == 'Отменить и очистить заказ':  # полный сброс заказа вплоть до очистки корзины
            clear_wishlist(message)
            bot.send_message(message.chat.id, "Заказ отменен и корзина очищена. Ждем вас снова!",
                             reply_markup=just_lk_markup)
            try:
                bot.delete_message(chat_id=message.chat.id,
                                   message_id=invoice_id)
            except:
                pass
            os.execv(sys.executable, [sys.executable] + sys.argv)

        elif message.text == "Сделать заказ":  # начало заказа виш-листа
            if check_username_wishlist(message) == False:
                bot.send_message(message.chat.id, "Ваша корзина пуста. Перейдите в меню, чтобы добавить в нее товары",
                                 reply_markup=markup(['Меню']).m)
            else:
                if zakaz_goods_only_sum(message) < 89:
                    bot.send_message(message.chat.id,
                                     "Простите, но минимальная сумма заказа через бота - 89 рублей. Пожалуйста, "
                                     "перейдите в меню, чтобы добрать товаров до необходимой стоимости",
                                     reply_markup=markup(['Меню']).m)
                else:
                    if check_username_order(message) == False:
                        no_cancel_change_order = markup(
                            ['Комментариев нет', 'Отменить и очистить заказ', 'Изменить содержимое заказа'])

                        peremennaya = bot.send_message(message.chat.id, "У вас остались пожелания по заказу? "
                                                                        "Воспользуйтесь одной из кнопок внизу"
                                                                        " экрана или "
                                                                        "отправьте сообщение"
                                                                        " с вашим комментарием в чат",
                                                       reply_markup=no_cancel_change_order.m, parse_mode='html')

                        bot.register_next_step_handler(peremennaya, comments_handler, message.from_user.id)
                    else:
                        bot.send_message(message.chat.id,
                                         "Вы уже сделали заказ! "
                                         "Для оформления нового заказа необходимо получить Ваш нынешний заказ")

        elif (
                message.text == "1234567890" or message.text == "Вернуться в Админ-Панель") and message.from_user.username in admin_list:  # вход в админ-панель по паролю и проверке username пользователя (администратора)
            markup_admin_1 = ty.ReplyKeyboardMarkup(row_width=1)
            admin_btn = ty.KeyboardButton("Заказы")
            markup_admin_1.add(admin_btn, ty.KeyboardButton("Выйти из Админ-Панели"),
                               ty.KeyboardButton('Обратная связь'))

            bot.send_message(message.chat.id,
                             'Добро пожаловать в админ-панель, <i>{0.first_name}</i>!'.format(message.from_user,
                                                                                              bot.get_me()),
                             parse_mode="html", reply_markup=markup_admin_1)

        elif message.text == "Заказы" and message.from_user.username in admin_list:  # просмотр списка заказов виш-листов
            markup_admin_wishlists = ty.ReplyKeyboardMarkup(row_width=1)
            for i in range(len(list(s.o))):
                markup_admin_wishlists.add(ty.KeyboardButton(f"Заказ №{s.o[i][0]} - {s.o[i][12]}"))
                markup_admin_wishlists_array.append(ty.KeyboardButton(f"Заказ №{s.o[i][0]} - {s.o[i][12]}").text)
                markup_admin_delete_order_list.append(f"Заказ №{s.o[i][0]} выдан")
            markup_admin_wishlists.add("Вернуться в Админ-Панель")
            bot.send_message(message.chat.id, "Список заказов:", reply_markup=markup_admin_wishlists)
        elif message.text == 'Обратная связь' and message.from_user.username in admin_list:  # обратная связь для администраторов
            markup_admin_wishlists = ty.ReplyKeyboardMarkup(row_width=1)
            markup_admin_wishlists.add("Вернуться в Админ-Панель")
            msg2 = bot.reply_to(message, 'Опишите свою проблему и мы решим её в кратчайшие сроки!')
            bot.register_next_step_handler(msg2, feedback_from_shaurmen)

        elif message.text in markup_admin_wishlists_array and message.from_user.username in admin_list:  # просмотр выбранного заказа виш-листа
            full_order_info = ""
            summa_order = 0
            for k in range(len(s.o[markup_admin_wishlists_array.index(message.text)][:14])):
                i = s.o[markup_admin_wishlists_array.index(message.text)][k]
                markup_admin_for_order_list = ty.ReplyKeyboardMarkup(row_width=1)
                markup_admin_for_order_list.add(
                    ty.KeyboardButton(f"Заказ №{s.o[markup_admin_wishlists_array.index(message.text)][0]} выдан"))
                if (i == "" or i == " ") and (
                        s.o[markup_admin_wishlists_array.index(message.text)].index(i) != 11): continue
                if s.o[markup_admin_wishlists_array.index(message.text)].index(i) == 0:
                    full_order_info += "<b>Номер заказа:</b> "
                    full_order_info += str(i)
                if s.o[markup_admin_wishlists_array.index(message.text)].index(i) == 1:
                    full_order_info += "<b>ID пользователя:</b> "
                    full_order_info += str(i)
                    full_order_info += "\n"
                    full_order_info += "\n"
                    full_order_info += "<b>Список заказанных товаров:</b>"
                if s.o[markup_admin_wishlists_array.index(message.text)].index(i) >= 2 and s.o[
                    markup_admin_wishlists_array.index(message.text)].index(i) <= 11:
                    full_order_info += str(i) + " " + str(s.d[search_good_line_no_price_in_menu(i)][3]) + "₽"
                    try:
                        for j in s.o[search_username_order(message.from_user.id)][14:]:
                            if translate_sql_good_to_index(j[-5:]) == k:
                                dobavka = j[:-5]
                                #print(dobavka)
                                if dobavka[-1] == 'g':
                                    dobavka = dobavka[:-2]
                                else:
                                    dobavka = dobavka[:-1]
                                full_order_info += '\n' + '     ' + str(dobavka) + ' ' + \
                                                   str(s.d[search_good_line_no_price_in_menu(dobavka)][3]) + '₽'
                                summa_order += int(s.d[search_good_line_no_price_in_menu(dobavka)][3])
                    except TypeError:
                        print('type error in printing dobavki for admin')
                if s.o[markup_admin_wishlists_array.index(message.text)].index(i) == 12:
                    full_order_info += ("\n")
                    full_order_info += f"Общая стоимость заказа: {sum_price([i for i in s.o[markup_admin_wishlists_array.index(message.text)][2:12]]) + summa_order}₽"
                    full_order_info += ("\n")
                    full_order_info += "<b>Время заказа:</b> "
                    full_order_info += str(i)
                if s.o[markup_admin_wishlists_array.index(message.text)].index(i) == 13:
                    full_order_info += "<b>Комментарии к заказу:</b> "
                    full_order_info += str(i)

                full_order_info += "\n"
            markup_admin_for_order_list.add("Вернуться в Админ-Панель")
            bot.send_message(message.chat.id, full_order_info, parse_mode="html",
                             reply_markup=markup_admin_for_order_list)
            summa_order = 0
        elif message.text in markup_admin_delete_order_list:  # Удаление выданного заказа после его выдачи
            s.sql.execute(
                f"""DELETE FROM orders WHERE ID = '{s.o[markup_admin_delete_order_list.index(message.text)][0]}';""")
            s.sql.execute(
                f"""DELETE FROM dobavki WHERE user_id = '{s.o[markup_admin_delete_order_list.index(message.text)][1]}';""")
            s.sql.execute(
                f"""DELETE FROM order_string_id WHERE user_id = '{s.o[markup_admin_delete_order_list.index(message.text)][1]}';""")
            s.db.commit()
            bot.send_message(message.chat.id, "Выбранный заказ удален",
                             reply_markup=markup(["Вернуться в Админ-Панель"]).m)
            os.execv(sys.executable, [sys.executable] + sys.argv)


@bot.callback_query_handler(func=lambda call: True)
def inline_markups(
        call):  # реакция бота на нажатия пользователем кнопок на клавиатурах внутри сообщений (под сообщениями)
    choice_ids12 = (s.sql.execute("SELECT * FROM choice_ids"))
    choice_ids2 = s.sql.fetchall()
    try:
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=choice_ids2[search_username_choice_ids(call.from_user.id)][1])
    except:
        pass
    global menu_id
    # try:
    if call.message:
        #print(call.data)
        #print(new_menu_markup_in_array)
        if 'add' in str(call.data):  # добавление очередной добавки к товару
            #print('check this ', last_unfree_db_space(message=call))
            if dobavki_max_is_not_met(message=call, bd_good_number=(last_unfree_db_space(message=call))):
                s.sql.execute(
                    f"""UPDATE wishlist SET {search_for_last_free_dobavki_space(call)} =
                    '{str(call.data)[:-3] + ' ' + last_unfree_db_space(call)}' WHERE username = '{call.from_user.id}'""")
                s.db.commit()

                bot.send_message(call.from_user.id, "Добавка выбрана!")

                os.execv(sys.executable, [sys.executable] + sys.argv)
            else:
                bot.send_message(call.from_user.id, "Вы выбрали максимальное "
                                                    "число добавок для одной шаурмы (5)")

        elif str(call.data) in new_menu_markup_in_array:  # отображение страницы (раздела) товара
            #print("товары символы: ")
            #for j in [(i[1], 32 - len(i[1])) for i in s.d]: print(j)
            good_n_name = good_name_by_id(call.data)
            markup_for_every_good = ty.ReplyKeyboardMarkup(row_width=1)
            i_current = search_good_line_in_menu(good_n_name)
            markup_for_every_good.add(ty.KeyboardButton(f"Добавить {s.d[i_current][6]} в корзину"),
                                      ty.KeyboardButton("Вернуться в Меню"),
                                      ty.KeyboardButton("Вернуться в Личный Кабинет"))

            good_line = search_good_line_in_menu_by_idx(int(call.data))
            #print(call.data)
            #print(type(call.data))
            #print(good_line)

            if s.d[good_line][4] != None:
                photoimage = s.d[good_line][4]
                writeTofile(photoimage, 'photoo.jpg')
                bot.send_photo(call.message.chat.id, open('photoo.jpg', 'rb'))


            good_n = good(s.d[i_current][6], s.d[i_current][2], s.d[i_current][3], s.d[i_current][5])

            bot.send_message(call.message.chat.id, good_n.description_info(), reply_markup=markup_for_every_good,
                             parse_mode="html")

        elif str(call.data) == "yes_choice":  # ситуация, в которой пользователь хочет добавить к товару добавки
            add_dobavki_markup = ty.InlineKeyboardMarkup()
            for i in s.d:
                if str(i[5]) == "Добавки": add_dobavki_markup.add(
                    ty.InlineKeyboardButton(str(i[1]), callback_data=str(i[6]) + 'add'))
            dobavki_menu = bot.send_message(call.message.chat.id, "Список возможных добавок: ",
                                            reply_markup=add_dobavki_markup)
            no_more_dobavki = markup(['Завершить выбор добавок'])
            bot.send_message(call.message.chat.id,
                             "Всего для одной шаурмы может выбрано не более 5 добавок",
                             reply_markup=no_more_dobavki.m)
            menu_ids12 = (s.sql.execute("SELECT * FROM menu_ids"))
            menu_ids2 = s.sql.fetchall()
            try:
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=menu_ids2[search_username_menu_ids(call.from_user.id)][1])
            except:
                pass
            dobavki_menu_id = int(str(dobavki_menu).split(',')[2].split(' ')[-1])

            checker_menu_id = False
            for i in s.menu_ids:
                if str(i[0]) == str(call.from_user.id):
                    checker_menu_id = True
            if not checker_menu_id:
                s.sql.execute(f"""INSERT INTO menu_ids(username, menu_id)
                                                                           VALUES('{call.from_user.id}', {dobavki_menu_id});""")
                s.db.commit()
            else:
                s.sql.execute(
                    f"""UPDATE menu_ids SET menu_id = {dobavki_menu_id} WHERE username = '{call.from_user.id}'""")
                s.db.commit()

            choice_ids12 = (s.sql.execute("SELECT * FROM choice_ids"))
            choice_ids2 = s.sql.fetchall()
            try:
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=choice_ids2[search_username_choice_ids(call.from_user.id)][1])
            except:
                pass

        elif str(call.data) == "no_choice":  # ситуация, в которой пользователь не хочет добавлять к товару добавки
            menu_or_lk_markup = markup(['Меню', 'Вернуться в Личный Кабинет', 'Перейти в Корзину'])

            bot.send_message(call.message.chat.id, "Хорошо! Шаурма (без дополнительных добавок) уже в вашей корзине",
                             reply_markup=menu_or_lk_markup.m)
            menu_ids12 = (s.sql.execute("SELECT * FROM menu_ids"))
            menu_ids2 = s.sql.fetchall()
            try:
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=menu_ids2[search_username_menu_ids(call.from_user.id)][1])
            except:
                pass

            choice_ids12 = (s.sql.execute("SELECT * FROM choice_ids"))
            choice_ids2 = s.sql.fetchall()
            try:
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=choice_ids2[search_username_choice_ids(call.from_user.id)][1])
            except:
                pass

            os.execv(sys.executable, [sys.executable] + sys.argv)

        elif str(call.data) == 'hot_dishes_with_chicken':  # фильтр по одной из категорий товаров
            menu_markup_f1 = ty.InlineKeyboardMarkup()
            for i in s.d:
                if str(i[5]) == "Горячие блюда из птицы": menu_markup_f1.add(
                    ty.InlineKeyboardButton(str(i[1]), callback_data=str(i[0])))
            filter_menu = bot.send_message(call.message.chat.id, "Вот отфильтрованное по вашим параметрам меню",
                                           reply_markup=menu_markup_f1)
            lk_and_menu_markup = markup(['Вернуться в Меню', 'Вернуться в Личный Кабинет'])
            bot.send_message(call.message.chat.id, "Чтобы вернуться в начальное меню, нажмите на кнопку внизу экрана",
                             reply_markup=lk_and_menu_markup.m)
            menu_ids12 = (s.sql.execute("SELECT * FROM menu_ids"))
            menu_ids2 = s.sql.fetchall()
            try:
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=menu_ids2[search_username_menu_ids(call.from_user.id)][1])
            except:
                pass

            filter_menu_id = int(str(filter_menu).split(',')[2].split(' ')[-1])

            checker_menu_id = False
            for i in s.menu_ids:
                if str(i[0]) == str(call.from_user.id):
                    checker_menu_id = True
            if not checker_menu_id:
                s.sql.execute(f"""INSERT INTO menu_ids(username, menu_id)
                VALUES('{call.from_user.id}', {filter_menu_id});""")
                s.db.commit()
            else:
                s.sql.execute(
                    f"""UPDATE menu_ids SET menu_id = {filter_menu_id} WHERE username = '{call.from_user.id}'""")
                s.db.commit()

        elif str(call.data) == 'vegan_menu':  # фильтр по одной из категорий товаров
            menu_markup_f1 = ty.InlineKeyboardMarkup()
            for i in s.d:
                if str(i[5]) == "Вегетарианское меню": menu_markup_f1.add(
                    ty.InlineKeyboardButton(str(i[1]), callback_data=str(i[0])))
            filter_menu = bot.send_message(call.message.chat.id, "Вот отфильтрованное по вашим параметрам меню",
                                           reply_markup=menu_markup_f1)
            lk_and_menu_markup = markup(['Вернуться в Меню', 'Вернуться в Личный Кабинет'])
            bot.send_message(call.message.chat.id, "Чтобы вернуться в начальное меню, нажмите на кнопку внизу экрана",
                             reply_markup=lk_and_menu_markup.m)
            menu_ids12 = (s.sql.execute("SELECT * FROM menu_ids"))
            menu_ids2 = s.sql.fetchall()
            try:
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=menu_ids2[search_username_menu_ids(call.from_user.id)][1])
            except:
                pass

            filter_menu_id = int(str(filter_menu).split(',')[2].split(' ')[-1])

            checker_menu_id = False
            for i in s.menu_ids:
                if str(i[0]) == str(call.from_user.id):
                    checker_menu_id = True
            if not checker_menu_id:
                s.sql.execute(f"""INSERT INTO menu_ids(username, menu_id)
                            VALUES('{call.from_user.id}', {filter_menu_id});""")
                s.db.commit()
            else:
                s.sql.execute(
                    f"""UPDATE menu_ids SET menu_id = {filter_menu_id} WHERE username = '{call.from_user.id}'""")
                s.db.commit()

        elif str(call.data) == 'hot_drinks':  # фильтр по одной из категорий товаров
            menu_markup_f1 = ty.InlineKeyboardMarkup()
            for i in s.d:
                if str(i[5]) == "Горячие напитки": menu_markup_f1.add(
                    ty.InlineKeyboardButton(str(i[1]), callback_data=str(i[0])))
            filter_menu = bot.send_message(call.message.chat.id, "Вот отфильтрованное по вашим параметрам меню",
                                           reply_markup=menu_markup_f1)
            lk_and_menu_markup = markup(['Вернуться в Меню', 'Вернуться в Личный Кабинет'])
            bot.send_message(call.message.chat.id, "Чтобы вернуться в начальное меню, нажмите на кнопку внизу экрана",
                             reply_markup=lk_and_menu_markup.m)

            menu_ids12 = (s.sql.execute("SELECT * FROM menu_ids"))
            menu_ids2 = s.sql.fetchall()
            try:
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=menu_ids2[search_username_menu_ids(call.from_user.id)][1])
            except:
                pass

            filter_menu_id = int(str(filter_menu).split(',')[2].split(' ')[-1])

            checker_menu_id = False
            for i in s.menu_ids:
                if str(i[0]) == str(call.from_user.id):
                    checker_menu_id = True
            if not checker_menu_id:
                s.sql.execute(f"""INSERT INTO menu_ids(username, menu_id)
                            VALUES('{call.from_user.id}', {filter_menu_id});""")
                s.db.commit()
            else:
                s.sql.execute(
                    f"""UPDATE menu_ids SET menu_id = {filter_menu_id} WHERE username = '{call.from_user.id}'""")
                s.db.commit()

        elif str(call.data) == 'cold_drinks':  # фильтр по одной из категорий товаров
            menu_markup_f1 = ty.InlineKeyboardMarkup()
            for i in s.d:
                if str(i[5]) == "Холодные напитки": menu_markup_f1.add(
                    ty.InlineKeyboardButton(str(i[1]), callback_data=str(i[0])))
            filter_menu = bot.send_message(call.message.chat.id, "Вот отфильтрованное по вашим параметрам меню",
                                           reply_markup=menu_markup_f1)
            lk_and_menu_markup = markup(['Вернуться в Меню', 'Вернуться в Личный Кабинет'])
            bot.send_message(call.message.chat.id, "Чтобы вернуться в начальное меню, нажмите на кнопку внизу экрана",
                             reply_markup=lk_and_menu_markup.m)

            menu_ids12 = (s.sql.execute("SELECT * FROM menu_ids"))
            menu_ids2 = s.sql.fetchall()
            try:
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=menu_ids2[search_username_menu_ids(call.from_user.id)][1])
            except:
                pass

            filter_menu_id = int(str(filter_menu).split(',')[2].split(' ')[-1])

            checker_menu_id = False
            for i in s.menu_ids:
                if str(i[0]) == str(call.from_user.id):
                    checker_menu_id = True
            if not checker_menu_id:
                s.sql.execute(f"""INSERT INTO menu_ids(username, menu_id)
                            VALUES('{call.from_user.id}', {filter_menu_id});""")
                s.db.commit()
            else:
                s.sql.execute(
                    f"""UPDATE menu_ids SET menu_id = {filter_menu_id} WHERE username = '{call.from_user.id}'""")
                s.db.commit()

    # except: pass


bot.infinity_polling(timeout=10, long_polling_timeout = 5)
