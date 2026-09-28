# Brasil: revisión de los 25 ítems fuera de rango, APLICADA (resumen, 28-09-2026)

Decisiones de Oscar (28-sep-2026) sobre `catalogo/fuentes/revision_25_extremos_BR_20260928.md`, aplicadas con `tools/fase-a-composicoes-br.py` (constantes `REVISION25_OK`, `COMP_CAMBIADA`, `ADAPTADAS`, `DEJAR_RECETA`, `MAPA_CORREGIDO`). Fuente: SINAPI (Caixa/IBGE) 08/2026, hojas Analítico e ICD/CCD (COM desoneração), libro sha256 `1587f458…4aec89`. Versiones al aplicar: catalogo_BR `v20260928c-br-sinapi-revision25`; precios_BR sube una letra sobre la publicada (hoy `v20260928b-br-sinapi-202608`).

Sólo cambian `insumos` y `referencia` de cada ítem; código, nombre, categoría, unidad, parámetros, fórmula, tipoIfc, etiqueta y «verificado» quedan iguales. Reglas de aplanado sin cambios (M.O. y equipo como UNA línea con costo CCD; auxiliares abiertas). Costos: 1 unidad del ítem en São Paulo, sin cargas ni BDI; «Antes» = receta publicada × precios publicados; «Después» = receta nueva × precios SINAPI SP que quedan al aplicar.

Comando (sobre el repo): `python tools/fase-a-composicoes-br.py --ratio-min 0.5 --ratio-max 2 --aplicar`

## Por ítem

