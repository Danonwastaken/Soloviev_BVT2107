from datetime import datetime, date, time
import telebot 
from telebot import types
import psycopg2

token = "5060703475:AAHrgtXgUhdl_SJc2Lr1Gh2LEIQ08XAY-7I"
bot = telebot.TeleBot(token)

# Бд
conn = psycopg2.connect(database="teleschedule",
                        user="postgres",
                        password="XdanMST",
                        host="localhost",
                        port="5432")
cursor = conn.cursor()


# Время
start = date(2021, 9, 1) 
d = datetime.now() 

week = d.isocalendar()[1] - start.isocalendar()[1] + 1 

# Подсчёт недели
if week%2 == 1:
    top_week = True
    text_week = "верхней"
else:
    top_week = False
    text_week = "нижней"


@bot.message_handler(commands = ['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.row("/help", "/mtuci", "/week")
    keyboard.row("Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота")
    keyboard.row("Расписание на текущую неделю", "Расписание на следующую неделю")
    bot.send_message(message.chat.id, '/help', reply_markup=keyboard)


@bot.message_handler(commands = ['help'])
def help(message):
    bot.send_message(message.chat.id, 'Расписание группы БВТ2107\n\
Для того, чтобы узнать расписание на определенный день недели, нужно нажать на соответсвующую кнопку\n\
Чтобы узнать, какая сейчас неделя воспользуйтесь командой /week\n\
Расписание можно посмотреть полностью на эту и следующую неделю нажав соответсвующие кнопки\n\
Подробнее о ВУЗе можно узнать с помощью команды /mtuci')


@bot.message_handler(commands = ['week'])
def week(message):
    if top_week:
        bot.send_message(message.chat.id, 'верхняя')
    else:
        bot.send_message(message.chat.id, 'нижняя')
        

@bot.message_handler(commands = ['mtuci'])
def mtuci(message):
    bot.send_message(message.chat.id, 'Хочешь посетить сайт ВУЗа? Тогда тебе сюда – https://mtuci.ru/')


@bot.message_handler()
def answer(message):
    dot_week = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота']
    if message.text.lower() in dot_week:
        if message.text.lower() == "понедельник":
            dof = 'monday'
            text_dotw = "понедельник"
        elif message.text.lower() ==  "вторник":
            dof = 'tuesday'
            text_dotw = "вторник"
        elif message.text.lower() == "среда":
            dof = 'wednesday'
            text_dotw = "среду"
        elif message.text.lower() == "четверг":
            dof = 'thursday'
            text_dotw = "четверг"
        elif message.text.lower() == "пятница":
            dof = 'friday'
            text_dotw = "пятницу"            
        else:
            dof = 'saturday'
            text_dotw = "субботу"
        cursor.execute(f"SELECT service.subject.name, service.timetable.room_numb, service.timetable.start_time, service.teacher.full_name\
                        FROM service.subject\
                        INNER JOIN service.timetable ON service.subject.name = service.timetable.subject\
                        INNER JOIN service.teacher ON service.subject.name = service.teacher.subject\
                        WHERE service.timetable.day = '{dof}' and (migalka = '{'even' if (top_week) else 'odd'}' or migalka = 'always')\
                        ORDER BY service.timetable.start_time")
        records = list(cursor.fetchall())
        bot.send_message(message.chat.id, f"Расписание на {text_dotw} (по {text_week} неделе):")
        if records == []:
            for i in range(5):
                bot.send_message(message.chat.id, 'CPC')
        for i in range(len(records)):
            bot.send_message(message.chat.id, f"{records[i][0]} | {records[i][1]} \n{records[i][2]} | {records[i][3]}")

    elif message.text.lower() == "расписание на текущую неделю":
        cursor.execute(f"SELECT service.subject.name, service.timetable.room_numb, service.timetable.start_time, service.teacher.full_name, service.timetable.day\
                        FROM service.subject\
                        INNER JOIN service.timetable ON service.subject.name = service.timetable.subject\
                        INNER JOIN service.teacher ON service.subject.name = service.teacher.subject\
                        WHERE migalka = '{'even' if not (top_week) else 'odd'}' or migalka = 'always'\
                        ORDER BY service.timetable.letter, service.timetable.start_time")
        records = list(cursor.fetchall())
        bot.send_message(message.chat.id, f"Расписание на текущую неделю:")
        week = ['','Понедельник','Вторник','Среда','Четверг', 'Пятница', 'Суббота']
        for i in range(len(records)):
            bot.send_message(message.chat.id, f"{week[getdaynum(records[i][4])]} \n{records[i][0]} | {records[i][1]} \n{records[i][2]} | {records[i][3]}")

    elif message.text.lower() == "расписание на следующую неделю":
        cursor.execute(f"SELECT service.subject.name, service.timetable.room_numb, service.timetable.start_time, service.teacher.full_name, service.timetable.day\
                        FROM service.subject\
                        INNER JOIN service.timetable ON service.subject.name = service.timetable.subject\
                        INNER JOIN service.teacher ON service.subject.name = service.teacher.subject\
                        WHERE migalka = '{'even' if (top_week) else 'odd'}' or migalka = 'always'\
                        ORDER BY service.timetable.letter, service.timetable.start_time")
        records = list(cursor.fetchall())
        bot.send_message(message.chat.id, f"Расписание на следующую неделю:")
        week = ['','Понедельник','Вторник','Среда','Четверг', 'Пятница', 'Суббота']
        for i in range(len(records)):
            bot.send_message(message.chat.id, f"{week[getdaynum(records[i][4])]} \n{records[i][0]} | {records[i][1]} \n{records[i][2]} | {records[i][3]}")
            
    else:
        bot.send_message(message.chat.id, 'Извините, я Вас не понял')
def getdaynum(dayname):
    if dayname == 'monday':
        return 1
    if dayname == 'tuesday':
        return 2
    if dayname == 'wednesday':
        return 3
    if dayname == 'thursday':
        return 4
    if dayname == 'friday':
        return 5
    if dayname == 'saturday':
        return 6
bot.polling()