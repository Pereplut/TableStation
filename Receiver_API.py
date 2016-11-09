import httplib2
import json

validValues={'temp':'temper_inC_Value','light':'lightValue'}


def getAllValuesFromServer(input_string):
    url=('http://192.168.2.52:5000/%s/all' % (input_string))
    head=httplib2.Http()
    responce,content=head.request(url,'GET')
    result= json.loads(content.decode('utf-8'))
    return result

def convertDataToList(requestType):
    decoded_json=getAllValuesFromServer(requestType)
    keyWord=validValues.get(requestType)
    list_to_fill=[]
    listWithDicts= list(decoded_json.values())[0]
    for eachDict in listWithDicts:
        list_to_fill.append(eachDict[keyWord])
    print(list_to_fill)


convertDataToList('temp')
