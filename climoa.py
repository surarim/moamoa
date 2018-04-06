#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import socket, os

print("Started... (Ctrl+C or q for exit)")
while True:
  mes = input("> ")
  if mes == "q":
    break
  try:
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect("/tmp/irimoa.sock")
    client.send(mes.encode('utf-8'))
    mes = client.recv(1024)
    print(mes.decode('utf-8'))
    client.close()
  except OSError:
   print("Socket not found, server is running?")

