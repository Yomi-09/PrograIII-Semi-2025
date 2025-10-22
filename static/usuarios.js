
async function listar() {
  const res = await fetch("/usuarios");
  const usuarios = await res.json();
  let tabla = "<tr><th>ID</th><th>Usuario</th><th>Nombre</th><th>Teléfono</th><th>Acción</th></tr>";
  usuarios.forEach(u => {
    tabla += `<tr>
      <td>${u.idUsuario}</td>
      <td>${u.usuario}</td>
      <td>${u.nombre}</td>
      <td>${u.telefono}</td>
      <td>
        <button onclick="editar(${u.idUsuario})">Editar</button>
        <button onclick="eliminarU(${u.idUsuario})">Eliminar</button>
      </td>
    </tr>`;
  });
  document.getElementById("tabla").innerHTML = tabla;
}

async function registrar() {
  const data = {
    usuario: document.getElementById("usuario").value,
    clave: document.getElementById("clave").value,
    nombre: document.getElementById("nombre").value,
    direccion: document.getElementById("direccion").value,
    telefono: document.getElementById("telefono").value
  };
  const res = await fetch("/usuarios", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  const msg = await res.json();
  alert(msg.message);
  listar();
}

async function eliminarU(id) {
  if (!confirm("¿Eliminar usuario?")) return;
  await fetch(`/usuarios/${id}`, { method: "DELETE" });
  listar();
}

async function editar(id) {
  const usuario = prompt("Nuevo usuario:");
  const clave = prompt("Nueva clave:");
  const nombre = prompt("Nuevo nombre:");
  const direccion = prompt("Nueva dirección:");
  const telefono = prompt("Nuevo teléfono:");
  if (usuario === null) return; // cancelado
  await fetch(`/usuarios/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ usuario, clave, nombre, direccion, telefono })
  });
  listar();
}

document.getElementById("btnRegistrar").addEventListener("click", registrar);
window.addEventListener("load", listar);
