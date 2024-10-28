from django.shortcuts import render
from .forms import FileForm
import requests

api = 'http://localhost:5000'
# Create your views here.

#Esta es una vista de ejemplo, pero puedes agregar las que necesites
def index(request):
    xmlContent = None
    return render(request, 'index.html',  {'xmlContent': xmlContent})

def ayuda(request):
    return render(request, 'ayuda.html')

def visualizarXML(request):
    xml_content = ""
    if request.method == 'POST':
    
        form = FileForm(request.POST, request.FILES)

        if form.is_valid():
            file = form.cleaned_data['file']
            xml_content = file.read().decode('utf-8')
            print(xml_content)
        else:
            print(form.errors)
    return render(request, 'index.html', {'xml_content': xml_content})

def subirXML(request):
    xml_content = ""

    if request.method == 'POST':
        xml_content = request.POST.get('xml', '')

        cleaned_xml_content = xml_content.encode('utf-8')
        response = requests.post(api+'/config/postXML', data=cleaned_xml_content)

        if response.status_code == 200:
            print(response.json())
    return render(request, 'index.html', {'xml_content': xml_content, 'response': response.json().get('message', '')})

def mostrarResultadosXML(request):
    response = requests.get(api + '/config/getAnswer')
    if response.status_code == 200:
        xml_response = response.text
        return render(request, 'index.html', {'response': xml_response})
    else:
        return render(request, 'index.html', {'response': 'Error al obtener los resultados'})
    
def reset(request):
    response = requests.get(api+'/config/limpiarDatos')
    return render(request, 'index.html', {'response': response.json().get('message', '')})