| Ítem | Unidad | Veredicto | Composição usada | `referencia` | Líneas | Antes SP | Después SP | Después/antes | Aplanado vs CCD |
|---|---|---|---|---|---|---:|---:|---:|---:|
| AC002BR Reboco de Teto sobre Laje | m2 | OK_PUBLICAR | 87415 | SINAPI 87415 · 08/2026 | 3 → 3 | 132,71 | 40,75 | 0,31 | +0.0% |
| AC017BR Reboco Interno de Gesso | m2 | OK_PUBLICAR | 87418 | SINAPI 87418 · 08/2026 | 3 → 3 | 97,79 | 22,53 | 0,23 | +0.1% |
| AC033BR Piso de Tábua Corrida E=1.9 Cm | m2 | OK_PUBLICAR | 101746 | SINAPI 101746 · 08/2026 | 3 → 5 | 281,54 | 607,05 | 2,16 | +0.0% |
| AC035BR Piso de Madeira Macho-e-Fêmea de Cedro com Vigamento | m2 | OK_PUBLICAR | 105090 | SINAPI 105090 · 08/2026 | 6 → 7 | 273,09 | 593,94 | 2,17 | +0.0% |
| AC037BR Piso de Pedra São Tomé | m2 | OK_PUBLICAR | 101731 | SINAPI 101731 · 08/2026 | 5 → 9 | 194,43 | 392,52 | 2,02 | +0.0% |
| AC049BR Pintura de Beirais | m2 | OK_PUBLICAR | 104640 | SINAPI 104640 · 08/2026 | 4 → 3 | 33,87 | 15,64 | 0,46 | +0.1% |
| AC050BR Pintura de Concreto Aparente Externo | m2 | OK_PUBLICAR | 95626 | SINAPI 95626 · 08/2026 | 4 → 3 | 39,49 | 18,60 | 0,47 | +0.1% |
| AC069BR Batente de Madeira 2″x4″ (Guanandi) | Pza | OK_PUBLICAR | 90806 | SINAPI 90806 · 08/2026 | 6 → 10 | 245,83 | 541,60 | 2,20 | +0.0% |
| CR002BR Pintura de Portas | m2 | ADAPTAR | 102220×2 + 102193×2 | adaptado de SINAPI 102220+102193 · 08/2026 | 5 → 4 | 53,67 | 44,27 | 0,82 | +0.1% |
| CU001BR Retirada de Cobertura de Telha de Aço Galvanizado | m2 | OK_PUBLICAR | 97647 | SINAPI 97647 · 08/2026 | 1 → 2 | 21,37 | 4,92 | 0,23 | +0.2% |
| IE022BR Transformador 150 KVA | Glb | OK_PUBLICAR | 102106 | SINAPI 102106 · 08/2026 | 3 → 4 | 52.515,38 | 25.339,53 | 0,48 | +0.0% |
| IS015BR Fornecimento e Instalação de Registro 1/2″ | Pza | OK_PUBLICAR | 89352 | SINAPI 89352 · 08/2026 | 4 → 4 | 75,83 | 31,27 | 0,41 | +0.0% |
| IS016BR Fornecimento e Instalação de Registro 3/4″ | Pza | OK_PUBLICAR | 89353 | SINAPI 89353 · 08/2026 | 4 → 4 | 78,80 | 35,45 | 0,45 | +0.1% |
| IS034BR Caixa de Gordura de Polietileno 25x35x35 Cm | Pza | OK_PUBLICAR | 98110 | SINAPI 98110 · 08/2026 | 5 → 5 | 141,08 | 461,80 | 3,27 | +0.0% |
| IS052BR Locação e Marcação de Tubulações | m | OK_PUBLICAR | 99063 | SINAPI 99063 · 08/2026 | 5 → 27 | 5,38 | 11,76 | 2,19 | +0.5% |
| IS066BR Fornecimento e Instalação de Tubulação de PEAD de 110 Mm (4″) | m | DEJAR_RECETA | — (receta sin cambios) | — | 4 | 54,08 | 54,08 | 1,00 | DEJAR_RECETA (revisión de los 25, Oscar 28-sep-2026): falta precio BR del PEAD SDR 17/21; SINAPI sólo trae SDR 11 PN 12,5 |
| IS074BR Escavação de Vala com Retroescavadeira | m3 | OTRA_COMPOSICAO | 90105 | SINAPI 90105 · 08/2026 | 3 → 3 | 30,89 | 10,75 | 0,35 | +0.0% |
| IS083BR Reaterro e Compactação de Vala com Compactador | m3 | OK_PUBLICAR | 93382 | SINAPI 93382 · 08/2026 | 3 → 4 | 71,64 | 34,94 | 0,49 | +0.1% |
| OG083BR Verga de Concreto Armado | m | OK_PUBLICAR | 93187 | SINAPI 93187 · 08/2026 | 11 → 21 | 315,19 | 85,04 | 0,27 | +0.1% |
| OT005BR Limpeza do Terreno | m2 | OK_PUBLICAR | 98524 | SINAPI 98524 · 08/2026 | 1 → 1 | 2,82 | 6,50 | 2,30 | +0.1% |
| OT007BR Remoção de Calçamento de Pedra | m2 | DEJAR_RECETA | — (receta sin cambios) | — | 1 | 9,79 | 9,79 | 1,00 | DEJAR_RECETA (revisión de los 25, Oscar 28-sep-2026): 97635 es remoção CON reaprovechamiento (otro servicio) |
| OT010BR Limpeza e Capina do Terreno | m2 | OK_PUBLICAR | 98524 | SINAPI 98524 · 08/2026 | 1 → 1 | 2,41 | 6,50 | 2,70 | +0.1% |
| OT014BR Retirada de Forro (Gesso sob Laje) | m2 | OTRA_COMPOSICAO | 97631 | SINAPI 97631 · 08/2026 | 1 → 2 | 16,07 | 15,85 | 0,99 | +0.1% |
| OT022BR Movimentação de Terra com Trator de Esteiras | m3 | OK_PUBLICAR | 101116 | SINAPI 101116 · 08/2026 | 2 → 3 | 11,25 | 2,62 | 0,23 | +0.8% |
| OT026BR Reaterro e Compactação com Solo Selecionado | m3 | ADAPTAR | 94319 (6079→6081) | adaptado de SINAPI 94319 · 08/2026 | 3 → 5 | 351,24 | 114,68 | 0,33 | +0.0% |

Suma (1 unidad de cada uno): antes 55.055,65 → después 28.502,38. «Aplanado vs CCD» = costo SP de la receta aplanada contra el CCD SP publicado (en las adaptadas, Σ factor × CCD de las partes + la diferencia de precio del insumo cambiado). Si la receta ya estaba aplicada, «Antes» y «Después» coinciden.

## Detalle de las composições cambiadas y adaptadas

### IS074BR Escavação de Vala com Retroescavadeira [m3]: 90106 → 90105

vala de instalação predial: largura < 0,8 m.

