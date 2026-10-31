# Pruebas de la base institucional

Suite: `BASE-E2E` · Prioridad alta · Navegación, identidad y alternativas accesibles.

| Caso | Recorrido | Resultado esperado |
| --- | --- | --- |
| BASE-01 | Inicio → catálogo → E01–E05 → Evaluación → Evidencia | Pantallas correctas, propuestas enlazadas, navegación activa, recarga e historial funcionales, sin almacenamiento ni errores |
| BASE-02 | Teclado y navegación a 320, 768 y 1440 px | Enlace de salto, foco visible, destinos de al menos 44 px, sin desbordamiento horizontal y paleta de las fichas |
| BASE-03 | Desplazar al último bloque y volver a visitarlo | Entrada suave una sola vez; movimiento reducido elimina la animación |
| BASE-04 | Desactivar IntersectionObserver | Las cinco propuestas permanecen visibles |
| BASE-05 | Desactivar JavaScript | Explicación del requisito y enlace al portal oficial, no una pantalla vacía |
| RUNTIME-01 | Solicitar la web y rutas privadas a Nginx | HTML idéntico a la compilación, CSS disponible, fuentes/configuración/datos/documentos con respuesta 404 |

Los recorridos solo prueban la base. No verifican interacciones futuras, impacto electoral,
certificación WCAG completa ni autorización de divulgación.
