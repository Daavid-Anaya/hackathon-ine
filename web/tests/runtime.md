### Prueba E2E: servidor estático en Docker

**Identificador de la suite:** `WEB-DOCKER-001`

**Prioridad:** alta

**Objetivo:** Verificar que el servidor ejecutado exclusivamente en Docker exponga el sitio generado, no las entradas del proyecto.

**Condiciones previas:** El servicio web está saludable y el contenedor de pruebas recibe su URL interna.

### Pasos

1. Solicitar el documento raíz de Nginx y compararlo con la compilación estática de la imagen de pruebas.
2. Solicitar los recursos CSS referenciados.
3. Solicitar rutas de fuentes y configuración, datos y salidas internas, un PDF técnico y una ruta desconocida.

### Resultado esperado

- La raíz devuelve HTTP 200 con HTML de Nginx idéntico al generado durante la compilación.
- Los recursos CSS devuelven HTTP 200 con el tipo de contenido correcto.
- Todas las rutas no públicas del proyecto y la ruta desconocida devuelven HTTP 404.

### Notas

Esta prueba no implica un despliegue en producción ni una certificación de confidencialidad estadística.
