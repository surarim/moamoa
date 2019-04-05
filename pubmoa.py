#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

# Общий модуль с параметрами и функциями

import os

config = [] # Список параметров файла конфигурации

# Функция получения значений параметров конфигурации
def get_config(key):
  global config
  if not config:
    # Чтение файла конфигурации
    try:
      if os.path.isfile('/etc/moamoa/moa.conf'):
        configfile = open('/etc/moamoa/moa.conf')
      else:
        configfile = open('moa.conf')
    except IOError as error:
      log_write(error)
    else:
      for line in configfile:
        param = line.partition('=')[::2]
        if param[0].strip().isalpha() and param[1].strip().find('#') == -1:
          config.append(param[0].strip())
          config.append(param[1].strip())
  return config[config.index(key)+1]
