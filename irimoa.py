#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import socket, psycopg2, datetime, os, threading
exit_status = False

# Command and status processing flow
# Поток обработки команд и статусов
def server_status():
  print("Started... (Ctrl+C for exit)")
  socket_file = "/tmp/irimoa.sock"
  sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
  try:
    os.remove(socket_file)
  except OSError:
    pass
  sock.bind(socket_file)
  sock.listen(1)
  while True:
    conn, addr = sock.accept()
    while True:
      mes = conn.recv(1024)
      if not mes: break
      if mes.decode('utf-8') == "exit":
        conn.send(b'exit ok')
        global exit_status
        exit_status = True
        exit(0)
      elif mes.decode('utf-8') == "status":
        conn.send(b'status ok')
      else:
        conn.send(b'command not found')
    conn.close()

# Feed the port read and send to the database
# Поток чтения порта и отправки в базу
def server_udp():
  # Start listening to the port
  # Запуск прослушивания порта
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  server_address = ('', 514)
  sock.bind(server_address)
  # Connection to the database
  # Подключение к базе
  try:
    conn_pg = psycopg2.connect(database="dbmoa", user="postgres", password="")
  except psycopg2.OperationalError as error:
    print(format(error))
    exit(1)
  cursor = conn_pg.cursor()
  # Cycle reading port
  # Цикл чтения порта
  while True:
    if exit_status:
      break
    mes, addr = sock.recvfrom(2048)
    # Getting data to write to the database
    # Получение данных для записи в базу
    log_date = datetime.datetime.now().date()
    log_time = datetime.datetime.now().time()
    log_ip = addr[0]
    # Message length limit
    # Ограничение на длину сообщения
    log_text = mes.decode('utf-8')[:200]
    # Write to the database
    # Выполнение записи в базу
    try:
      cursor.execute("insert into log(date, time, ip, text) values (%s, %s, %s, %s);",(log_date, log_time ,log_ip, log_text))
      conn_pg.commit()
    except psycopg2.Error as error:
      print(format(error))
      exit(1)

# Running threads
# Запуск потоков
if __name__ =='__main__':
  thread_server_status = threading.Thread(target=server_status, name="server_status")
  thread_server_udp = threading.Thread(target=server_udp, name="server_udp")
  thread_server_status.start()
  thread_server_udp.start()
  thread_server_status.join()
  thread_server_udp.join()
