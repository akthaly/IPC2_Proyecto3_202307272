
class Empresa:
    def __init__(self, nombre, servicios):
        self.nombre = nombre
        self.servicios = servicios
    
    def __str__(self):
        return f"Nombre: {self.nombre}, Servicios: {self.servicios}"
    
    def __repr__(self):
        return self.__str__()