_90105: ESCAVAÇÃO MECANIZADA DE VALA COM PROFUNDIDADE ATÉ 1,5 M (MÉDIA MONTANTE E JUSANTE/UMA COMPOSIÇÃO POR TRECHO), RETROESCAV. (0,26 M3), LARGURA MENOR QUE 0,8 M, EM SOLO DE 1A CATEGORIA, LOCAIS COM BAIXO NÍVEL DE INTERFERÊNCIA. AF_09/2024_

| Antes: insumo | unidad | rend. | | Después: insumo | unidad | rend. | P. SP |
|---|---|---:|---|---|---|---:|---:|
| Operador de Retroescavadeira | Hr | 0.132 | | Servente | Hr | 0.0762094 | 30,48 |
| Servente | Hr | 0.0644 | | Retroescavadeira (CHI, hora improdutiva) | Hr | 0.0375152 | 77,85 |
| Retroescavadeira | Hr | 0.1389 | | Retroescavadeira | Hr | 0.0332585 | 165,68 |

Costo SP: 30,89 → 10,75 (referencia SINAPI 10,75).

### OT014BR Retirada de Forro (Gesso sob Laje) [m2]: 97641 → 97631

Oscar: «OT014 es yeso aplicado bajo losa» → demolição de argamassas manual.

_97631: DEMOLIÇÃO DE ARGAMASSAS, DE FORMA MANUAL, SEM REAPROVEITAMENTO. AF_09/2023_

| Antes: insumo | unidad | rend. | | Después: insumo | unidad | rend. | P. SP |
|---|---|---:|---|---|---|---:|---:|
| Servente | Hr | 0.5272 | | Servente | Hr | 0.3872 | 30,48 |
|  | |  | | Pedreiro | Hr | 0.1151 | 35,18 |

Costo SP: 16,07 → 15,85 (referencia SINAPI 15,84).

### CR002BR Pintura de Portas [m2]: 102220×2 + 102193×2

esmalte 2 demãos (102220) + lixamento (102193), por m² de vano y las DOS caras de la puerta.

| Antes: insumo | unidad | rend. | | Después: insumo | unidad | rend. | P. SP |
|---|---|---:|---|---|---|---:|---:|
| Tinta Esmalte Sintético Brilhante | L | 0.3224 | | Tinta Esmalte Sintético Premium Brilhante *(nuevo)* | L | 0.2506 | 42,07 |
| Aguarrás | L | 0.3071 | | Aguarrás | L | 0.025 | 27,47 |
| Lixa para Parede | Hoja | 0.4406 | | Lixa para Parede | Hoja | 0.8 | 1,35 |
| Oficial Especializado | Hr | 0.5256 | | Pintor | Hr | 0.8692 | 36,77 |
| Servente | Hr | 0.5271 | |  | | |  |

Costo SP: 53,67 → 44,27 (referencia SINAPI 44,24).

### OT026BR Reaterro e Compactação com Solo Selecionado [m3]: 94319 (6079→6081)

94319 con el suelo 6079 (sin transporte) cambiado por 6081 (argila/barro p/ reaterro COM transporte até 10 km).

| Antes: insumo | unidad | rend. | | Después: insumo | unidad | rend. | P. SP |
|---|---|---:|---|---|---|---:|---:|
| Terra Selecionada | m3 | 1.1236 | | Terra Selecionada | m3 | 1.3889 | 57,41 |
| Pedreiro | Hr | 0.4623 | | Servente | Hr | 0.7866 | 30,48 |
| Servente | Hr | 2.3008 | | Compactador Manual de Impacto (Sapo) | Hr | 0.1962 | 46,05 |
|  | |  | | Caminhão Pipa (CHI, hora improdutiva) | Hr | 0.0006 | 84,83 |
|  | |  | | Caminhão Pipa | Hr | 0.0054 | 347,83 |

Costo SP: 351,24 → 114,68 (referencia SINAPI 114,65).

## Mapeo corregido: `br_tierra_seleccionada_m3`

SINAPI 7253 «TERRA VEGETAL (GRANEL)» → **6081 «ARGILA OU BARRO PARA ATERRO/REATERRO (COM TRANSPORTE ATE 10 KM)» (M3)**. El 7253 es tierra vegetal de jardín, no suelo de relleno (`br_tierra_negra_m3` sigue en 7253, que sí le corresponde). El SINAPI 08/2026 publica el 6081 sólo en SP; las demás capitales llevan el precio de SP con la nota «Sem preço em UF… preço de SP» (misma regla de siempre).

