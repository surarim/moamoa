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
    epoll.register(server.fileno(), select.EPOLLIN | select.EPOLLET)
    #
    connections = {}; requests = {}; responses = {}
    while not app_work.empty():
        events = epoll.poll(1)
        for fileno, event in events:
          # Получен пакет от клиента
          if fileno == server.fileno():
            connection, address = server.accept()
            connection.setblocking(0)
            requests[connection.fileno()] = b''
            responses[connection.fileno()] = b''
            connections[connection.fileno()] = connection
            # Регистрируем новое соединения для чтения-записи
            epoll.register(connection.fileno(), select.EPOLLIN | select.EPOLLET)
          # Другие события в том числе ошибки
          elif event in [8,9,10,16,17,18,24,25,26]:
            epoll.unregister(fileno)
            connections[fileno].close()
            del connections[fileno]
          # Событие чтения
          elif event & select.EPOLLIN:
            try:
              while not app_work.empty():
                data = connections[fileno].recv(1024)
                if not data:
                  epoll.modify(fileno, select.EPOLLHUP)
                  connections[fileno].shutdown(socket.SHUT_RDWR)
                  break
                else:
                  requests[fileno] += data
            except socket.error:
              pass
            mes = requests[fileno].decode()
            epoll.modify(fileno, select.EPOLLOUT | select.EPOLLET)
          # Событие записи
          elif event & select.EPOLLOUT:
            # Подготовка ответа
            if mes == "exit":
              responses[fileno] = b'exit ok\n'
              # Инициализация завершения приложения
              app_work.get()
            elif mes == "status":
              responses[fileno] = b'status ok\n'
            else:
              responses[fileno] = b'command not found\n'
            # Ответ клиенту
            while len(responses[fileno]) >  0:
              byteswritten = connections[fileno].send(responses[fileno])
              responses[fileno] = responses[fileno][byteswritten:]
            epoll.modify(fileno, select.EPOLLET)
            connections[fileno].shutdown(socket.SHUT_RDWR)
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
    # Запуск прослушивания порта
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('', 514)
    sock.setblocking(0)
    sock.bind(server_address)
    # Подключение к базе
    try:
      conn_pg = psycopg2.connect(database="dbmoa", user=get_config('DatabaseUserName'), password=get_config('DatabasePassword'))
    except psycopg2.OperationalError as error:
      print(format(error))
      exit(1)
    cursor = conn_pg.cursor()
    mes = ''
    # Цикл чтения порта
    while not app_work.empty():
      try:
        mes, addr = sock.recvfrom(2048)
        # Получение сообщения с учётом ограничений на длину (200)
        log_text = mes.decode('utf-8')[:200]
      except BlockingIOError:
        pass
      if mes:
        # Получение данных для записи в базу
        log_date = datetime.datetime.now().date()
        log_time = datetime.datetime.now().time()
        log_ip = addr[0]
        # Выполнение записи в базу
        try:
          cursor.execute("insert into log(date, time, ip, text) values (%s, %s, %s, %s);",(log_date, log_time ,log_ip, log_text))
          conn_pg.commit()
        except psycopg2.Error as error:
          print(format(error))
          exit(1)
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
  threads_list.put('thread')
  server_udp(threads_list).start()
  # Главный цикл работы программы
  while not threads_list.empty():
    time.sleep(0.1)
