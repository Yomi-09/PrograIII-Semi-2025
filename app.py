
from flask import Flask, request, jsonify, render_template
import mysql.connector

app = Flask(__name__)

def get_db():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",  # Si tienes contraseña en MySQL, colócala aquí
        database="db_academica"
    )

@app.route('/')
def login_view():
    return render_template('login.html')

@app.route('/home')
def home_view():
    return render_template('usuarios.html')

# ---------- LOGIN ----------
@app.route('/login', methods=['POST'])
def login_user():
    data = request.get_json(force=True)
    usuario = data.get('usuario', '').strip()
    clave = data.get('clave', '').strip()

    cn = get_db()
    cur = cn.cursor(dictionary=True)
    cur.execute("SELECT * FROM usuarios WHERE usuario=%s AND clave=%s", (usuario, clave))
    user = cur.fetchone()
    cur.close()
    cn.close()

    if user:
        return jsonify({'success': True, 'message': 'Acceso concedido'})
    return jsonify({'success': False, 'message': 'Usuario o clave incorrecta'})

# ---------- CRUD USUARIOS ----------
@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    cn = get_db()
    cur = cn.cursor(dictionary=True)
    cur.execute("SELECT * FROM usuarios")
    usuarios = cur.fetchall()
    cur.close()
    cn.close()
    return jsonify(usuarios)

@app.route('/usuarios', methods=['POST'])
def crear_usuario():
    data = request.get_json(force=True)
    cn = get_db()
    cur = cn.cursor()
    cur.execute(
        "INSERT INTO usuarios (usuario, clave, nombre, direccion, telefono) VALUES (%s, %s, %s, %s, %s)",
        (data['usuario'], data['clave'], data['nombre'], data['direccion'], data['telefono'])
    )
    cn.commit()
    cur.close()
    cn.close()
    return jsonify({'message': 'Usuario registrado correctamente'})

@app.route('/usuarios/<int:idUsuario>', methods=['PUT'])
def actualizar_usuario(idUsuario):
    data = request.get_json(force=True)
    cn = get_db()
    cur = cn.cursor()
    cur.execute(
        "UPDATE usuarios SET usuario=%s, clave=%s, nombre=%s, direccion=%s, telefono=%s WHERE idUsuario=%s",
        (data['usuario'], data['clave'], data['nombre'], data['direccion'], data['telefono'], idUsuario)
    )
    cn.commit()
    cur.close()
    cn.close()
    return jsonify({'message': 'Usuario actualizado correctamente'})

@app.route('/usuarios/<int:idUsuario>', methods=['DELETE'])
def eliminar_usuario(idUsuario):
    cn = get_db()
    cur = cn.cursor()
    cur.execute("DELETE FROM usuarios WHERE idUsuario=%s", (idUsuario,))
    cn.commit()
    cur.close()
    cn.close()
    return jsonify({'message': 'Usuario eliminado'})

if __name__ == '__main__':
    # Usa host 0.0.0.0 si quieres acceder desde otros dispositivos en tu red
    app.run(debug=True)