| Ciudad | Antes | Después |
|---|---:|---:|
| São Paulo (SP) | 235,71 | 57,41 |
| Rio de Janeiro (RJ) | 167,14 | 57,41 |
| Belo Horizonte (MG) | 188,57 | 57,41 |
| Brasília (DF) | 192,85 | 57,41 |
| Curitiba (PR) | 285,00 | 57,41 |
| Porto Alegre (RS) | 201,42 | 57,41 |
| Salvador (BA) | 167,14 | 57,41 |
| Recife (PE) | 167,14 | 57,41 |
| Fortaleza (CE) | 310,71 | 57,41 |
| Manaus (AM) | 235,71 | 57,41 |

Ítems que usan el insumo (costo SP de 1 unidad):

| Ítem | Unidad | Rend. del insumo | Antes | Después | Cambio |
|---|---|---:|---:|---:|---|
| OT026BR Reaterro e Compactação com Solo Selecionado | m3 | 1.3889 | 351,24 | 114,68 | receta nueva + precio |
| OG040BR Compactação com Rolo Pé de Carneiro | m3 | 1.2127 | 445,40 | 229,17 | sólo precio |
| OG054BR Reaterro e Compactação com Rolo Liso | m3 | 1.2753 | 406,88 | 179,49 | sólo precio |

## Insumos nuevos (21)

Id `br_sinapi_<hoja>_<código>`, en las 10 ciudades de `oficiales_BR.json` y en `mapa_sinapi_BR.csv`; `precios-sinapi-br.py` les pone el precio SINAPI de cada UF (si la UF no tiene, el de SP).

| idCanonico | Nombre | Unidad | Tipo | Categoría | Precio SP | Ítems |
|---|---|---|---|---|---:|---|
| `br_sinapi_icd_10527` | Locação de Andaime Metálico Tubular de Encaixe, tipo de Torre, Cada Painel com Largura de 1 Até 1,5 m e Altura de 1,00 m, Incluindo Diagonal | m×mes | HERRAMIENTA | Herramientas | 28,00 | AC035BR |
| `br_sinapi_ccd_5928` | Guindauto Hidráulico (CHP, hora produtiva) | Hr | HERRAMIENTA | Maquinaria | 303,67 | IE022BR |
| `br_sinapi_ccd_5849` | Trator de Esteira D7G (CHI, hora improdutiva) | Hr | HERRAMIENTA | Maquinaria | 99,95 | OT022BR |
| `br_sinapi_icd_5065` | Prego de Aço Polido com Cabeça 10 x 10 (7/8 x 17) | Kg | MATERIAL | Acero y Metal | 23,70 | AC033BR |
| `br_sinapi_icd_5066` | Prego de Aço Polido com Cabeça 12 x 12 | Kg | MATERIAL | Acero y Metal | 16,42 | AC069BR |
| `br_sinapi_icd_5075` | Prego de Aço Polido com Cabeça 18 x 30 (2 3/4 x 10) | Kg | MATERIAL | Acero y Metal | 12,46 | AC069BR |
| `br_sinapi_icd_39027` | Prego de Aço Polido com Cabeça 19 x 36 (3 1/4 x 9) | Kg | MATERIAL | Acero y Metal | 12,45 | AC069BR |
| `br_sinapi_icd_40568` | Prego de Aço Polido com Cabeça 22 x 48 (4 1/4 x 5) | Kg | MATERIAL | Acero y Metal | 12,55 | AC035BR |
| `br_sinapi_icd_4710` | Pedra Quartzito ou Calcário Laminado, Serrada, tipo Cariri, Itacolomi, Lagoa Santa, Luminária, Pirenópolis | m2 | MATERIAL | Agregados | 255,82 | AC037BR |
| `br_sinapi_icd_7614` | Transformador Trifásico de Distribuição, Potência de 150 KVA, Tensão Nominal de 15 kV, Tensão Secundaria de 220/127V | Pza | MATERIAL | Eléctrico | 24.537,33 | IE022BR |
| `br_sinapi_icd_4448` | Viga 7,5 x 15 cm em Pinus, Mista ou Equivalente da Região - Bruta | m | MATERIAL | Ferretería | 20,22 | AC035BR |
| `br_sinapi_icd_183` | Batente / Portal / Aduela / Marco em Madeira Maciça com Rebaixo, e = 3 cm, L = 14 cm, para Portas de Giro de 60 cm a 120 cm x 210 cm | Pza | MATERIAL | Madera | 240,00 | AC069BR |
| `br_sinapi_icd_4433` | Caibro Não Aparelhado 6 x 6 cm, em Macaranduba/Massaranduba, Angelim ou Equivalente da Região - Bruta | m | MATERIAL | Madera | 32,66 | IS052BR |
| `br_sinapi_icd_4417` | Sarrafo Não Aparelhado 2,5 x 7 cm, em Macaranduba/Massaranduba, Angelim, Peroba-Rosa ou Equivalente da Região - Bruta | m | MATERIAL | Madera | 9,08 | IS052BR |
| `br_sinapi_icd_6189` | Tábua Não Aparelhada 2,5 x 30 cm, em Macaranduba/Massaranduba, Angelim ou Equivalente da Região - Bruta | m | MATERIAL | Madera | 34,44 | OG083BR |
| `br_sinapi_icd_6178` | Tábua de Madeira para Piso, Cumaru/Ipê Champanhe ou Equivalente da Região, Encaixe Macho/Fêmea, 10 x 2 cm | m2 | MATERIAL | Madera | 467,16 | AC033BR |
| `br_sinapi_icd_6180` | Tábua de Madeira para Piso, Cumaru/Ipê Champanhe ou Equivalente da Região, Encaixe Macho/Fêmea, 15 x 2 cm | m2 | MATERIAL | Madera | 504,19 | AC035BR |
| `br_sinapi_icd_7319` | Tinta Asfáltica Impermeabilizante Dispersa em Água, para Materiais Cimentícios | L | MATERIAL | Pinturas | 11,70 | AC069BR |
| `br_sinapi_icd_7292` | Tinta Esmalte Sintético Premium Brilhante | L | MATERIAL | Pinturas | 42,07 | CR002BR |
| `br_sinapi_icd_35277` | Caixa de Gordura em PVC, Diâmetro Mínimo 300 mm, Diâmetro de Saída 100 mm, Capacidade Aproximada 18 Litros, com Tampa e Cesto | Pza | MATERIAL | Plomería | 441,28 | IS034BR |
| `br_sinapi_icd_3148` | Fita Veda Rosca, em PTFE, Rolo de 18 mm x 50 m (L x C) | Pza | MATERIAL | Plomería | 16,87 | IS015BR, IS016BR |

