from pprint import pprint
import time
import re
import sys
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)			# убираем из вывода предупреждение о не достоверных сертификатах
# Здесь нужно задать правила подключения

CMS_BASE='https://10.100.1.227:9443/api/v1/'                                                        # Задаем основные параметры (например IP)
CMS_HEADERS = {'Content-type': 'application/json', 'authorization': "Basic YWRtaW46QzFzY28xMjM="}    # Задаем логин-пароль (берем из postman)

# Здесь мы задаем номера абонентов
Party = ['1000', '1001', '1002', '1003', '1004', '1005', '1006', '1007', '1008', '1009', '1011', '1014', '1017']
Domain = "@str.ru"  # это доменная часть - будет прибавляться ко всем номерам (В случае если будет вызов по ip - сделать пустым и писать вместо номеров ip-шники)

# Здесь мы задаем слово из имени конференции или иное вхождение (например владелец) по которому будем ее искать
Name = "sergyuts Team"

# Autoconnect

def autoconnect(action) :		# Определяем функцию, которую будет удобно вызывать для подключения / отключения всех абонентов списка

    pprint(action)
    if str(action) == "1":     # подключаем абонентов из списка
        for element in Party :
            pprint ("подключаем абонента")
            pprint (element)   #   отслеживаем работу скрипта
            connect = requests.get(CMS_BASE + 'calllegs?filter=' + element, verify=False, headers=CMS_HEADERS)	# проверяем не подключен ли он уже к серверу?
            if ''.join(re.findall(r'callLegs total="(\d)', connect.text)) == '0' :
                requests.post(CMS_BASE + 'calls/' + CallID + '/calllegs', data="remoteParty=" + element + Domain, verify=False, headers=CMS_HEADERS)  # 	операция подключения
            else :
                print("Абонент уже подключен - отмена")
    if str(action) == "2":      # отключаем абонентов из списка
        for element in Party:
            pprint("отключаем абонента")
            pprint (element)
            connect = requests.get(CMS_BASE + 'calllegs?filter=' + element, verify=False, headers=CMS_HEADERS)
            if ''.join(re.findall(r'callLegs total="(\d)', connect.text)) != '0':
                calllegidcurrent = ''.join(re.findall(r'callLeg id="(\w+\-\w+\-\w+\-\w+\-\w+)', connect.text))
                pprint(calllegidcurrent)
                requests.delete(CMS_BASE + 'calllegs/' + calllegidcurrent, verify=False, headers=CMS_HEADERS)
            else :
                print("Абонент не подключен - отмена")

coSpaces = requests.get(CMS_BASE + 'coSpaces' + '?filter=' + Name, verify=False, headers=CMS_HEADERS)

if coSpaces.status_code == 200:
    pprint("это то, что выдал request.get:" + coSpaces.text)

SpacesNumber =  int(''.join(re.findall(r'<coSpaces total="(\d+)', coSpaces.text)))
if SpacesNumber == 0:
    print ("Конференций не найдено")
    time.sleep(5)
    quit()

elif SpacesNumber == 1:
    id = ''.join(re.findall(r'<coSpace id="(\w+\-\w+\-\w+\-\w+\-\w+)', coSpaces.text))
    print (id)

elif SpacesNumber > 1:
    print("Найдено  " + str(SpacesNumber) + "  конференции, выберете номер конференции из списка и нажмите enter")
    Names = re.findall(r'<name>(\w+\s*\w*\s*\w*)</name>', coSpaces.text)
    i=1
    while i <= SpacesNumber:
        pprint (str(i) + " - " + Names[i-1])
        i=i+1
    N = int(sys.stdin.readline())
    id = re.findall(r'<coSpace id="(\w+\-\w+\-\w+\-\w+\-\w+)', coSpaces.text)[N-1]
    print("это id нашей конференции:  " + id)

# Узнаем есть ли открытая медиа сессия

Call = requests.get(CMS_BASE + 'calls' + '?coSpaceFilter=' + id, verify=False, headers=CMS_HEADERS)

if int(''.join(re.findall(r'<calls total="(\d+)', Call.text))) == 0: # Медиа сессии нет - и ее нужно открыть
    pprint ("Нет активной сессии - создаем объект Call")
    response = requests.post(CMS_BASE + 'calls', data= {'coSpace' : id, 'name' : 'autodial', 'allowAllMuteSelf' : 'true', 'allowAllPresentationContribution' : 'true', 'joinAudioMuteOverride' : 'true' }, verify=False, headers=CMS_HEADERS)
    time.sleep(1)
    Call = requests.get(CMS_BASE + 'calls' + '?coSpaceFilter=' + id, verify=False, headers=CMS_HEADERS)
    CallID = ''.join(re.findall(r'<call id="(\w+\-\w+\-\w+\-\w+\-\w+)', Call.text))
else:
    pprint ("Медиа сессия уже существует")
    CallID = ''.join(re.findall(r'<call id="(\w+\-\w+\-\w+\-\w+\-\w+)', Call.text))

pprint ("Это ID медиасессии с которой мы работаем: " + CallID)
print ("Выберете операцию и нажмите enter:")
print (" 1 - автоматическое ПОДКЛЮЧЕНИЕ абонентов")
print (" 2 - автоматическое ОТКЛЮЧЕНИЕ абонентов")

actiontype = int(sys.stdin.readline())

autoconnect(actiontype)



