let catalogoCompleto = [];

// URL correcta con la ruta completa a tu archivo JSON
const CATALOG_URL = "https://jamcalza-store-imagenes.s3.amazonaws.com/data/catalog.json";

async function cargarCatalogo() {
  try {
    const respuesta = await fetch(CATALOG_URL);
    if (!respuesta.ok) throw new Error("Error al descargar el archivo JSON");
    
    const datosRecibidos = await respuesta.json();
    let listaOriginal = [];
    
    if (Array.isArray(datosRecibidos)) {
      listaOriginal = datosRecibidos;
    } else if (datosRecibidos.productos && Array.isArray(datosRecibidos.productos)) {
      listaOriginal = datosRecibidos.productos;
    } else if (datosRecibidos.data && Array.isArray(datosRecibidos.data)) {
      listaOriginal = datosRecibidos.data;
    } else {
      const propiedadLista = Object.values(datosRecibidos).find(val => Array.isArray(val));
      listaOriginal = propiedadLista || [];
    }
    
    catalogoCompleto = listaOriginal.map(obj => {
      const objetoLimpio = {};
      for (let llave in obj) {
        if (obj.hasOwnProperty(llave)) {
          const llaveNormalizada = llave.trim().toLowerCase().replace(/[^a-z0-dash_]/g, "");
          objetoLimpio[llaveNormalizada] = obj[llave];
        }
      }
      return objetoLimpio;
    });

    console.log("Datos normalizados con éxito:", catalogoCompleto);
    
    poblarFiltros(catalogoCompleto);
    renderizarProductos(catalogoCompleto);
  } catch (error) {
    console.error("Hubo un fallo en la carga:", error);
    document.getElementById("catalogo").innerHTML = `<p style='color:red; padding:20px;'>Error: No se pudo conectar con el catálogo de AWS S3.</p>`;
  }
}

function poblarFiltros(productos) {
  const categorias = [...new Set(productos.map(p => p.categoria || p.categoras || p.cat || ""))].map(c => String(c).trim()).filter(Boolean);
  const selectCategoria = document.getElementById("filtro-categoria");
  if (selectCategoria) {
    selectCategoria.innerHTML = '<option value="">Todas</option>';
    categorias.forEach(cat => {
      const opcion = document.createElement("option");
      opcion.value = cat;
      opcion.textContent = cat;
      selectCategoria.appendChild(opcion);
    });
  }

  const ubicaciones = [...new Set(productos.map(p => p.ubicacion || p.ubicacin || p.ub || ""))].map(u => String(u).trim()).filter(Boolean);
  const selectUbicacion = document.getElementById("filtro-ubicacion");
  if (selectUbicacion) {
    selectUbicacion.innerHTML = '<option value="">Todas</option>';
    ubicaciones.forEach(ub => {
      const opcion = document.createElement("option");
      opcion.value = ub;
      opcion.textContent = ub;
      selectUbicacion.appendChild(opcion);
    });
  }
}

function aplicarFiltros() {
  const categoria = document.getElementById("filtro-categoria")?.value || "";
  const talla = document.getElementById("filtro-talla")?.value || "";
  const ubicacion = document.getElementById("filtro-ubicacion")?.value || "";

  let filtrados = catalogoCompleto;
  if (categoria) filtrados = filtrados.filter(p => String(p.categoria || p.categoras || p.cat).trim() === categoria);
  if (talla) filtrados = filtrados.filter(p => String(p.talla).trim() == talla);
  if (ubicacion) filtrados = filtrados.filter(p => String(p.ubicacion || p.ubicacin || p.ub).trim() === ubicacion);

  renderizarProductos(filtrados);
}

window.aplicarFiltros = aplicarFiltros;

function renderizarProductos(productos) {
  const contenedor = document.getElementById("catalogo");
  if (!contenedor) return;

  if (productos.length === 0) {
    contenedor.innerHTML = "<p style='padding:20px;'>No hay productos disponibles.</p>";
    return;
  }

  contenedor.innerHTML = productos.map(p => {
    const nombre = p.nombre || p.codigo || p.id || "Producto sin nombre";
    const categoria = p.categoria || p.categoras || p.cat || "General";
    const talla = p.talla || "N/A";
    const color = p.color || "N/A";
    const ubicacion = p.ubicacion || p.ubicacin || p.ub || "No especificada";
    
    const precioClave = Object.keys(p).find(k => k.includes("precio") || k.includes("valor") || k.includes("costo"));
    const precio = precioClave ? parseFloat(p[precioClave]) : 0;
    
    const stockClave = Object.keys(p).find(k => k.includes("stock") || k.includes("cantidad") || k.includes("existencia") || k.includes("disponible"));
    const stock = stockClave ? parseInt(p[stockClave]) : 0;
    
    const imagenClave = Object.keys(p).find(k => k.includes("imagen") || k.includes("foto") || k.includes("url") || k.includes("src"));
    const imagen_url = imagenClave ? String(p[imagenClave]).trim() : "";

    return `
      <div class="tarjeta-producto" style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 10px; width: 220px; display: inline-block; vertical-align: top; font-family: sans-serif; background: #fff; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
        <img src="${imagen_url}" alt="${nombre}" loading="lazy" onerror="this.onerror=null;this.src='https://placehold.co'" style="width: 100%; height: 200px; object-fit: cover; border-radius: 4px;">
        <h3 style="font-size: 16px; margin: 10px 0 5px 0; color: #333;">${nombre}</h3>
        <p style="font-size: 12px; color: #666; margin: 0;">Cat: ${categoria} | Talla: ${talla}</p>
        <p style="font-size: 12px; color: #666; margin: 0;">📍 ${ubicacion}</p>
        <p style="font-size: 16px; font-weight: bold; color: #2c3e50; margin: 8px 0;">$${isNaN(precio) ? '0.00' : precio.toFixed(2)}</p>
        <p style="font-size: 12px; font-weight: bold; margin: 0; color: ${stock > 0 ? '#2ecc71' : '#e74c3c'}">
          ${stock > 0 ? `Disponible (${stock})` : "Agotado"}
        </p>
      </div>
    `;
  }).join("");
}

cargarCatalogo();
