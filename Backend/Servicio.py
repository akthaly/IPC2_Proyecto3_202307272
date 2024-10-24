class Servicio:
    def __init__(self, nombre, alias):
        self.nombre = nombre
        self.alias = alias
    
    def __str__(self):
        return f"Nombre: {self.nombre}, Alias: {self.alias}"