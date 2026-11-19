# Comparador auxiliar RAM++ para portadas

Se incorporó en la pestaña **Etiquetar pares**, entre las tarjetas de los juegos y los botones de decisión. La función se ejecuta solo al pulsar «Analizar elementos de las portadas». El resultado muestra tres columnas: etiquetas exclusivas de cada portada y etiquetas compartidas. Cada par nuevo reinicia el panel.

## Requisitos adicionales (opcionales)

La aplicación principal conserva sus dependencias. Para activar este módulo se requiere instalar **PyTorch**, **torchvision**, **Pillow** y el proyecto oficial **Recognize Anything** (que expone el paquete Python `ram`), siguiendo sus instrucciones de instalación compatibles con el servidor. Descargar el checkpoint **RAM++ Swin-L** oficial y configurar:

```bash
export FAIRPLAY_RAM_CHECKPOINT=/ruta/al/checkpoint/ram_plus_swin_large_14m.pth
```

Reiniciar el servicio después de instalar las dependencias. No se descargan pesos automáticamente. El botón muestra un mensaje claro si el checkpoint o las dependencias no están disponibles. Los resultados se mantienen en inglés para evitar traducciones ambiguas. Solo se admiten URLs HTTPS de CDN de Steam y el análisis tiene caché por URL.

**Importante:** la versión incluida no trae el checkpoint de RAM++ ni las dependencias opcionales, por su tamaño y requisitos de hardware. No se ha probado la inferencia RAM++ con pesos reales en este entorno. El modelo de clasificación y el registro de etiquetas no se modificaron.
