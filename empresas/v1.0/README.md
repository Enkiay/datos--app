# Directorio de Empresas Colaboradoras

Archivo `index.json` consumido por ArqOn para mostrar el directorio público de
empresas que colaboran enviando listas de precios.

## Schema

```json
{
  "version": "vYYYYMMDD-HHMMSS",
  "empresas": [
    {
      "id": "ferreteria-abc-cbb",
      "nombre": "Ferretería ABC",
      "ciudad": "Cochabamba",
      "tipo": "FERRETERIA",
      "estado": "ACTIVA",
      "fechaPrimeraColaboracion": "2026-05",
      "fechaUltimaColaboracion": "2026-05",
      "telefono": "70712345",
      "descripcion": "Colabora con la actualización de precios de referencia."
    }
  ]
}
```

## Campos

| Campo | Tipo | Obligatorio | Valores |
|---|---|---|---|
| `id` | string | sí | slug único; usado para detectar updates entre versiones |
| `nombre` | string | sí | nombre visible de la empresa |
| `ciudad` | string | sí | ciudad de operación |
| `tipo` | string | sí | `FERRETERIA` · `DISTRIBUIDOR` · `IMPORTADOR` · `FABRICANTE` · `OTRO` |
| `estado` | string | sí | `ACTIVA` · `INACTIVA` · `HISTORICA` |
| `fechaPrimeraColaboracion` | string | sí | formato `YYYY-MM` (mes/año de la primera vez que envió) |
| `fechaUltimaColaboracion` | string | sí | formato `YYYY-MM` |
| `telefono` | string\|null | no | público en pantalla detalle |
| `descripcion` | string | sí | texto libre de 1-2 líneas explicando el aporte |

## Cómo actualizar

1. Editar `index.json` directamente (agregar/quitar entradas, actualizar fechas).
2. Bumpear `version` con timestamp nuevo.
3. Actualizar `empresas.version` en el `manifest.json` raíz del repo.
4. Commit + push.

Los datos internos (correo, observaciones admin, cantidad de colaboraciones,
historial de archivos) NO van en este JSON público — viven solo en notas
locales del admin.
