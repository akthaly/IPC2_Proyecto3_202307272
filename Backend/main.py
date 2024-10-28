from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from Empresa import Empresa
from Mensaje import Mensaje
from Servicio import Servicio
from xml.dom import minidom
import re
import unicodedata

#  FLask App
app = Flask(__name__)
CORS(app)

lista_mensajes = []
lista_empresas = []
lista_sentimientos_positivos = []
lista_sentimientos_negativos = []

# Routes
@app.route('/')
def index():
    return 'Hello, World!'

@app.route('/api', methods=['GET'])
def api():
    return jsonify({'message': 'Hello, World!'})

# Función para eliminar tildes y convertir a minúsculas
def normalizar_texto(texto):
    # Convertir el texto a minúsculas
    texto = texto.lower()
    # Eliminar tildes
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join([c for c in texto if unicodedata.category(c) != 'Mn'])
    return texto

@app.route('/config/postXML', methods=['POST'])
def postXML():
    data = request.get_data()  # Obtener los datos XML del request

    # Parsear el XML con minidom
    try:
        dom = minidom.parseString(data)
    except Exception as e:
        return jsonify({'message': 'Error al parsear XML', 'error': str(e)})

    # Extraer sentimientos positivos
    sentimientos_positivos = dom.getElementsByTagName('sentimientos_positivos')[0]
    positivos = sentimientos_positivos.getElementsByTagName('palabra')
    for palabra in positivos:
        palabra_texto = normalizar_texto(palabra.firstChild.data.strip())  # Normalizar palabra
        lista_sentimientos_positivos.append(palabra_texto)

    # Extraer sentimientos negativos
    sentimientos_negativos = dom.getElementsByTagName('sentimientos_negativos')[0]
    negativos = sentimientos_negativos.getElementsByTagName('palabra')
    for palabra in negativos:
        palabra_texto = normalizar_texto(palabra.firstChild.data.strip())  # Normalizar palabra
        lista_sentimientos_negativos.append(palabra_texto)

    # Extraer empresas y servicios
    empresas = dom.getElementsByTagName('empresa')
    for empresa in empresas:
        nombre_empresa = normalizar_texto(empresa.getElementsByTagName('nombre')[0].firstChild.data.strip())  # Normalizar empresa
        empresa_obj = Empresa(nombre_empresa, [])
        servicios = empresa.getElementsByTagName('servicio')
        for servicio in servicios:
            nombre_servicio = normalizar_texto(servicio.getAttribute('nombre'))  # Normalizar servicio
            servicio_obj = Servicio(nombre_servicio, [])
            aliases = servicio.getElementsByTagName('alias')
            for alias in aliases:
                alias_text = normalizar_texto(alias.firstChild.data.strip())  # Normalizar alias
                servicio_obj.alias.append(alias_text)
            empresa_obj.servicios.append(servicio_obj)
        lista_empresas.append(empresa_obj)

    # Extraer lista de mensajes y verificar empresas dentro del contenido
    mensajes = dom.getElementsByTagName('mensaje')
    for mensaje in mensajes:
        texto_mensaje = normalizar_texto(mensaje.firstChild.data.strip())  # Normalizar mensaje
        
        # Utilizamos expresiones regulares para extraer los campos
        # La fecha puede venir con o sin hora
        lugar_fecha_match = re.search(r"lugar y fecha:\s*(.+?),\s*(\d{2}/\d{2}/\d{4})(?:\s+(\d{2}:\d{2}))?", texto_mensaje)
        usuario_match = re.search(r"usuario:\s*(\S+)", texto_mensaje)
        red_social_match = re.search(r"red social:\s*(\S+)", texto_mensaje)
        contenido_mensaje_match = re.search(r"red social:\s*\S+\s+(.*)", texto_mensaje, re.DOTALL)

        # Extraemos los valores si existen
        if lugar_fecha_match:
            lugar = lugar_fecha_match.group(1).strip()
            fecha = lugar_fecha_match.group(2).strip()  # Solo la fecha
            hora = lugar_fecha_match.group(3).strip() if lugar_fecha_match.group(3) else None  # Hora opcional

            # Si no hay hora, asignar una cadena vacía o una hora por defecto (opcional)
            if not hora:
                hora = "00:00"  # Puedes cambiar esto si prefieres dejarlo vacío

        usuario = usuario_match.group(1).strip() if usuario_match else ""
        red_social = red_social_match.group(1).strip() if red_social_match else ""
        contenido_mensaje = contenido_mensaje_match.group(1).strip() if contenido_mensaje_match else ""

        # Reemplaza saltos de línea, tabulaciones y espacios múltiples
        lugar = re.sub(r"\s+", " ", lugar).strip()

        # Verificar si alguna empresa está mencionada en el contenido del mensaje
        empresa_en_mensaje = None
        for empresa in lista_empresas:
            if normalizar_texto(empresa.nombre) in contenido_mensaje:
                empresa_en_mensaje = empresa.nombre
                break

        # Inicializar contadores
        positivos_contador = 0
        negativos_contador = 0

        # Analizar el contenido del mensaje
        for palabra in contenido_mensaje.split():
            palabra_normalizada = normalizar_texto(palabra)  # Normalizar cada palabra del mensaje
            if palabra_normalizada in lista_sentimientos_positivos:
                positivos_contador += 1
            elif palabra_normalizada in lista_sentimientos_negativos:
                negativos_contador += 1

        # Determinar el sentimiento
        if positivos_contador > negativos_contador:
            sentimiento = "positivo"
        elif negativos_contador > positivos_contador:
            sentimiento = "negativo"
        else:
            sentimiento = "neutral"

        # Crear objeto Mensaje (fecha y hora separados)
        mensaje_obj = Mensaje(lugar, fecha, hora, usuario, red_social, contenido_mensaje, empresa_en_mensaje, sentimiento)
        lista_mensajes.append(mensaje_obj)

    # Mostrar los mensajes almacenados
    for i, mensaje in enumerate(lista_mensajes):
        print(f"\nMENSAJE {i + 1}\n")
        print(mensaje)

    return jsonify({'message': 'XML recibido'})

