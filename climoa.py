#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import socket, os
from pubmoa import get_config

# Client for console access to the process of reading the port and writing to the database
# Клиент для консольного доступа к процессу чтения порта и записи в базу
print("Started... (Ctrl+C or q for exit)")
while True:
  mes = input("> ")
  if mes == "q":
    break
  try:
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(get_config('SocketFile'))
    client.send(mes.encode('utf-8'))
    mes = client.recv(1024)
    print(mes.decode('utf-8'))
    client.close()
  except OSError:
    print("Socket not found, server is running?")

