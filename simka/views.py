import re
import requests
from docxtpl import DocxTemplate
from django.shortcuts import render
from requests.auth import HTTPBasicAuth
from simka.forms import StatementForm
from django.http import FileResponse

def create_simka(request):
    form = StatementForm()
    context = {
        'form': form,
    }
    return render(request, "simka/index.html", context)

def error(request):
    return render(request, "error.html")

def succes(request):
    return render(request, "succes.html")

def download(request, namefile):
    response = FileResponse(open(namefile, 'rb'))
    return response


def statement(request):

    if request.method == 'POST':
        stateform = StatementForm(request.POST)

        if stateform.is_valid():
            errorStatus = []
            linkTicket = stateform.cleaned_data["link"]

            # Данные для авторизации
            auth = HTTPBasicAuth('service_simkarta_uk', '95W6g&9oL2')

            # Составляем параметры для запроса
            params = {'fields': ['customfield_38701', 'customfield_27301', 'customfield_11904', 'customfield_44000',
                                 'customfield_25511', 'customfield_44001', 'customfield_24001', 'customfield_18802',
                                 'customfield_14304', 'customfield_44100', 'customfield_45001', 'customfield_25504',
                                 'customfield_27300', 'customfield_30702', 'customfield_20708', 'customfield_44901']}

            # Берем номер тикета из ссылки, которую вставили
            try:
                numberTicket = re.search(r'SD-\d*', linkTicket).group(0)
            except:
                errorStatus.append('Ошибка в ссылке на тикет')

            # создаем GET запрос
            fullReq = requests.get('https://ticket.ertelecom.ru/rest/api/2/issue/' + numberTicket, params=params,
                                   auth=auth).json()

            if fullReq != '':
                fioPerson = fullReq['fields']['customfield_38701']  # ФИО
                pasportPerson = fullReq['fields']['customfield_27301']  # Серия и номер паспорта
                fullAdressPerson = fullReq['fields']['customfield_11904']  # Полный адрес
                cityPerson = fullReq['fields']['customfield_44000']  # Город
                ufmsPerson = fullReq['fields']['customfield_25511']  # Кем выдан
                codeUfmsPerson = int(fullReq['fields']['customfield_44001'])  # Код подразделения, кто выдал паспорт
                positionPerson = fullReq['fields']['customfield_24001'][0]  # Должность сотрудника
                otdelPerson = fullReq['fields']['customfield_18802'][0]  # Отдел сотрудника
                cityCompanyPerson = fullReq['fields']['customfield_14304'][0]  # Город филиала
                typeSimkarta = fullReq['fields']['customfield_25504']['value']  # Тип симкарты
                numberSimkarta = fullReq['fields']['customfield_27300']  # Номер симкарты
                if fullReq['fields']['customfield_30702'] != None:
                    operatorSimkarta = fullReq['fields']['customfield_30702']['value']  # Оператор
                else:
                    operatorSimkarta = None
                if fullReq['fields']['customfield_20708'] != None:
                    tarifSimkarta = fullReq['fields']['customfield_20708']  # Тариф симкарты
                else:
                    tarifSimkarta = None
                dateBornPersonTemp = fullReq['fields']['customfield_44100']  # Дата рождения
                datePassportPersonTemp = fullReq['fields']['customfield_45001']  # Дата выдачи паспорта

                listTemp = {fioPerson: 'ФИО', pasportPerson: 'Серия и номер паспорта', fullAdressPerson: 'Полный адрес',
                            cityPerson: 'Город', ufmsPerson: 'Кем выдан', codeUfmsPerson: 'Код подразделения',
                            positionPerson: 'Должность сотрудника', otdelPerson: 'Отдел сотрудника',
                            cityCompanyPerson: 'Город филиала', typeSimkarta: 'Тип симкарты',
                            numberSimkarta: 'Номер симкарты', operatorSimkarta: 'Оператор симкарты',
                            tarifSimkarta: 'Тариф симкарты', dateBornPersonTemp: 'Дата рождения',
                            datePassportPersonTemp: 'Дата выдачи паспорта '}

                listError = []
                for item in listTemp.keys():
                    if item == None:
                        listError.append(listTemp.get(item))

                strError = ''
                if len(listError) > 0:
                    strError = listError[0]
                    for k in listError[1:]:
                        strError += ',' + k
                    statusTicket = "Ошибка.", ' В тикете не хватает обязательных полей: ' + strError
                    errorStatus.append(statusTicket)
                    context = {'statusTicket': statusTicket}
                    return render(request, "error.html", context)
                else:
                    if fullReq['fields']['customfield_44901'] != None:
                        limitSimkarta = int(fullReq['fields']['customfield_44901'])  # Лимит по симкарте
                    else:
                        limitSimkarta = None

                    # Составление нормализованной даты рождения

                    dateBornList = dateBornPersonTemp.split('-')  # Список из чисел
                    dateBornListReversed = list(reversed(dateBornList))  # Переворачиваем список
                    dateBornPerson = str(dateBornListReversed[0])  # Присваем переменной первое число
                    # Цикл для составлия полной даты
                    for k in dateBornListReversed[1:]:
                        dateBornPerson += '.' + k

                    # Составление нормализованной даты выдачи паспорта
                    datePassportPersonList = datePassportPersonTemp.split('-')  # Список из чисел
                    datePassportPersonListReversed = list(reversed(datePassportPersonList))  # Переворачиваем список
                    datePassportPerson = str(datePassportPersonListReversed[0])  # Присваем переменной первое число
                    # Цикл для составлия полной даты
                    for i in datePassportPersonListReversed[1:]:
                        datePassportPerson += '.' + i

                    # Дополнительный текст
                    if typeSimkarta == 'Дополнительная':
                        textDopoln = 'Прошу ежемесячно удерживать стоимость услуг Оператора по SIM-карте из моей заработной платы'
                    elif typeSimkarta == 'Производственная':
                        textDopoln = ''
                    elif typeSimkarta == 'Основная' and limitSimkarta > 0:
                        textDopoln = 'Установленный ежемесячный Лимит возмещения затрат составляет ' + str(limitSimkarta) + \
                                     ' рублей. В случае, если фактическая стоимость услуг Оператора по SIM-карте за месяц ' \
                                     'превысит установленный Лимит, прошу ежемесячно, начиная с даты настоящего Заявления, ' \
                                     'удерживать из моей заработной платы сумму превышения.'
                    elif typeSimkarta == 'Основная':
                        textDopoln = 'Установленный ежемесячный Лимит возмещения затрат составляет 0 рублей. Прошу ежемесячно ' \
                                     'удерживать стоимость услуг Оператора по SIM-карте из моей заработной платы'
                    else:
                        # messagebox.showinfo("Ошибка", 'Невозможно определить тип сим-карты или не указан лимит у Основной сим-карты. ' + strError + '.Нажмите ОК')
                        textExcept = 'Ошибка с полем Тип-симкарты'

                    # Начинаем работать с docx заявлением
                    template = DocxTemplate("static/zayva.docx")

                    print(template)
                    if len(errorStatus) > 0:
                        return render(request, "error.html", {'statusTicket': errorStatus})
                    else:
                        # Переменные
                        context = {
                            'numberTicket': numberTicket,
                            'fioPerson': fioPerson,
                            'pasportPerson': pasportPerson,
                            'fullAdressPerson': fullAdressPerson,
                            'cityPerson': cityPerson,
                            'ufmsPerson': ufmsPerson,
                            'codeUfmsPerson': codeUfmsPerson,
                            'positionPerson': positionPerson,
                            'otdelPerson': otdelPerson,
                            'cityCompanyPerson': cityCompanyPerson,
                            'dateBornPerson': dateBornPerson,
                            'datePassportPerson': datePassportPerson,
                            'typeSimkarta': typeSimkarta,
                            'numberSimkarta': numberSimkarta,
                            'operatorSimkarta': operatorSimkarta,
                            'tarifSimkarta': tarifSimkarta,
                            'textDopoln': textDopoln,
                        }

                        # Рендеринг заявления
                        template.render(context)
                        name_file_othcet = 'Заявление для ' + str(fioPerson) + ' для сим-карты.docx'
                        template.save(name_file_othcet)
                        template.save

                        response = FileResponse(open(name_file_othcet, 'rb'))
                        context = {'link': name_file_othcet}
                        return render(request, "succes.html", context)

            else:
                errorStatus.append('Ошибка в API JIRA')
                context = {'statusTicket': errorStatus}
                return render(request, "error.html", context)
        else:
            return render(request, "error.html", {'statusTicket': 'Невалидные данные'})
    else:
        return render(request, "error.html", {'statusTicket': 'Запрос не POST'})