# Endpoint para contar ventas por departamento y generar el XML de salida
@app.route('/config/getAnswer', methods=['GET'])
def generarXML():
    # Crear el documento XML
    doc = minidom.Document()

    # Crear el elemento raíz
    lista_respuestas = doc.createElement('lista_respuestas')
    doc.appendChild(lista_respuestas)

    # Agrupar mensajes por fecha
    mensajes_por_fecha = {}
    for mensaje in lista_mensajes:
        fecha_solo = mensaje.fecha.split()[0]  # Extraer solo la parte de la fecha
        if fecha_solo not in mensajes_por_fecha:
            mensajes_por_fecha[fecha_solo] = []
        mensajes_por_fecha[fecha_solo].append(mensaje)

    # Procesar cada fecha
    for fecha, mensajes in mensajes_por_fecha.items():
        # Crear la respuesta
        respuesta = doc.createElement('respuesta')
        lista_respuestas.appendChild(respuesta)

        # Crear elemento de fecha
        fecha_elem = doc.createElement('fecha')
        fecha_elem.appendChild(doc.createTextNode(fecha.split()[0]))
        respuesta.appendChild(fecha_elem)

        # Calcular totales
        total_mensajes = len(mensajes)
        positivos_contador = sum(1 for m in mensajes if m.sentimiento == "positivo")
        negativos_contador = sum(1 for m in mensajes if m.sentimiento == "negativo")
        neutros_contador = total_mensajes - (positivos_contador + negativos_contador)

        # Crear elemento de mensajes
        mensajes_elem = doc.createElement('mensajes')
        total_elem = doc.createElement('total')
        total_elem.appendChild(doc.createTextNode(str(total_mensajes)))
        mensajes_elem.appendChild(total_elem)
        positivos_elem = doc.createElement('positivos')
        positivos_elem.appendChild(doc.createTextNode(str(positivos_contador)))
        mensajes_elem.appendChild(positivos_elem)
        negativos_elem = doc.createElement('negativos')
        negativos_elem.appendChild(doc.createTextNode(str(negativos_contador)))
        mensajes_elem.appendChild(negativos_elem)
        neutros_elem = doc.createElement('neutros')
        neutros_elem.appendChild(doc.createTextNode(str(neutros_contador)))
        mensajes_elem.appendChild(neutros_elem)
        respuesta.appendChild(mensajes_elem)

        # Crear el análisis
        analisis_elem = doc.createElement('analisis')
        respuesta.appendChild(analisis_elem)

        # Agrupar mensajes por empresa
        mensajes_por_empresa = {}
        for mensaje in mensajes:
            if mensaje.empresa not in mensajes_por_empresa:
                mensajes_por_empresa[mensaje.empresa] = []
            mensajes_por_empresa[mensaje.empresa].append(mensaje)

        # Procesar cada empresa
        for nombre_empresa, mensajes_empresa in mensajes_por_empresa.items():
            empresa_elem = doc.createElement('empresa')
            empresa_elem.setAttribute('nombre', nombre_empresa)
            analisis_elem.appendChild(empresa_elem)

            # Calcular totales por empresa
            total_empresa = len(mensajes_empresa)
            positivos_empresa = sum(1 for m in mensajes_empresa if m.sentimiento == "positivo")
            negativos_empresa = sum(1 for m in mensajes_empresa if m.sentimiento == "negativo")
            neutros_empresa = total_empresa - (positivos_empresa + negativos_empresa)

            mensajes_empresa_elem = doc.createElement('mensajes')
            total_empresa_elem = doc.createElement('total')
            total_empresa_elem.appendChild(doc.createTextNode(str(total_empresa)))
            mensajes_empresa_elem.appendChild(total_empresa_elem)
            positivos_empresa_elem = doc.createElement('positivos')
            positivos_empresa_elem.appendChild(doc.createTextNode(str(positivos_empresa)))
            mensajes_empresa_elem.appendChild(positivos_empresa_elem)
            negativos_empresa_elem = doc.createElement('negativos')
            negativos_empresa_elem.appendChild(doc.createTextNode(str(negativos_empresa)))
            mensajes_empresa_elem.appendChild(negativos_empresa_elem)
            neutros_empresa_elem = doc.createElement('neutros')
            neutros_empresa_elem.appendChild(doc.createTextNode(str(neutros_empresa)))
            mensajes_empresa_elem.appendChild(neutros_empresa_elem)
            empresa_elem.appendChild(mensajes_empresa_elem)

            # Procesar servicios
            servicios_elem = doc.createElement('servicios')
            empresa_elem.appendChild(servicios_elem)

            # Filtrar servicios relacionados a la empresa actual
            for servicio in [s for e in lista_empresas if e.nombre == nombre_empresa for s in e.servicios]:
                servicio_elem = doc.createElement('servicio')
                servicio_elem.setAttribute('nombre', servicio.nombre)

                # Contar mensajes relacionados con el servicio y sus alias
                servicio_mensajes = [
                    m for m in mensajes_empresa
                    if servicio.nombre in m.mensaje or any(alias in m.mensaje for alias in servicio.alias)
                ]

                total_servicio = len(servicio_mensajes)
                positivos_servicio = sum(1 for m in servicio_mensajes if m.sentimiento == "positivo")
                negativos_servicio = sum(1 for m in servicio_mensajes if m.sentimiento == "negativo")
                neutros_servicio = total_servicio - (positivos_servicio + negativos_servicio)

                # Crear elemento de mensajes para el servicio
                mensajes_servicio_elem = doc.createElement('mensajes')
                total_servicio_elem = doc.createElement('total')
                total_servicio_elem.appendChild(doc.createTextNode(str(total_servicio)))
                mensajes_servicio_elem.appendChild(total_servicio_elem)
                positivos_servicio_elem = doc.createElement('positivos')
                positivos_servicio_elem.appendChild(doc.createTextNode(str(positivos_servicio)))
                mensajes_servicio_elem.appendChild(positivos_servicio_elem)
                negativos_servicio_elem = doc.createElement('negativos')
                negativos_servicio_elem.appendChild(doc.createTextNode(str(negativos_servicio)))
                mensajes_servicio_elem.appendChild(negativos_servicio_elem)
                neutros_servicio_elem = doc.createElement('neutros')
                neutros_servicio_elem.appendChild(doc.createTextNode(str(neutros_servicio)))
                mensajes_servicio_elem.appendChild(neutros_servicio_elem)
                servicio_elem.appendChild(mensajes_servicio_elem)

                servicios_elem.appendChild(servicio_elem)


    # Convertir el documento a cadena
    xml_str = doc.toprettyxml(indent="  ")

    response = make_response(xml_str)
    response.headers['Content-Type'] = 'application/xml'

    return response


@app.route('/config/limpiarDatos', methods=['GET'])
def limpiarDatos():
    lista_mensajes.clear()
    lista_empresas.clear()
    lista_sentimientos_positivos.clear()
    lista_sentimientos_negativos.clear()
    lista_sentimientos_negativos.clear()
    lista_sentimientos_positivos.clear()
    return jsonify({'message': 'Datos limpiados'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
