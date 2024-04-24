import mysql.connector
import bcrypt

def encriptar_contraseña(contraseña):
    salt = bcrypt.gensalt()
    contraseña_encriptada = bcrypt.hashpw(contraseña.encode('utf-8'), salt)
    return contraseña_encriptada.decode('utf-8')

conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="pdf"
)
cursor = conexion.cursor()


nombre_completo = input("Introduce el nombre completo: ")
correo = input("Introduce el correo: ")
contraseña = input("Introduce la contrasena: ")
telefono = input("Introduce el telefono: ")
contraseña_encriptada = encriptar_contraseña(contraseña)

consulta = "INSERT INTO administradores (nombre_completo,correo,contrasena,telefono) VALUES (%s,%s,%s,%s)"
valores = (nombre_completo,correo,contraseña_encriptada,telefono,)
cursor.execute(consulta, valores)


conexion.commit()

print("Se a registrado bien")


conexion.close()
