class Mensaje:
    def __init__(self, lugar, fecha, hora, usuario, red_social, mensaje, empresa=None, sentimiento=None):
        self.lugar = lugar
        self.fecha = fecha
        self.hora = hora
        self.usuario = usuario
        self.red_social = red_social
        self.mensaje = mensaje
        self.empresa = empresa
        self.sentimiento = sentimiento
    
    def __str__(self):
        return f"Lugar: {self.lugar}, Fecha: {self.fecha}, Hora: {self.hora} , Usuario: {self.usuario}, Red social: {self.red_social}, Mensaje: {self.mensaje}, Empresa: {self.empresa}, Sentimiento: {self.sentimiento}"
    
    def __repr__(self):
        return self.__str__()
