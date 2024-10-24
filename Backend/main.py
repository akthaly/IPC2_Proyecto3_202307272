from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from Empresa import Empresa
from Mensaje import Mensaje
from Servicio import Servicio
from xml.dom import minidom
import re
from collections import defaultdict

#  FLask App
app = Flask(__name__)
CORS(app)

lista_mensajes = []

# Lista de los 22 departamentos de Guatemala
sentimientos_positivos = []
sentimientos_negativos = []

# Routes
@app.route('/')
def index():
    return 'Hello, World!'

@app.route('/api', methods=['GET'])
def api():
    return jsonify({'message': 'Hello, World!'})

@app.route('/config/postXML', methods=['POST'])
def postXML():
    global listadoVentas  # Asegurarse de que trabajamos sobre la lista global

    # Limpiar la lista de ventas para evitar duplicados
    listadoVentas.clear()

    data = request.get_data()  # Obtener los datos XML del request

    # Parsear el XML con minidom
    try:
        dom = minidom.parseString(data)
    except Exception as e:
        return jsonify({'message': 'Error al parsear XML', 'error': str(e)})

    # Encontrar todas las etiquetas 'Venta'
    ventas = dom.getElementsByTagName('Venta')

    for venta in ventas:
        departamento = venta.getAttribute('departamento')  # Obtener atributo 'departamento'

        # Verificar si el departamento es válido
        if departamento not in departamentos_validos:
            # Si el departamento no es válido, lo omitimos
            continue

        # Buscar la etiqueta 'Fecha' dentro de la etiqueta 'Venta'
        fecha_node = venta.getElementsByTagName('Fecha')
        if fecha_node:
            fechaCreacion = fecha_node[0].firstChild.nodeValue  # Obtener el texto de 'Fecha'

            # Validar la fecha con una expresión regular
            patron_fecha = r'\b(\d{2}/\d{2}/\d{4})\b'
            fechaGuardar = re.search(patron_fecha, fechaCreacion)

            if fechaGuardar:
                # Crear el objeto Venta con los datos extraídos
                venta_obj = Venta(departamento, fechaGuardar.group())
                listadoVentas.append(venta_obj)
            else:
                return jsonify({'message': 'Fecha incorrecta'})
        else:
            return jsonify({'message': 'Fecha no encontrada en el XML'})

    return jsonify({'message': 'XML recibido'})

# Endpoint para contar ventas por departamento y generar el XML de salida
@app.route('/config/getResumenVentas', methods=['GET'])
def generarResumenVentas():
    # Contar las ventas por departamento
    ventas_por_departamento = defaultdict(int)

    for venta in listadoVentas:
        ventas_por_departamento[venta.departamento] += 1

    # Crear el XML de salida usando minidom
    doc = minidom.Document()

    # Crear el elemento raíz <ResumenVentas>
    root = doc.createElement('resultados')
    doc.appendChild(root)

     # Crear el elemento <departamentos> que envolverá los departamentos
    departamentos_element = doc.createElement('departamentos')
    root.appendChild(departamentos_element)

    # Agregar cada departamento con ventas al XML
    for departamento, cantidad in ventas_por_departamento.items():
        if cantidad > 0:  # Solo mostrar departamentos con al menos una venta
            # Crear el elemento <Departamento> con el atributo 'nombre'
            departamento_element = doc.createElement(departamento)

            # Crear el elemento <Cantidad> para las ventas
            cantidad_element = doc.createElement('cantidadVentas')
            cantidad_text = doc.createTextNode(str(cantidad))
            cantidad_element.appendChild(cantidad_text)

            # Añadir <Cantidad> al <Departamento>
            departamento_element.appendChild(cantidad_element)

            # Añadir <Departamento> al nodo <departamentos>
            departamentos_element.appendChild(departamento_element)

    # Convertir el documento a un string XML
    xml_str = doc.toprettyxml(indent="  ")

    response = make_response(xml_str)
    response.headers['Content-Type'] = 'application/xml'

    return response

@app.route('/config/obtenerVentas', methods=['GET'])
def getVentas():
    ventas = []
    for venta in listadoVentas:
        ventas.append({'Departamento': venta.departamento , 'Fecha de Creacion': venta.fecha})

    return jsonify({'Ventas': ventas})


@app.route('/config/limpiarDatos', methods=['GET'])
def limpiarDatos():
    listadoVentas.clear()
    return jsonify({'message': 'Datos limpiados'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
