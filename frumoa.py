#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
from cgi import parse_qs, escape
import psycopg2, socket

# Function of reading from the database and filtering
# Функция чтения из базы и фильтрации
def db_select(post_filter):
  # Connection to the database
  # Подключение к базе
  conn_string = "host='localhost' dbname='dbmoa' user='postgres' password=''"
  try:
    conn_pg = psycopg2.connect(conn_string)
  except psycopg2.OperationalError as error:
    print(format(error))
  cursor = conn_pg.cursor()
  try:
    # Check for filter or read by default
    # Проверка на фильтр или чтение по умолчанию
    if post_filter != "":
      cursor.execute("select date, time, ip, text from log where text ~ %s order by id desc limit 30;", (post_filter,))
    else:
      cursor.execute("select date, time, ip, text from log order by id desc limit 30;")
    rows = cursor.fetchall()
    mes = ""
    for row in rows:
      mes = mes + row[0].strftime('%Y-%m-%d')+" "+row[1].strftime('%H:%M:%S')+" "+row[2]+" | "+row[3]+"<br>"
    cursor.close()
    conn_pg.close()
  except psycopg2.OperationalError as error:
    return format(error)
  return mes

# WSGI application
# WSGI приложение
def application(env, start_response):
  start_response('200 OK', [('Content-Type','text/html')])
  head = open('scripts.js', 'r').read()
  body = open('forms.html', 'r').read()
  # Check post request and get data
  # Проверка на post запрос и получение данных
  if env['REQUEST_METHOD'] == 'POST':
    if env.get('CONTENT_LENGTH'): env_len = int(env.get('CONTENT_LENGTH'))
    else: env_len = 0
    if env_len > 0: post = env['wsgi.input'].read(env_len).decode('utf-8')
    else: post = ""
    mes = ""
    # The Default processing (when the form is loaded)
    # Обработка по умолчанию (при загрузке формы)
    if env['PATH_INFO'] == "/default":
      mes = db_select("")
    # Filter processing
    # Обработка фильтра
    if env['PATH_INFO'] == "/filter":
      mes = db_select(post)
    # Server status processing
    # Обработка статуса сервера
    if env['PATH_INFO'] == "/server_status":
      mes = "no"
      try:
        cli = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        cli.connect("/tmp/irimoa.sock")
        mes = "status"
        cli.send(mes.encode('utf-8'))
        mes = cli.recv(1024)
        if mes.decode('utf-8') == "status ok":
          mes = "ok"
        cli.close()
      except OSError:
        pass
    html = mes
  else:
    if env['PATH_INFO'] == "/favicon.ico":
      # Method Get - favicon
      # Метод Get - иконка приложения
      favicon = open('frumoa.png', 'rb').read()
      start_response('200 OK', [('Content-Type','image/png'),('Content-Length', str(len(favicon)))])
      return [favicon]
    else:
      # Method Get - Default page (form)
      # Метод Get - страница по умолчанию (форма)
      html = "<html>\n" + head + "<body>\n" + body +"\n</body>\n</html>"
  return [html.encode('utf-8')]
