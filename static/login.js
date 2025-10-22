
document.getElementById("btnLogin").addEventListener("click", async () => {
  const usuario = document.getElementById("usuario").value.trim();
  const clave = document.getElementById("clave").value.trim();

  const res = await fetch("/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ usuario, clave }),
  });

  const data = await res.json();
  alert(data.message);
  if (data.success) window.location.href = "/home";
});
