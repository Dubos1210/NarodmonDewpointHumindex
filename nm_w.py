#!/usr/bin/python
# -*- coding: UTF-8 -*-

#32786 32813

try:
	import nm_creds
	UUID = nm_creds.uuid
	API_KEY = nm_creds.api_key
except ModuleNotFoundError:
	UUID =  "d3ba5486248bdb590c6335c6dcb98578"	#NM_W	
	API_KEY = ""	#YOUR API_KEY

import sys
import errno
import requests
import json
import math

if __name__ == "__main__":
	print ("NarodMon extra parameters calculator")
	if (len(sys.argv) < 4):
		print ("Usage: "+sys.argv[0]+" THIS_ID TEMP_S_ID HUM_S_ID")
		sys.exit(errno.EINVAL)

	DEVID = "DubosDewpHumi:"+sys.argv[1]
	TEMP_S_ID = sys.argv[2]
	HUM_S_ID = sys.argv[3]

	requests.get("http://narodmon.ru/api/appInit?version=1&platform=0&uuid="+UUID+"&api_key="+API_KEY+"&lang=ru&utc=3")

	data = json.loads(requests.get("http://narodmon.ru/api/sensorsValues?sensors="+TEMP_S_ID+","+HUM_S_ID+"&uuid="+UUID+"&api_key="+API_KEY).text)

	if(list(data.keys())[0] != "sensors"):
		print("Ошибка обращения к серверу")
		sys.exit(errno.EREMOTEIO)

	TEMP = ""
	HUM = ""

	for sensor in data["sensors"]:
		if(sensor["type"] == 1):		#Температура
			TEMP = sensor["value"]
		elif(sensor["type"] == 2):		#Влажность
			HUM = sensor["value"]

	if((TEMP == "") | (HUM == "")):
		print("Ошибка получения ТЕМПЕРАТУРЫ и ВЛАЖНОСТИ")
		sys.exit(errno.EREMOTEIO)

	print("\tТемпература:", TEMP)
	print("\tВлажность:", HUM)

	#Расчёт
	f = (17.27*TEMP)/(237.7+TEMP)+math.log(HUM/100)
	DP = (237.7*f)/(17.27-f)
	#DP_text = ""
	#if(DP < 10):
	#	DP_text = "Немного сухо для некоторых"
	#elif(DP < 12):
	#	DP_text = "Очень комфортная влажность"
	#elif(DP < 15):
	#	DP_text = "Комфортная влажность"
	#elif(DP < 17):
	#	DP_text = "Комфортная влажность для многих"
	#elif(DP < 20):
	#	DP_text = "Неприятная влажность для большинства"
	#elif(DP < 23):
	#	DP_text = "Очень влажно и некомфортно"
	#elif(DP < 26):
	#	DP_text = "Крайне некомфортная влажность"
	#else:
	#	DP_text = "Cмертельно опасно для больных астмой"

	print("\t\tТочка росы:", DP)

	e = 5417.7530*(1/273.16 - 1/(DP + 273.16))
	HI = TEMP + 0.5555*(6.11*math.exp(e)-10)
	#HI_text = ""
	#if(HI < 29):
	#	HI_text = "Комфортная температура. Употребляйте воду по необходимости."
	#elif(HI < 39):
	#	HI_text = "Несколько некомфортная температура. Помните о возможности теплового удара. Организуйте в работе 15-минутные перерывы каждый час. Выпивайте не меньше стакана воды каждые 20 минут."
	#elif(HI < 45):
	#	HI_text = "Некомфортная температура. Избегайте физических нагрузок, организуйте в работе 45-минутные перерывы каждый час. Выпивайте не меньше стакана воды каждые 20 минут."
	#else:
	#	HI_text = "Высокая опасность теплового удара. Работы можно продолжать только под медицинским наблюдением."

	print("\t\tИндекс T и H:", HI)

	#Отправка
	senddata = "https://narodmon.ru/get?ID="+DEVID+"&DP="+str(DP)+"&HUMINDEX="+str(HI)
	data = requests.get(senddata.replace(" ", "%20")).text
	if(data != "ОК"):
		print("Ошибка отправки: "+data)
		sys.exit(errno.EPROTO)
	else: 
		print("Отправлено на сервер")