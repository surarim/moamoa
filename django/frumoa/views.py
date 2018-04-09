from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from .models import log
import socket, os

def frumoa_main(request):
  log_list = log.objects.order_by('-id')[:30]
  context = {'log_list': log_list}
  return render(request, 'form.html', context)

def frumoa_filter(request):
  fsr_list=""
  if log.objects.count() > 0:
    f_list = log.objects.filter(date__icontains = request.body.decode()) | log.objects.filter(time__icontains = request.body.decode()) | log.objects.filter(ip__icontains = request.body.decode()) | log.objects.filter(text__icontains = request.body.decode())
    fsr_list = f_list.values().order_by('-id')[:30]
    for item in fs_list:
      fsr_list+=str(item['date'])+" "+str(item['time'])+" "+str(item['ip'])+" || "+item['text']+"<br>"
  return HttpResponse(fsr_list)

def frumoa_server_status(request):
  try:
    cli = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    cli.connect("/tmp/irimoa.sock")
    mes = "status"
    cli.send(mes.encode('utf-8'))
    mes = cli.recv(1024)
    if mes.decode('utf-8') == "status ok":
      return HttpResponse('ok')
    cli.close()
  except OSError:
    pass
  return HttpResponse('no')
