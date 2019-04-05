#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from cgi import parse_qs, escape
import psycopg2, socket
from pubmoa import get_config

# Функция чтения из базы и фильтрации
def db_select(post_filter):
  # Подключение к базе
  try:
    conn_pg = psycopg2.connect(database="dbmoa", user=get_config('DatabaseUserName'), password=get_config('DatabasePassword'))
  except psycopg2.OperationalError as error:
    return format(error)
  cursor = conn_pg.cursor()
  # Проверка на фильтр или чтение по умолчанию
  try:
    if post_filter != "":
      cursor.execute("select date, time, ip, text from log where to_tsvector('english', text) @@ to_tsquery('english', %s) order by id desc limit 1000;", (post_filter,))
    else:
      cursor.execute("select date, time, ip, text from log order by id desc limit 30;")
  except psycopg2.Error as error:
    return format(error)
  rows = cursor.fetchall()
  mes = ""
  for row in rows:
    mes = mes + row[0].strftime('%Y-%m-%d')+" "+row[1].strftime('%H:%M:%S')+" "+row[2]+" | "+row[3]+"<br>"
  cursor.close()
  conn_pg.close()
  return mes

# WSGI приложение
def application(env, start_response):
  start_response('200 OK', [('Content-Type','text/html')])
  head = open('scripts.js', 'r').read()
  body = open('forms.html', 'r').read()
  # Проверка на post запрос и получение данных
  if env['REQUEST_METHOD'] == 'POST':
    if env.get('CONTENT_LENGTH'): env_len = int(env.get('CONTENT_LENGTH'))
    else: env_len = 0
    if env_len > 0: post = env['wsgi.input'].read(env_len).decode('utf-8')
    else: post = ""
    mes = ""
    # Обработка по умолчанию (при загрузке формы)
    if env['PATH_INFO'] == "/default":
      mes = db_select("")
    # Обработка фильтра
    if env['PATH_INFO'] == "/filter":
      mes = db_select(post)
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
      # Метод Get - иконка приложения
      favicon = open('frumoa.png', 'rb').read()
      start_response('200 OK', [('Content-Type','image/png'),('Content-Length', str(len(favicon)))])
      return [favicon]
    else:
      # Метод Get - страница по умолчанию (форма)
      html = "<html>\n" + head + "<body>\n" + body +"\n</body>\n</html>"
  return [html.encode('utf-8')]
