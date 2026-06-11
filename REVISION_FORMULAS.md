# Revisión: fórmulas explícitas en el catálogo oficial (branch `fix/formulas-defaults`)

**Problema:** los ítems sin `formulaResultado` se calculan en la app como
`cantidad = input × producto de TODOS los parámetros`. 57 ítems tenían parámetros
que no debían multiplicar (Ancho=4 en cubiertas/losas → ×4, Espesor=0.15 en muros
→ ×0.15, secciones de vigas ml → ×0.06, hoja de puerta/ventana → ×1.89/×1.32).

**Fix aplicado (commit `9f1e4c6`, SIN pushear):** fórmula explícita por unidad +
defaults que participan en la fórmula normalizados a 1. Los parámetros que NO
están en la fórmula quedan como dato informativo (espesores, secciones, hoja de
carpintería — siguen sirviendo para descuentos paramétricos).

- `items.json` (genérico): 57 ítems corregidos.
- `items_BO.json` (el que descarga Bolivia): 32 — ya estaba parcialmente curado
  (varios muros ya tenían solo Largo/Alto), pero conservaba los `Ancho=4`.
- `manifest.json`: bump de versión de `catalogo` y `catalogo_BO` →
  `v20260611-100000-formulas` (los celulares detectan la actualización).

La columna "Hoy" muestra los parámetros de `items_BO.json` cuando el ítem existe
ahí; "(solo genérico)" = en BO ese ítem ya estaba sano.

