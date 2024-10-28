class Servicio:
    def __init__(self, nombre, alias):
        self.nombre = nombre
        self.alias = alias
    
    def __str__(self):
        return f"Nombre: {self.nombre}, Alias: {self.alias}"
    
    def __repr__(self):
        return self.__str__()