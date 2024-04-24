import mysql.connector
from flask import render_template
import bcrypt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ssl
from email.message import EmailMessage

def encriptar_contraseña(contraseña):
    # Generar una sal aleatoria
    salt = bcrypt.gensalt()
    # Encriptar la contraseña usando la sal
    contraseña_encriptada = bcrypt.hashpw(contraseña.encode('utf-8'), salt)
    return contraseña_encriptada

def verificar_contraseña(contraseña, contraseña_encriptada):
    # Verificar si la contraseña coincide con la contraseña encriptada
    return bcrypt.checkpw(contraseña.encode('utf-8'), contraseña_encriptada)

def verificar_text(palabra):
    signos = ["'","+","-","*",">","<","|","^","(",")","!","?",";",":"]
    signos.sort()
    print(signos)
    for i in palabra:
        for j in signos:
            if j in i:
                print("esta un signo")
                exit()
            else:
                print("no esta el signo")

def login(correo,contra):
    global cuenta
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="pdf"
    )
    cursor = conexion.cursor()
    verificar_text(correo)
    cursor.execute("SELECT contrasena,num_plan,num_imagenes,num_usuario FROM usuarios WHERE correo = %s", (correo,))
    cuenta = cursor.fetchone()

    if cuenta:
        contraseña_encriptada = cuenta[0]
        if bcrypt.checkpw(contra.encode('utf-8'), contraseña_encriptada.encode('utf-8')):
            print("Inicio de sesión exitoso.")
            return True,correo,cuenta[3]
        else:
            print("Credenciales incorrectas.")
    else:
        print("Usuario no encontrado.")

   
    conexion.close()
    
        
def register(nombre_com,correo,telefono,contra,num_plan):
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="pdf"
    )
    cursor = conexion.cursor()
    verificar_text(correo)
    #verificar_text(contra)
    verificar_text(nombre_com)
    verificar_text(telefono)
    contra_encriptada = encriptar_contraseña(contra)
    cursor.execute("INSERT INTO usuarios(nombre_completo,correo,contrasena,telefono,num_plan) VALUES(%s,%s,%s,%s,%s)",(nombre_com,correo,contra_encriptada,telefono,num_plan))
    conexion.commit()
    conexion.close()

def num_imagenes(numero_imagenes_ac):
    num_plan = cuenta[1]
    num_imagenes_bd = cuenta[2]
    num_usuario = cuenta[3]
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="pdf"
    )
    cursor = conexion.cursor()
    cursor.execute("SELECT cantidad_fotos FROM planes WHERE num_plan="+str(num_plan))
    cantidad_imagenes = cursor.fetchone()
    suma_imagenes = num_imagenes_bd + numero_imagenes_ac
    if suma_imagenes < cantidad_imagenes[0]:
        cursor.execute("UPDATE usuarios SET num_imagenes=%s WHERE num_usuario=%s",(suma_imagenes,num_usuario))
        conexion.commit()
        print("exito")
        return True
    else:
        return False
    conexion.close()
    
    
def log_admin(correo,contra):
    global login_admin
    login_admin = False
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="pdf"
    )
    cursor = conexion.cursor()
    verificar_text(correo)
    verificar_text(contra)

    cursor.execute("SELECT nombre_completo,correo,contrasena,telefono FROM administradores WHERE correo = %s", (correo,))
    datos = cursor.fetchone()

    if datos:
        contraseña_encriptada = datos[2]
        if bcrypt.checkpw(contra.encode('utf-8'), contraseña_encriptada.encode('utf-8')):
            print("Inicio de sesión exitoso.")
            login_admin = True
            return True
        else:
            print("Credenciales incorrectas.")
    else:
        print("Usuario no encontrado.")

    conexion.close()

def tablausuario_ad():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="pdf"
    )
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM usuarios")
    datos = cursor.fetchall()
    if login_admin == True:
        print(datos)
        return datos
    else:
        exit()
    conexion.close()

def tablaplanes_ad():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="pdf"
    )
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM planes")
    datos = cursor.fetchall()
    if login_admin == True:
        print(datos)
        return datos
    else:
        exit()
    conexion.close()

def tablaplanesactualizados_ad(num_plan,nombre,precio,c_fotos):
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="pdf"
    )
    cursor = conexion.cursor()
    if num_plan != "" and nombre != "" and precio !="" and c_fotos != "":
        cursor.execute("UPDATE planes SET nombre=%s,precio=%s,cantidad_fotos=%s WHERE num_plan=%s",(nombre,precio,c_fotos,num_plan))
        conexion.commit()
        return True
    else:
        exit()
    conexion.close()

def tabla_usuarios_actualizados_ad(num_usuario,nombre,correo,contra,telefono,num_imagenes,num_plan):
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="pdf"
    )
    cursor = conexion.cursor()
    if num_usuario != "" and nombre != "" and correo !="" and telefono != "" and num_imagenes != "" and num_plan != "":
        cursor.execute("UPDATE usuarios SET nombre_completo=%s,correo=%s,telefono=%s,num_imagenes=%s,num_plan=%s WHERE num_usuario=%s",(nombre,correo,telefono,num_imagenes,num_plan,num_usuario))
        conexion.commit()
        return True
    else:
        exit()
    conexion.close()

def tabla_usuarios_eliminar_ad(id_usuario):
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="pdf"
    )
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM usuarios WHERE num_usuario="+id_usuario)
    conexion.commit()
    conexion.close()

def cambiar_contrasena(contra):
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="pdf"
    )
    cursor = conexion.cursor()
    if contra != "":
        contra_encriptada = encriptar_contraseña(contra)
        cursor.execute("UPDATE usuarios SET contrasena=%s WHERE num_usuario=%s",(contra_encriptada,cuenta[3]))
        conexion.commit()
        conexion.close()
        return True
    
def cambiar_precios():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="pdf"
    )
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM planes")
    datos = cursor.fetchall()
    return datos

def olvido_contrasena(correo):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 465 

    sender_email = 'gamacortezr@gmail.com'
    password = 'qsik jgqd mkee urej'

    receiver_email = correo

    asunto = 'Cambio de contraseña'
    body = """
    La nueva contraseña es 12345678
    """
    message = EmailMessage()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = asunto
    message.set_content(body)

    contexto = ssl.create_default_context()

    with smtplib.SMTP_SSL(smtp_server, smtp_port, context=contexto) as server:

        server.login(sender_email, password)

        server.sendmail(sender_email,receiver_email,message.as_string())

    print('¡Correo enviado!')

    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="pdf"
    )
    cursor = conexion.cursor()
    contra_encriptada = encriptar_contraseña("12345678")
    cursor.execute("UPDATE usuarios SET contrasena=%s WHERE correo=%s",(contra_encriptada,correo))
    conexion.commit()
    conexion.close()
