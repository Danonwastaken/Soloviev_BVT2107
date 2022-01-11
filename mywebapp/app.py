import requests

from flask import Flask, render_template, request, redirect

import psycopg2

app = Flask(__name__)
conn = psycopg2.connect(database="service_db",user="postgres",password="XdanMST",host="localhost",port="5432")
cursor = conn.cursor()

@app.route('/', methods=['GET'])

def index():
    return redirect('/login')


@app.route('/login/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        if request.form.get("login"):
            username = request.form.get('username'); password = request.form.get('password')
            cursor.execute("SELECT * FROM service.users WHERE login=%s AND password=%s", (str(username), str(password)))
            records = list(cursor.fetchall())
            if len(records) == 0:
                return "Ошибка входа. Аккаунт не найден"
            return render_template('account.html', full_name=records[0][1])
        elif request.form.get("registration"):
            return redirect("/registration/")

    return render_template('login.html')

@app.route('/login/', methods=['POST'])

def loginPOST():
    username = request.form.get('username')
    password = request.form.get('password')
    if(not(username and password and username.strip() and password.strip())): 
        return('У вас пустой логин/пароль')
    cursor.execute("SELECT * FROM service.users WHERE login=%s AND password=%s", (str(username), str(password)))
    
    records = list(cursor.fetchall())
    return render_template('account.html', full_name=records[0][1])
    
@app.route('/registration/', methods=['POST', 'GET'])
def registration():
    if request.method == 'POST':
        name = request.form.get('name')
        login = request.form.get('login')
        password = request.form.get('password')
        if not (password.strip() and login.strip()):
            return "Ошибка регистрации. Логин/Пароль не должен быть пустым/содержать пробельные символы"
        cursor.execute('INSERT INTO service.users (full_name, login, password) VALUES (%s, %s, %s);',
                       (str(name), str(login), str(password)))
        conn.commit()

        return redirect('/login/')

    return render_template('registration.html')