| # | Código | Ítem | Und | Hoy (defaults) | Efecto hoy | Fórmula nueva | Defaults ajustados |
|---|---|---|---|---|---|---|---|
| 1 | AC002 | Revoque Cielo Raso sobre Losa | m2 | Largo=1, Ancho=4 | ×4 | `Largo*Ancho` | Ancho 4→1 |
| 2 | AC019 | Contrapiso de Cemento sobre Losa | m2 | Largo=1, Ancho=4 | ×4 | `Largo*Ancho` | Ancho 4→1 |
| 3 | AC020 | Contrapiso Ladrillo Adobito | m2 | Largo=1, Ancho=4 | ×4 | `Largo*Ancho` | Ancho 4→1 |
| 4 | AC021 | Empedrado y Contrapiso de Ho | m2 | Largo=1, Ancho=4 | ×4 | `Largo*Ancho` | Ancho 4→1 |
| 5 | AC035 | Piso Machihembre Cedro con Envigado | m2 | Largo=1, Ancho=0.2 | ×0.2 | `Largo*Ancho` | Ancho 0.2→1 |
| 6 | CA001 | Puerta | Pza | Ancho=0.9, Alto=2.1 | ×1.89 | `1` (solo genérico) | — (hoja queda informativa) |
| 7 | CA002 | Ventana | Pza | Ancho=1.2, Alto=1.1 | ×1.32 | `1` (solo genérico) | — (hoja queda informativa) |
| 8 | CU001 | Desate de Cubierta de Calamina | m2 | Largo=1, Ancho=4 | ×4 | `Largo*Ancho` | Ancho 4→1 |
| 9 | CU002 | Cubierta Calamina Galvanizado N° 28 | m2 | Largo=1, Ancho=4 | ×4 | `Largo*Ancho` | Ancho 4→1 |
| 10 | CU003 | Cubierta Calamina Galvanizado N° 33 | m2 | Largo=1, Ancho=4 | ×4 | `Largo*Ancho` | Ancho 4→1 |
| 11 | CU004 | Cubierta Calamina Ondulada de Policarbonato | m2 | Largo=1, Ancho=4 | ×4 | `Largo*Ancho` | Ancho 4→1 |
| 12 | CU005 | Cubierta Calamina Plástica PVC | m2 | Largo=1, Ancho=4 | ×4 | `Largo*Ancho` | Ancho 4→1 |
| 13 | CU008 | Cubierta Steel Frame con Calamina Ondulada | m2 | Largo=1, Ancho=4 | ×4 | `Largo*Ancho` | Ancho 4→1 |
| 14 | CU009 | Cubierta Placa Ondulada | m2 | Largo=1, Ancho=4 | ×4 | `Largo*Ancho` | Ancho 4→1 |
| 15 | CU010 | Cubierta Steel Frame con Teja Colonial | m2 | Largo=1, Ancho=4 | ×4 | `Largo*Ancho` | Ancho 4→1 |
| 16 | CU011 | Cubierta Teja Colonial Cerámica | m2 | Largo=1, Ancho=4 | ×4 | `Largo*Ancho` | Ancho 4→1 |
| 17 | CU012 | Cubierta Teja Española Cerámica | m2 | Largo=1, Ancho=4 | ×4 | `Largo*Ancho` | Ancho 4→1 |
| 18 | CU013 | Cubierta Teja Española Duralit | m2 | Largo=1, Ancho=4 | ×4 | `Largo*Ancho` | Ancho 4→1 |
| 19 | CU014 | Cubierta Termoacústica Isolcruz - Densidad 13 | m2 | Largo=1, Ancho=4 | ×4 | `Largo*Ancho` | Ancho 4→1 |
| 20 | CU015 | Cubierta Termoacústica Isolcruz E=30 Mm Densidad 40 | m2 | Largo=1, Ancho=4 | ×4 | `Largo*Ancho` | Ancho 4→1 |
| 21 | CU016 | Cubierta Termoacústica Isolcruz E=50 Mm - Densidad 40 | m2 | Largo=1, Ancho=4 | ×4 | `Largo*Ancho` | Ancho 4→1 |
| 22 | CU017 | Cumbrera Calamina Plana | m | Largo=1, Ancho=4, Espesor=0.05 | ×0.2 | `Largo` (solo genérico) | — |
| 23 | CU018 | Cumbrera Teja Colonial | m | Largo=1, Ancho=4, Espesor=0.05 | ×0.2 | `Largo` (solo genérico) | — |
| 24 | CU021 | Bajante Calamina Plana N° 28 | m | Largo=1, Ancho=4, Espesor=0.05 | ×0.2 | `Largo` (solo genérico) | — |
| 25 | CU022 | Canaleta de Calamina N° 28 Corte 50 Cm | m | Largo=1, Ancho=4, Espesor=0.05 | ×0.2 | `Largo` (solo genérico) | — |
| 26 | CU023 | Cubierta de Policarbonato (6 Mm) | m2 | Largo=1, Ancho=4 | ×4 | `Largo*Ancho` | Ancho 4→1 |
| 27 | CU024 | Cubierta de Policarbonato (8 Mm) | m2 | Largo=1, Ancho=4 | ×4 | `Largo*Ancho` | Ancho 4→1 |
| 28 | CU025 | Impermeabilización de Cubierta Teja Colonial | m2 | Largo=1, Ancho=4 | ×4 | `Largo*Ancho` | Ancho 4→1 |
| 29 | CU026 | Pintura Anticorrosiva para Cubierta | m2 | Largo=1, Ancho=4 | ×4 | `Largo*Ancho` | Ancho 4→1 |
| 30 | CU027 | Pintura de Cubierta Exterior | m2 | Largo=1, Ancho=4 | ×4 | `Largo*Ancho` | Ancho 4→1 |
| 31 | MP002 | Muro Bloque de Hormigón 3H E=15 Cm | m2 | Largo=1, Alto=1, Espesor=0.15 | ×0.15 | `Largo*Alto` (solo genérico) | — |
| 32 | MP003 | Muro Bloque de Vidrio 20x20 Cm | m2 | Largo=1, Alto=1, Espesor=0.15 | ×0.15 | `Largo*Alto` (solo genérico) | — |
| 33 | MP006 | Muro Ladrillo 12 Cm 6H con Pega Ladrillo Fácil | m2 | Largo=1, Alto=1, Espesor=0.15 | ×0.15 | `Largo*Alto` (solo genérico) | — |
| 34 | MP007 | Muro Ladrillo 16 Cm 6H | m2 | Largo=1, Alto=1, Espesor=0.15 | ×0.15 | `Largo*Alto` (solo genérico) | — |
| 35 | MP008 | Muro Ladrillo 9.8 Cm 6H con Pegamento Valkure (Hz) | m2 | Largo=1, Alto=1, Espesor=0.15 | ×0.15 | `Largo*Alto` (solo genérico) | — |
| 36 | MP009 | Muro Ladrillo Adobito 15 Cm | m2 | Largo=1, Alto=1, Espesor=0.15 | ×0.15 | `Largo*Alto` (solo genérico) | — |
| 37 | MP012 | Muro Drywall 1 Cara 12 Cm Placa 1.2x2.4 M | m2 | Largo=1, Alto=1, Espesor=0.15 | ×0.15 | `Largo*Alto` (solo genérico) | — |
| 38 | MP013 | Muro Drywall 2 Caras 12 Cm Placa 1.2x2.4 M | m2 | Largo=1, Alto=1, Espesor=0.15 | ×0.15 | `Largo*Alto` (solo genérico) | — |
| 39 | MP014 | Muro Drywall 1 Cara 92 Mm Durlock (0.90x2.40 M) | m2 | Largo=1, Alto=1, Espesor=0.15 | ×0.15 | `Largo*Alto` (solo genérico) | — |
| 40 | MP015 | Muro Drywall 2 Caras 92 Mm Durlock (0.90x2.40 M) | m2 | Largo=1, Alto=1, Espesor=0.15 | ×0.15 | `Largo*Alto` (solo genérico) | — |
| 41 | MP016 | Muro Interior Termoacústico Construpanel E=60 Mm | m2 | Largo=1, Alto=2.8 | ×2.8 | `Largo*Alto` (genérico: `Largo`) | Alto 2.8→1 |
| 42 | MP017 | Muro Interior Termoacústico Construpanel E=75 Mm | m2 | Largo=1, Alto=2.8 | ×2.8 | `Largo*Alto` (genérico: `Largo`) | Alto 2.8→1 |
| 43 | MP018 | Muro Ext. Autoportante Construpanel E=100 Mm | m2 | Largo=1, Alto=2.8 | ×2.8 | `Largo*Alto` (genérico: `Largo`) | Alto 2.8→1 |
| 44 | MP019 | Muro Ext. Autoportante Construpanel E=120 Mm | m2 | Largo=1, Alto=2.8 | ×2.8 | `Largo*Alto` (genérico: `Largo`) | Alto 2.8→1 |
| 45 | MP020 | Muro Placa Cementicia 1 Cara Exterior | m2 | Largo=1, Alto=1, Espesor=0.15 | ×0.15 | `Largo*Alto` (solo genérico) | — |
| 46 | MP021 | Muro Placa Cementicia 2 Caras Int. y Ext. | m2 | Largo=1, Alto=1, Espesor=0.15 | ×0.15 | `Largo*Alto` (solo genérico) | — |
| 47 | OG021 | Losa Alivianada Vigueta Pretensada | m2 | Largo=1, Ancho=4 | ×4 | `Largo*Ancho` | Ancho 4→1 |
| 48 | OG022 | Losa H=20 con Vigueta H° Premezclado H-25 | m2 | Largo=1, Ancho=4 | ×4 | `Largo*Ancho` | Ancho 4→1 |
| 49 | OG023 | Losa H=20 con Vigueta H° Premezclado H-21 | m2 | Largo=1, Ancho=4 | ×4 | `Largo*Ancho` | Ancho 4→1 |
| 50 | OG024 | Losa H=20 Vigueta H-21 con Bomba Adicional | m2 | Largo=1, Ancho=4 | ×4 | `Largo*Ancho` | Ancho 4→1 |
| 51 | OG027 | Columna de Ladrillo Gambote 25x25 Cm | m | Largo=1, Ancho=0.2, Prof=0.2, Alto=3 | ×0.12 | `Alto` (solo genérico) | Alto 3→1 |
| 52 | OG030 | Imperm. de Sobrecimiento H=30 Cm | m | Largo=1, Ancho=0.8, Alto=0.3 | ×0.24 | `Largo` (solo genérico) | — |
| 53 | OG031 | Imperm. de Sobrecimiento H=30 con Asfaltex | m | Largo=1, Ancho=0.8, Alto=0.3 | ×0.24 | `Largo` (solo genérico) | — |
| 54 | OG066 | Viga Prefabricada H°P° L=20,60 M | m | Largo=1, Ancho=0.2, Alto=0.3 | ×0.06 | `Largo` (solo genérico) | — |
| 55 | OG067 | Viga Prefabricada H°P° L=25,60 M | m | Largo=1, Ancho=0.2, Alto=0.3 | ×0.06 | `Largo` (solo genérico) | — |
| 56 | OG068 | Viga Prefabricada H°P° L=35,60 M | m | Largo=1, Ancho=0.2, Alto=0.3 | ×0.06 | `Largo` (solo genérico) | — |
| 57 | OG069 | Viga Prefabricada H°P° L=45,60 M | m | Largo=1, Ancho=0.2, Alto=0.3 | ×0.06 | `Largo` (solo genérico) | — |

## Después del push

1. Los celulares ven la nueva versión del manifest → re-descargar catálogo en
   Configuración. La app toma la fórmula del remoto cuando la local está vacía
   (los ítems ya descargados se corrigen solos al actualizar).
2. Las mediciones ya cargadas en proyectos NO cambian solas (guardan su valor);
   conviene revisar partidas que usen estos ítems.
