// static/js/scripts.js

/**
 * Función genérica para mostrar mensajes de alerta
 * @param {string} message - El mensaje a mostrar.
 * @param {string} type - 'success' o 'danger'.
 */
function showAlert(message, type = 'success') {
    const alertDiv = document.getElementById('alert-message');
    if (!alertDiv) return;

    alertDiv.innerHTML = message;
    alertDiv.className = `alert alert-${type}`;
    alertDiv.style.display = 'block';

    // Ocultar después de 5 segundos
    setTimeout(() => {
        alertDiv.style.display = 'none';
    }, 5000);
}

// --- Lógica del formulario de Usuarios --- (2 ptos)
if (document.getElementById('usuarios-form')) {
    document.addEventListener('DOMContentLoaded', () => {
        const form = document.getElementById('usuarios-form');
        const listContainer = document.getElementById('usuarios-list-container');
        const searchInput = document.getElementById('search-input');
        const searchButton = document.getElementById('search-btn');
        const clearButton = document.getElementById('clear-search-btn');

        let isEditing = false; // Indica si estamos en modo edición
        let currentUserId = null; // Almacena el ID del usuario a editar

        // Cargar usuarios al iniciar
        fetchUsuarios();

        // 1. Manejar el envío del formulario (Registrar/Editar)
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Recoger los datos del formulario (2 ptos)
            const formData = {
                usuario: document.getElementById('usuario').value,
                clave: document.getElementById('clave').value,
                nombre: document.getElementById('nombre').value,
                direccion: document.getElementById('direccion').value,
                telefono: document.getElementById('telefono').value
            };

            let url = '/api/usuarios';
            let method = 'POST';

            // Si estamos editando, cambiamos URL y método [cite: 19]
            if (isEditing) {
                url = `/api/usuarios/${currentUserId}`;
                method = 'PUT';
                // La clave y el usuario no se envían al editar por seguridad y simplicidad
                delete formData.usuario;
                delete formData.clave;
            } else if (!formData.usuario || !formData.clave) {
                showAlert('El usuario y la clave son obligatorios para el registro.', 'danger');
                return;
            }
            
            if (!formData.nombre) {
                showAlert('El nombre es obligatorio.', 'danger');
                return;
            }

            try {
                const response = await fetch(url, {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });

                const result = await response.json();

                if (response.ok) {
                    showAlert(result.message, 'success');
                    form.reset(); // Limpiar formulario
                    fetchUsuarios(); // Recargar la lista
                    // Si se estaba editando, volver a modo registro
                    if (isEditing) {
                        toggleEditMode(false);
                    }
                } else {
                    showAlert(result.message || 'Error al procesar la solicitud.', 'danger');
                }
            } catch (error) {
                showAlert('Error de conexión con el servidor.', 'danger');
            }
        });

        // 2. Función para cargar y mostrar usuarios (Búsqueda y listado) (2 ptos)
        async function fetchUsuarios(searchTerm = '') {
            try {
                const url = searchTerm ? `/api/usuarios?search=${searchTerm}` : '/api/usuarios';
                const response = await fetch(url);
                const usuarios = await response.json();

                if (listContainer) {
                    listContainer.innerHTML = ''; // Limpiar lista
                    if (usuarios.length === 0) {
                        listContainer.innerHTML = '<p class="alert alert-danger">No se encontraron usuarios.</p>';
                        return;
                    }

                    // Crear la tabla
                    const table = document.createElement('table');
                    table.className = 'data-table';
                    table.innerHTML = `
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Usuario</th>
                                <th>Nombre</th>
                                <th>Dirección</th>
                                <th>Teléfono</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    `;
                    const tbody = table.querySelector('tbody');

                    usuarios.forEach(user => {
                        const row = tbody.insertRow();
                        row.insertCell().textContent = user.idUsuario;
                        row.insertCell().textContent = user.usuario;
                        row.insertCell().textContent = user.nombre;
                        row.insertCell().textContent = user.direccion || 'N/A';
                        row.insertCell().textContent = user.telefono || 'N/A';

                        const actionsCell = row.insertCell();
                        
                        // Botón Editar [cite: 19]
                        const editBtn = document.createElement('button');
                        editBtn.textContent = 'Editar';
                        editBtn.className = 'btn-primary';
                        editBtn.onclick = () => fillFormForEdit(user);
                        actionsCell.appendChild(editBtn);
                        
                        // Botón Eliminar [cite: 19]
                        const deleteBtn = document.createElement('button');
                        deleteBtn.textContent = 'Eliminar';
                        deleteBtn.className = 'btn-danger';
                        deleteBtn.style.marginLeft = '5px';
                        deleteBtn.onclick = () => eliminarUsuario(user.idUsuario, user.nombre);
                        actionsCell.appendChild(deleteBtn);
                    });

                    listContainer.appendChild(table);
                }
            } catch (error) {
                showAlert('Error al cargar la lista de usuarios.', 'danger');
            }
        }

        // 3. Llenar formulario para edición [cite: 19]
        function fillFormForEdit(user) {
            document.getElementById('usuario').value = user.usuario;
            document.getElementById('clave').value = ''; // No cargar la clave
            document.getElementById('nombre').value = user.nombre;
            document.getElementById('direccion').value = user.direccion;
            document.getElementById('telefono').value = user.telefono;
            
            // Deshabilitar campos de usuario/clave y cambiar el botón
            document.getElementById('usuario').disabled = true;
            document.getElementById('clave').disabled = true;
            document.getElementById('form-submit-btn').textContent = 'Guardar Cambios';
            document.getElementById('form-title').textContent = 'Editar Usuario';
            
            // Mostrar botón de cancelar edición
            document.getElementById('cancel-edit-btn').style.display = 'inline-block';

            isEditing = true;
            currentUserId = user.idUsuario;
            
            // Scroll a la parte superior del formulario
            window.scrollTo(0, 0);
        }

        // 4. Salir del modo edición
        function toggleEditMode(editMode) {
            isEditing = editMode;
            currentUserId = null;
            document.getElementById('usuario').disabled = editMode;
            document.getElementById('clave').disabled = editMode;
            document.getElementById('form-submit-btn').textContent = editMode ? 'Guardar Cambios' : 'Registrar Usuario';
            document.getElementById('form-title').textContent = editMode ? 'Editar Usuario' : 'Registrar Nuevo Usuario';
            document.getElementById('cancel-edit-btn').style.display = editMode ? 'inline-block' : 'none';
        }

        document.getElementById('cancel-edit-btn').addEventListener('click', () => {
            form.reset();
            toggleEditMode(false);
        });
        
        // 5. Eliminar usuario [cite: 19]
        async function eliminarUsuario(id, nombre) {
            if (confirm(`¿Está seguro de eliminar al usuario ${nombre} (ID: ${id})?`)) {
                try {
                    const response = await fetch(`/api/usuarios/${id}`, {
                        method: 'DELETE'
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        showAlert(result.message, 'success');
                        fetchUsuarios(); // Recargar la lista
                    } else {
                        showAlert(result.message || 'Error al eliminar el usuario.', 'danger');
                    }
                } catch (error) {
                    showAlert('Error de conexión con el servidor.', 'danger');
                }
            }
        }

        // 6. Lógica de búsqueda [cite: 19]
        searchButton.addEventListener('click', () => {
            const searchTerm = searchInput.value.trim();
            fetchUsuarios(searchTerm);
        });
        
        clearButton.addEventListener('click', () => {
            searchInput.value = '';
            fetchUsuarios('');
        });
        
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                fetchUsuarios(searchInput.value.trim());
            }
        });
    });
}