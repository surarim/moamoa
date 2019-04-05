#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import os, datetime, time, sys, socket, select, signal
from threading import Thread
from multiprocessing import Queue
from pubmoa import get_config
try:
  import psycopg2
except ModuleNotFoundError as err:
  print(err)
  sys.exit(1)

# Обработчик сигнала завершения приложения
def signal_hundler(signal, frame):
  # Инициализация завершения приложения
  app_work.get()

# Поток обработки команд и статусов
class server_status(Thread):
  # Стартовые параметры
  def  __init__(self, threads_list):
    super().__init__()
    self.daemon = True
    self.threads_list = threads_list

  # Главный цикл класса
  def run(self):
    # Подключение сокет файла
    socket_file = get_config('SocketFile')
    try:
      os.remove(socket_file)
    except OSError:
      pass
    # Старт epoll сервера
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(socket_file)
    server.listen(1)
    server.setblocking(0)
    epoll = select.epoll()
    epoll.register(server.fileno(), select.EPOLLIN)
    #
    connections = {}; requests = {}; responses = {}
    while not app_work.empty():
        events = epoll.poll(1)
        for fileno, event in events:
          if fileno == server.fileno():
            try:
              while not app_work.empty():
                connection, address = server.accept()
                connection.setblocking(0)
                epoll.register(connection.fileno(), select.EPOLLIN)
                connections[connection.fileno()] = connection
                requests[connection.fileno()] = b''
                responses[connection.fileno()] = b''
            except socket.error:
              pass
          elif event & select.EPOLLIN:
            try:
              # Получение данных из сокета
              while not app_work.empty():
                requests[fileno] += connections[fileno].recv(1024)
            except socket.error:
              epoll.modify(fileno, select.EPOLLOUT)
              mes = requests[fileno].decode()
          elif event & select.EPOLLOUT:
            try:
              # Подготовка ответа
              if mes == "exit":
                responses[fileno] = b'exit ok\n'
                # Инициализация завершения приложения
                app_work.get()
              elif mes == "status":
                responses[fileno] = b'status ok\n'
              else:
                responses[fileno] = b'command not found\n'
              while len(responses[fileno]) >  0:
                byteswritten = connections[fileno].send(responses[fileno])
                responses[fileno] = responses[fileno][byteswritten:]
            except socket.error:
              epoll.modify(fileno, 0)
              connections[fileno].shutdown(socket.SHUT_RDWR)
          elif event & select.EPOLLHUP:
            epoll.unregister(fileno)
            connections[fileno].close()
            del connections[fileno]
    # Завершение epoll
    epoll.unregister(server.fileno())
    epoll.close()
    server.close()
    # Удаление потока из списка
    self.threads_list.get()

# Поток чтения порта и отправки в базу
class server_udp(Thread):
  # Стартовые параметры
  def  __init__(self, threads_list):
    super().__init__()
    self.daemon = True
    self.threads_list = threads_list

  # Главный цикл класса
  def run(self):
    # Старт epoll сервера
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('',515))
    server.listen(1)
    server.setblocking(0)
    epoll = select.epoll()
    epoll.register(server.fileno(), select.EPOLLIN | select.EPOLLET)
    #
    connections = {}; requests = {}; responses = {}
    # Подключение к базе
    try:
      conn_pg = psycopg2.connect(database="dbmoa", user=get_config('DatabaseUserName'), password=get_config('DatabasePassword'))
    except psycopg2.OperationalError as error:
      print(format(error))
      sys.exit(1)
    cursor = conn_pg.cursor()
    while not app_work.empty():
        events = epoll.poll(1)
        for fileno, event in events:
          if fileno == server.fileno():
            try:
              while not app_work.empty():
                connection, address = server.accept()
                connection.setblocking(0)
                epoll.register(connection.fileno(), select.EPOLLIN | select.EPOLLET)
                connections[connection.fileno()] = connection
                requests[connection.fileno()] = b''
                responses[connection.fileno()] = b''
            except socket.error:
              pass
          elif event & select.EPOLLIN:
            try:
              # Получение данных из сокета
              while not app_work.empty():
                requests[fileno] += connections[fileno].recv(1)
            except socket.error:
              epoll.modify(fileno, select.EPOLLOUT | select.EPOLLET)
              mes = requests[fileno].decode()
            # Получение данных для записи в базу
            log_date = datetime.datetime.now().date()
            log_time = datetime.datetime.now().time()
            log_ip = addr[0]
            # Ограничение на длину сообщения
            log_text = mes.decode('utf-8')[:200]
            # Выполнение записи в базу
            try:
              cursor.execute("insert into log(date, time, ip, text) values (%s, %s, %s, %s);",(log_date, log_time ,log_ip, log_text))
              conn_pg.commit()
            except psycopg2.Error as error:
              print(format(error))
              sys.exit(1)
          elif event & select.EPOLLOUT:
            try:
              # Подготовка ответа
              if mes == "exit":
                responses[fileno] = b'exit ok\n'
                # Инициализация завершения приложения
                app_work.get()
              elif mes == "status":
                responses[fileno] = b'status ok\n'
              else:
                responses[fileno] = b'command not found\n'
              while len(responses[fileno]) >  0:
                byteswritten = connections[fileno].send(responses[fileno])
                responses[fileno] = responses[fileno][byteswritten:]
            except socket.error:
              epoll.modify(fileno, 0)
              epoll.modify(fileno, select.EPOLLET)
              connections[fileno].shutdown(socket.SHUT_RDWR)
          elif event & select.EPOLLHUP:
            epoll.unregister(fileno)
            connections[fileno].close()
            del connections[fileno]
    # Завершение epoll
    epoll.unregister(server.fileno())
    epoll.close()
    server.close()
    # Удаление потока из списка
    self.threads_list.get()

# Запуск потоков
if __name__ =='__main__':
 # Настройка обработчика завершения приложения для системного SIGTERM и Ctrl+C (SIGINT)
  signal.signal(signal.SIGTERM, signal_hundler)
  signal.signal(signal.SIGINT, signal_hundler)
  # Создание очереди завершения приложения
  app_work = Queue()
  app_work.put('run')
  # Создание очереди состояния работы потоков
  threads_list = Queue()
  # Запуск потоков
  threads_list.put('thread')
  server_status(threads_list).start()
  #threads_list.put('thread')
  #server_udp(threads_list).start()
  # Главный цикл работы программы
  while not threads_list.empty():
    time.sleep(0.1)
