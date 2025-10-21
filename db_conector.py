
import mysql.connector
from config import Config

def connect_db():
    """Establece y devuelve la conexión a la base de datos."""
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error al conectar a MySQL: {err}")
        return None

def create_db_and_table():
    """Crea la base de datos db_academica si no existe y la tabla usuarios."""
    try:
        # Conexión sin especificar DB para crearla
        temp_conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        temp_cursor = temp_conn.cursor()

        # 1. Crear la base de datos db_academica si no existe
        temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME}")
        print(f"Base de datos '{Config.DB_NAME}' verificada/creada.")
        
        temp_cursor.close()
        temp_conn.close()

        # 2. Conexión a la base de datos recién creada/existente
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            
            # 3. Crear la tabla usuarios (2 ptos)
            create_table_query = """
            CREATE TABLE IF NOT EXISTS usuarios (
                idUsuario INT(10) AUTO_INCREMENT PRIMARY KEY,
                usuario CHAR(35) NOT NULL UNIQUE,
                clave CHAR(35) NOT NULL,
                nombre CHAR(85) NOT NULL,
                direccion CHAR(100),
                telefono CHAR(9)
            )
            """ # La clave primaria y A_I (AUTO_INCREMENT) se aplican a idUsuario [cite: 9]
            cursor.execute(create_table_query)
            conn.commit()
            print("Tabla 'usuarios' verificada/creada.")
            
            # 4. Insertar un usuario de prueba para el login si no existe
            test_user = ('admin', 'admin', 'Administrador Principal', '', '')
            try:
                # La clave se guardará en texto plano por simplicidad, pero se recomienda hashearla en producción
                cursor.execute(
                    "INSERT INTO usuarios (usuario, clave, nombre, direccion, telefono) VALUES (%s, %s, %s, %s, %s)",
                    test_user
                )
                conn.commit()
                print("Usuario de prueba 'admin' insertado.")
            except mysql.connector.IntegrityError:
                # El usuario ya existe (UNIQUE constraint violation)
                pass 
                
            cursor.close()
            conn.close()
            return True
        return False
        
    except mysql.connector.Error as err:
        print(f"Error al inicializar DB o tabla: {err}")
        return False