## Controles de la herramienta

- Ítems con cambios pendientes fuera de la revisión: 0.
- Ítems de la revisión convertidos: 23 de 23; DEJAR_RECETA sin tocar: IS066BR, OT007BR.
- Mayor diferencia aplanado vs CCD en la revisión: 0.83% (tolerancia 5 %).
- Antes de escribir recetas, `--aplicar` exige precio «REFERENCIA: SINAPI …» en las 10 ciudades para todo insumo usado; si falta uno, no escribe nada.

## Validación (simulación en una copia del repo, 28-09-2026)

Clon temporal de `datos--app` en 04a1e83, `python tools/fase-a-composicoes-br.py --ratio-min 0.5 --ratio-max 2 --aplicar`, y comparación contra HEAD:

- `items_BR.json`: 375 ítems, mismo orden; cambian exactamente los 23 de la revisión (19 OK_PUBLICAR + IS074BR, OT014BR, CR002BR, OT026BR). En los 23, todos los campos fuera de `insumos` y `referencia` quedan idénticos. IS066BR y OT007BR sin tocar. Versión `v20260928c-br-sinapi-revision25`.
- `oficiales_BR.json`: en las 10 ciudades, el único insumo existente que cambia es `br_tierra_seleccionada_m3` (precio y nota → SINAPI 6081); todos los demás, byte a byte iguales en precio y nota. Se agregan 21 insumos nuevos al final de cada ciudad. Versión `v20260928c-br-sinapi-202608`.
- `mapa_sinapi_BR.csv`: cambia sólo la fila de `br_tierra_seleccionada_m3` (7253 → 6081) y se agregan las 21 filas nuevas.
- `manifest.json`: sólo `catalogo_BR` y `precios_BR` suben de versión.
- Todas las líneas de los 23 ítems tienen precio «REFERENCIA: SINAPI …» > 0 en las 10 ciudades, y nombre, unidad, tipo y código coinciden con la lista de precios. Ningún ESTIMADO.
- Idempotencia: una segunda corrida con `--aplicar` no cambia nada (0 pendientes, 0 insumos nuevos, 0 mapeos a corregir).
