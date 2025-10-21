# app.py

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import db_connector

# Inicializar la aplicación Flask
app = Flask(__name__)
# Se necesita una clave secreta para la gestión de sesiones (obligatorio para usar 'session')
app.secret_key = 'super_secret_key_para_sesiones' 

# Inicializar la base de datos y la tabla al inicio
if not db_connector.create_db_and_table():
    print("La aplicación no puede iniciarse sin una conexión válida a la base de datos.")
    exit()

# Decorador para requerir inicio de sesión
def login_required(f):
    """Función decoradora para proteger rutas."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Si 'usuario' no está en la sesión, redirige al login
        if 'usuario' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Rutas de Interfaz (Frontend) ---

# Ruta principal: Redirige al login (debe ser la primera) (2 pto)
@app.route('/')
def index():
    return redirect(url_for('login'))

# Formulario de Login (GET) y Lógica de autenticación (POST) (2 pto)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        clave = request.form.get('clave')
        
        conn = db_connector.connect_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            # Buscar el usuario con la clave proporcionada [cite: 20]
            query = "SELECT idUsuario, usuario, nombre FROM usuarios WHERE usuario = %s AND clave = %s"
            cursor.execute(query, (usuario, clave))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user:
                # Almacenar en sesión e ir a la gestión de usuarios
                session['usuario'] = user['usuario']
                session['nombre'] = user['nombre']
                return redirect(url_for('gestion_usuarios'))
            else:
                # Denegar acceso [cite: 20]
                error = "Usuario o clave incorrectos."
                return render_template('login.html', error=error)

    return render_template('login.html')

# Vista de gestión de usuarios (requiere login)
@app.route('/usuarios')
@login_required
def gestion_usuarios():
    return render_template('usuarios.html')

# Lógica para cerrar sesión
@app.route('/logout')
@login_required
def logout():
    session.pop('usuario', None)
    session.pop('nombre', None)
    return redirect(url_for('login'))

# --- API de CRUD (Backend) ---

# API para recoger datos, procesar y almacenar (CRUD - Create) (2 ptos)
@app.route('/api/usuarios', methods=['POST'])
@login_required
def crear_usuario():
    # Recoger los datos enviados por el cliente
    data = request.get_json()
    usuario = data.get('usuario')
    clave = data.get('clave')
    nombre = data.get('nombre')
    direccion = data.get('direccion')
    telefono = data.get('telefono')

    if not all([usuario, clave, nombre]):
        return jsonify({"success": False, "message": "Faltan campos obligatorios."}), 400

    conn = db_connector.connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            insert_query = """
            INSERT INTO usuarios (usuario, clave, nombre, direccion, telefono)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (usuario, clave, nombre, direccion, telefono))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({"success": True, "message": "Usuario registrado exitosamente."}), 201
        except mysql.connector.IntegrityError:
            # Error si el usuario ya existe
            return jsonify({"success": False, "message": "El nombre de usuario ya existe."}), 409
        except Exception as e:
            conn.rollback()
            return jsonify({"success": False, "message": f"Error al registrar: {e}"}), 500
    return jsonify({"success": False, "message": "Error de conexión a la base de datos."}), 500

# API para buscar, editar o eliminar usuario (CRUD - Read, Update, Delete) (2 ptos)

# Leer todos los usuarios o buscar por ID
@app.route('/api/usuarios', methods=['GET'])
@login_required
def obtener_usuarios():
    search_term = request.args.get('search', '') # Para la búsqueda [cite: 19]

    conn = db_connector.connect_db()
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        if search_term:
            # Búsqueda por nombre o usuario [cite: 19]
            query = "SELECT idUsuario, usuario, nombre, direccion, telefono FROM usuarios WHERE nombre LIKE %s OR usuario LIKE %s ORDER BY idUsuario"
            search_pattern = f"%{search_term}%"
            cursor.execute(query, (search_pattern, search_pattern))
        else:
            # Obtener todos los usuarios
            query = "SELECT idUsuario, usuario, nombre, direccion, telefono FROM usuarios ORDER BY idUsuario"
            cursor.execute(query)
            
        usuarios = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(usuarios)
    return jsonify({"message": "Error de conexión a la base de datos."}), 500

# Editar usuario (CRUD - Update)
@app.route('/api/usuarios/<int:idUsuario>', methods=['PUT'])
@login_required
def editar_usuario(idUsuario):
    data = request.get_json()
    nombre = data.get('nombre')
    direccion = data.get('direccion')
    telefono = data.get('telefono')
    # Nota: No permitimos editar usuario/clave por esta ruta por simplicidad, aunque es posible.

    if not all([nombre]): # Se asume nombre es obligatorio
        return jsonify({"success": False, "message": "Falta el nombre obligatorio."}), 400

    conn = db_connector.connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            update_query = """
            UPDATE usuarios SET nombre = %s, direccion = %s, telefono = %s
            WHERE idUsuario = %s
            """
            cursor.execute(update_query, (nombre, direccion, telefono, idUsuario))
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({"success": False, "message": "Usuario no encontrado."}), 404
            
            cursor.close()
            conn.close()
            return jsonify({"success": True, "message": "Usuario actualizado exitosamente."}), 200
        except Exception as e:
            conn.rollback()
            return jsonify({"success": False, "message": f"Error al actualizar: {e}"}), 500
    return jsonify({"success": False, "message": "Error de conexión a la base de datos."}), 500

# Eliminar usuario (CRUD - Delete)
@app.route('/api/usuarios/<int:idUsuario>', methods=['DELETE'])
@login_required
def eliminar_usuario(idUsuario):
    conn = db_connector.connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            delete_query = "DELETE FROM usuarios WHERE idUsuario = %s"
            cursor.execute(delete_query, (idUsuario,))
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({"success": False, "message": "Usuario no encontrado."}), 404
            
            cursor.close()
            conn.close()
            return jsonify({"success": True, "message": "Usuario eliminado exitosamente."}), 200
        except Exception as e:
            conn.rollback()
            return jsonify({"success": False, "message": f"Error al eliminar: {e}"}), 500
    return jsonify({"success": False, "message": "Error de conexión a la base de datos."}), 500


if __name__ == '__main__':
    # Iniciar el servidor Flask
    # Debug=True permite recargar automáticamente al guardar cambios
    app.run(debug=True, host='0.0.0.0', port=5000)