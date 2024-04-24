from flask import Flask, render_template, request, send_file, url_for,jsonify
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import bd
import cv2
from multiprocessing import Pool

app = Flask(__name__)

extensiones_permitidas = {'png', 'jpg', 'jpeg'}

def convertir_imagenes_a_pdf(imagenes):
    direccion_pdf = os.getcwd()+"\pdf"
    nombre_pdf = 'resultado.pdf'
    ruta_pdf = os.path.join(direccion_pdf, nombre_pdf)
    c = canvas.Canvas(ruta_pdf, pagesize=[1920,1080])

    for imagen in imagenes:
        img = cv2.imread(imagen)
        alto, ancho, canal = img.shape
        c.drawImage(imagen, 0, 0, width=ancho, height=alto)
        c.showPage()

    c.save()
    return ruta_pdf

def archivos_permitidos(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensiones_permitidas

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/Login', methods=['POST'])
def iniciar_sesion():
    global consulta_ini
    if request.method == 'POST':
        correo_ini = request.form['correo']
        contrasena_ini = request.form['contrasena']
        if correo_ini != "" and contrasena_ini != "":
            consulta_ini = bd.login(correo_ini,contrasena_ini)
            print(consulta_ini)
            if consulta_ini[0] == True:
                return render_template("index.html",user = consulta_ini[1])
            else:
                pass

@app.route('/Registrarse')
def registrarse():
    consulta_precios = bd.cambiar_precios()
    print(consulta_precios[0][1])
    return render_template("register.html",data = consulta_precios)

@app.route('/Register', methods=['POST'])
def registrar():
    if request.method == 'POST':
        nombre = request.form['nombre_completo']
        telefono = request.form['telefono']
        correo = request.form['correo']
        contrasena = request.form['contrasena']
        plan = request.form['plan']
        if plan=="Basico":
            bd.register(nombre,correo,telefono,contrasena,1)
            return render_template("login.html")
        if plan=="Gold":
            bd.register(nombre,correo,telefono,contrasena,2)
            return render_template("login.html")
        if plan=="Platinum":
            bd.register(nombre,correo,telefono,contrasena,3)
            return render_template("login.html")

@app.route('/convertir', methods=['POST'])
def convert():
    direccion_imagenes = os.getcwd()+"\img_client"
    if 'images' not in request.files:
        return jsonify({'error': 'No se encontraron archivos en la solicitud'}), 400
    
    archivos = request.files.getlist('images')
    verificar_imagenes = bd.num_imagenes(archivos.__len__())

    if verificar_imagenes == True:
        if len(archivos) == 0:
            return jsonify({'error': 'Ningún archivo seleccionado'}), 400

        imagenes = []
        for archivo in archivos:
            if archivo and archivos_permitidos(archivo.filename):
                nombre_archivo = archivo.filename
                ruta_archivo = os.path.join(direccion_imagenes, nombre_archivo)
                archivo.save(ruta_archivo)
                imagenes.append(ruta_archivo)
            else:
                return jsonify({'error': 'Formato de archivo no admitido'}), 400

        # Convertir las imágenes a PDF utilizando múltiples procesos
        num_procesos = os.cpu_count()
        with Pool(num_procesos) as pool:
            pdf_path = pool.apply(convertir_imagenes_a_pdf, args=(imagenes,))
    
        return render_template("download.html")
    else:
        return render_template("index.html",resultado = "Error: Superaste tu limite de imagenes")

@app.route('/download')
def download():
    direccion_actual = os.getcwd()+"\pdf"
    pdf_direccion = os.path.join(direccion_actual, 'resultado.pdf')
    return send_file(pdf_direccion, as_attachment=True)

@app.route('/L_Administrador')
def login_administrador():
    return render_template("loginadmin.html")

@app.route('/T_Administrador' , methods=['POST'])
def tabla_administrador():
    if request.method == 'POST':
        correo = request.form['correo_ad']
        contra = request.form['contrasena_ad']
        if correo !="" and contra != "":
            consulta = bd.log_admin(correo,contra)
            if consulta == True:
                return render_template("menu_admin.html")
            
@app.route('/TU_Administrador')
def tablausuarios():
    datos_usuario = bd.tablausuario_ad()
    print(datos_usuario)
    return render_template("usuarios_admin.html", data = datos_usuario)

@app.route('/TP_Administrador')
def tablaplanes():
    datos_planes = bd.tablaplanes_ad()
    print(datos_planes)
    return render_template("planes_admin.html", data = datos_planes)

@app.route('/TPU_Administrador', methods=['POST'])
def tablaplanesactual():
    if request.method == 'POST':
        id_plan = request.form['id_plan']
        nombre = request.form['nombre_plan']
        precio = request.form['precio_plan']
        cantidad_fotos = request.form['cantidad_fotos_plan']
        datos_ac = bd.tablaplanesactualizados_ad(id_plan,nombre,precio,cantidad_fotos)
        if datos_ac==True:
            datos_planes = bd.tablaplanes_ad()
            return render_template("planes_admin.html", data = datos_planes)
        
@app.route('/TUE_Administrador', methods=['POST'])
def tablausuariosactual():
    if request.method == 'POST':
        num_usuario = request.form['Num_Usuario']
        nombre = request.form['Nombre_us']
        correo = request.form['Correo_us']
        contra = request.form['Contra_us']
        telefono = request.form['Telefono_us']
        num_imagenes = request.form['Num_Imagenes_us']
        num_plan = request.form['Num_Plan_us']
        datos_ac = bd.tabla_usuarios_actualizados_ad(num_usuario,nombre,correo,contra,telefono,num_imagenes,num_plan)
        if datos_ac==True:
            datos_usuarios = bd.tablausuario_ad()
            return render_template("usuarios_admin.html", data = datos_usuarios)

@app.route('/TUEE_Administrador', methods=['POST'])
def tablausuarioseliminar():    
    if request.method == 'POST':
        datos = request.form['Num_Usuario'] 
        bd.tabla_usuarios_eliminar_ad(datos)
        datos_usuarios = bd.tablausuario_ad()
        return render_template("usuarios_admin.html", data = datos_usuarios)
    
@app.route('/Cambiar_Contra_In')
def cambiar_contra():
    return render_template("cambiarcontra.html",user = consulta_ini[1])

@app.route('/Cambiar_Contra', methods=['POST'])
def cambiar_contra_accion():
    if request.method == 'POST':
        contra = request.form['contrasena']
        consulta = bd.cambiar_contrasena(contra)
        if consulta==True:
            return render_template("login.html")
        
@app.route('/Olvidar_Contrasena_In')
def olvidar_contrasena():
    return render_template("cambiarcontralogin.html")

@app.route('/Olvidar_Contrasena', methods=['POST'])
def olvidar_contrasena_accion():
    if request.method == 'POST':
        correo = request.form['correo']
        bd.olvido_contrasena(correo)
    return render_template("login.html")

if __name__ == '__main__':
    app.run(debug=True)
