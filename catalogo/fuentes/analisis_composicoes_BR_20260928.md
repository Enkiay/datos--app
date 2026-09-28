# Recetas del catálogo Brasil frente a las composiciones SINAPI (análisis, 28-sep-2026)

**Sólo lectura: no se tocó `items_BR.json`.** Catálogo analizado: `catalogo/v1.0/items_BR.json` (375 ítems, recetas bolivianas ajustadas, versión v20260928-br-rendimientos). Fuente: SINAPI (Caixa/IBGE) 08/2026, hojas «Analítico» (coeficientes de cada composición) y «CCD» (costo por UF, COM desoneração), el mismo libro nacional que usan los precios (sha256 `1587f458…4aec89`).

Clases de ítem: **EQUIVALENTE** (mismo servicio, alcance y unidad) · **PARCIAL** (mismo servicio, distinto alcance: el SINAPI lo parte en varias composiciones o pone el mortero/concreto en una auxiliar) · **ADAPTADA** (no hay el servicio exacto pero sí uno de la misma familia con otra medida/espesor; se adapta y se anota «adaptado de SINAPI NNNN») · **NINGUNA** (nada parecido en el SINAPI).

## Resumen

| Clase | Ítems |
|---|---:|
| EQUIVALENTE | 111 |
| PARCIAL | 80 |
| ADAPTADA | 153 |
| NINGUNA | 31 |
| **Total** | **375** |

| Categoría | EQUIVALENTE | PARCIAL | ADAPTADA | NINGUNA |
|---|---:|---:|---:|---:|
| Inst. Sanitarias | 27 | 15 | 40 | 4 |
| Obra Gruesa | 24 | 21 | 26 | 13 |
| Acabados | 27 | 13 | 26 | 4 |
| Otros | 16 | 7 | 17 | 5 |
| Cubiertas | 4 | 8 | 13 | 1 |
| Inst. Eléctricas | 9 | 13 | 2 | 0 |
| Carpintería | 2 | 3 | 17 | 0 |
| Mampostería | 2 | 0 | 12 | 4 |

### Familias fáciles y difíciles

- **Fáciles (1:1):** movimiento de tierra (93358, 93382, 94319), demoliciones y remociones, hormigón pobre y ciclópico (96616/96620/102487), acero por kg, gaviones, adoquines de concreto y de piedra, escaleras de hormigón, losa de viguetas con EPS H20 (106058), pinturas (látex 104642/95626, esmalte), vidrios, yeso (87418/87415), contrapiso (87640), bloque de concreto (103318), drywall (sólo cambia el perfil de 92 a 70 mm), loza sanitaria (86931/86940/100858), registros, cajas sifonadas PVC, PVC PBA JEI, colector DN 100/150, cables, electroductos, split, transformador.
- **Parciales por alcance:** hormigón armado por m³ (ArqOn = encofrado + armadura + hormigón; el SINAPI los separa en 3 composiciones y el hormigón viene usinado → cambiar por 94965 donde ArqOn usa hormigonera); cubiertas (el telhamento SINAPI no trae la estructura de madera: sumar 92543/92539); revoques (chapisco + emboço/massa única) y pisos (cerámica con colante y rejunte + contrapiso aparte); «puntos» eléctricos e hidráulicos (el SINAPI 08/2026 ya no tiene la composición «ponto»: se arman con aparato + cable/tubo por metro + caja + conexiones).
- **Adaptadas:** mampostería de ladrillo boliviano 24×15×11 (no existe: cambiar el bloque y la cantidad por m² en 103352/103354/103334), calamina ondulada N°28/N°33 (el SINAPI sólo tiene trapezoidal 0,5 mm), puertas de 1,00 m y carpintería por pieza (kits fijos de 60-90 cm o m²), fosas plásticas (tanque séptico premoldeado 98052), sumideros y pozos de visita, tanques de agua > 3000 L, PEAD de diámetros que no están, tubería galvanizada 1/2" y 3/4" (sólo existe como ramal de gas).
- **Recetas ArqOn con cantidades o unidades incoherentes** (conviene corregirlas antes de adoptar el SINAPI): UH022 estaca por m con cantidades de 1 m³; OG059/OG060 5 y 8 piezas por pieza; OG057 5,86 m³ de piedra por m³; OG001 20 kg de cemento por m³; OG042 0,08 m³/m² para e = 17 cm; CU014 teja en m en vez de m²; OG031 dice manta y es pintura; AC067 0,037 L de pintura/m² (≈10× menos); AC010 0,26 kg de cemento para 0,02 m³ de arena; AC015 ≈1 mm de revoque; MP013/MP015 drywall 2 caras con 1,5-1,8 m² de placa/m² (debería ≈2,1); AC008 rodapié de ≈33 cm; AC040/AC044 ≈0,04 m³ de arena por m de rodapié; AC009 «Forro de Gesso» es yeso aplicado, no placa; IS021/IS022 «PVC soldável» con tubo PPR y conexiones galvanizadas; IS071 berço e = 5 cm con 1,13 m³/m; IS067-070 ≈1 unión de termofusión por metro (real 0,1-0,17).


## Costo directo en São Paulo: receta ArqOn vs composición SINAPI (ítems EQUIVALENTE representativos)

- **Hoy**: receta ArqOn con los precios BR actuales (SINAPI donde ya hay mapa, estimado Bolivia en el resto).
- **Receta ArqOn, precios SINAPI**: los mismos coeficientes ArqOn, pero todos los insumos con precio SINAPI SP (propuesta de precios: MAPEAR/SUSTITUIR; QUITAR = 0).
- **Composición SINAPI**: costo CCD São Paulo de la composición (coeficientes SINAPI, precios SINAPI, mano de obra con encargos) × factor de unidad.

| Ítem | Unidad | Composición SINAPI | Hoy | Receta ArqOn, precios SINAPI | Composición SINAPI | SINAPI / ArqOn |
|---|---|---|---:|---:|---:|---:|
| AC002BR Reboco de Teto sobre Laje | m2 | 87415 | 132,71 | 132,71 | 40,73 | 0,31 |
| AC017BR Reboco Interno de Gesso | m2 | 87418 | 97,79 | 97,79 | 22,52 | 0,23 |
| AC019BR Contrapiso de Cimento sobre Laje | m2 | 87640 | 74,28 | 74,28 | 49,96 | 0,67 |
| CR002BR Pintura de Portas | m2 | 102220 | 53,67 | 53,67 | 19,60 | 0,37 |
| CU001BR Retirada de Cobertura de Telha de Aço Galvanizado | m2 | 97647 | 21,37 | 21,37 | 4,91 | 0,23 |
| CU015BR Cobertura Termoacústica (Telha Sanduíche) E=30 Mm Densidade 40 | m2 | 94216 | 262,18 | 213,50 | 215,91 | 1,01 |
| CU018BR Cumeeira de Telha Colonial | m | 94221 | 46,15 | 46,15 | 47,65 | 1,03 |
| IE006BR Fornecimento e Instalação de Fio de Cobre 10 mm² (AWG 8) | m | 91932 | 14,11 | 14,11 | 21,21 | 1,50 |
| IE007BR Fornecimento e Instalação de Fio de Cobre 6 mm² (AWG 10) | m | 91930 | 8,26 | 8,26 | 11,97 | 1,45 |
| IE008BR Fornecimento e Instalação de Fio de Cobre 4 mm² (AWG 12) | m | 91928 | 6,41 | 6,41 | 8,61 | 1,34 |
| IS005BR Lavatório (Louça) | Pza | 86940 | 869,42 | 781,59 | 1167,14 | 1,49 |
| IS011BR Fornecimento e Instalação de Acessórios de Banheiro | Pza | 95546 | 214,68 | 86,03 | 234,64 | 2,73 |
| IS013BR Mictório (Louça) | Pza | 100858 | 452,18 | 831,66 | 856,37 | 1,03 |
| MP002BR Alvenaria de Bloco de Concreto 3 Furos E=15 Cm | m2 | 103318 | 152,96 | 145,85 | 114,18 | 0,78 |
| MP003BR Alvenaria de Bloco de Vidro 20x20 Cm | m2 | 101164 | 558,38 | 696,12 | 689,62 | 0,99 |

## Lado a lado (coeficientes) de los representativos

Coeficiente por unidad del ítem. En el SINAPI, una línea COMPOSICAO es una composición auxiliar anidada (mortero, concreto, mano de obra con encargos); se indica su profundidad. La receta ArqOn trae esos morteros ya abiertos en cemento/cal/arena.

### AC002BR Reboco de Teto sobre Laje [m2] ↔ SINAPI 87415 [M2] — profundidad de anidado: 1

_APLICAÇÃO MANUAL DE GESSO DESEMPENADO (SEM TALISCAS) EM TETO DE AMBIENTES DE ÁREA ENTRE 5M² E 10M², ESPESSURA DE 1,0CM. AF_03/2023_

| ArqOn: insumo | coef. | SINAPI equivalente del insumo |
|---|---:|---|
| Estuque (Gesso para Acabamento) (Kg) | 18.2987 | 3315 ×1 |
| Pedreiro (Hr) | 1.7528 | 88309 ×1 |
| Servente (Hr) | 1.8446 | 88316 ×1 |

| SINAPI: tipo | código | descripción | unidad | coef. |
|---|---|---|---|---:|
| COMPOSICAO | 88316 | SERVENTE COM ENCARGOS COMPLEMENTARES | H | 0.19117 |
| COMPOSICAO | 88269 | GESSEIRO COM ENCARGOS COMPLEMENTARES | H | 0.6037 |
| INSUMO | 3315 | GESSO EM PO PARA REVESTIMENTOS/MOLDURAS/SANCAS E USO GERAL | KG | 17.07379 |

### AC017BR Reboco Interno de Gesso [m2] ↔ SINAPI 87418 [M2] — profundidad de anidado: 1

_APLICAÇÃO MANUAL DE GESSO DESEMPENADO (SEM TALISCAS) EM PAREDES, ESPESSURA DE 0,5CM. AF_03/2023_

| ArqOn: insumo | coef. | SINAPI equivalente del insumo |
|---|---:|---|
| Estuque (Gesso para Acabamento) (Kg) | 11.2477 | 3315 ×1 |
| Pedreiro (Hr) | 1.3843 | 88309 ×1 |
| Servente (Hr) | 1.3118 | 88316 ×1 |

| SINAPI: tipo | código | descripción | unidad | coef. |
|---|---|---|---|---:|
| COMPOSICAO | 88316 | SERVENTE COM ENCARGOS COMPLEMENTARES | H | 0.10443 |
| COMPOSICAO | 88269 | GESSEIRO COM ENCARGOS COMPLEMENTARES | H | 0.32979 |
| INSUMO | 3315 | GESSO EM PO PARA REVESTIMENTOS/MOLDURAS/SANCAS E USO GERAL | KG | 9.66321 |

### AC019BR Contrapiso de Cimento sobre Laje [m2] ↔ SINAPI 87640 [M2] — profundidad de anidado: 2

_CONTRAPISO EM ARGAMASSA TRAÇO 1:4 (CIMENTO E AREIA), PREPARO MECÂNICO COM BETONEIRA 400 L, APLICADO EM ÁREAS SECAS SOBRE LAJE, ADERIDO, ACABAMENTO NÃO REFORÇADO, ESPESSURA 4CM. AF_07/2021_

| ArqOn: insumo | coef. | SINAPI equivalente del insumo |
|---|---:|---|
| Cimento Portland (Kg) | 10.7093 | 1379 ×1 |
| Areia Fina (m3) | 0.05827 | 366 ×1 |
| Pedreiro (Hr) | 0.7913 | 88309 ×1 |
| Servente (Hr) | 1.1019 | 88316 ×1 |

| SINAPI: tipo | código | descripción | unidad | coef. |
|---|---|---|---|---:|
| COMPOSICAO | 88316 | SERVENTE COM ENCARGOS COMPLEMENTARES | H | 0.136 |
| COMPOSICAO | 88309 | PEDREIRO COM ENCARGOS COMPLEMENTARES | H | 0.271 |
| COMPOSICAO | 87301 | ARGAMASSA TRAÇO 1:4 (EM VOLUME DE CIMENTO E AREIA MÉDIA ÚMIDA) PARA CONTRAPISO, PREPARO MECÂNIC | M3 | 0.053 |
| INSUMO | 7334 | ADITIVO ADESIVO LIQUIDO PARA ARGAMASSAS DE REVESTIMENTOS CIMENTICIOS | L | 0.21 |
| INSUMO | 1379 | CIMENTO PORTLAND COMPOSTO CP II-32 | KG | 0.5 |

### CR002BR Pintura de Portas [m2] ↔ SINAPI 102220 [M2] — profundidad de anidado: 1

_PINTURA TINTA DE ACABAMENTO (PIGMENTADA) ESMALTE SINTÉTICO BRILHANTE EM MADEIRA, 2 DEMÃOS. AF_01/2021_

| ArqOn: insumo | coef. | SINAPI equivalente del insumo |
|---|---:|---|
| Tinta Esmalte Sintético Brilhante (L) | 0.3224 | 43647 ×1 |
| Aguarrás (L) | 0.3071 | 5318 ×1 |
| Lixa para Parede (Hoja) | 0.4406 | 3767 ×1 |
| Oficial Especializado (Hr) | 0.5256 | 88309 ×1 |
| Servente (Hr) | 0.5271 | 88316 ×1 |

| SINAPI: tipo | código | descripción | unidad | coef. |
|---|---|---|---|---:|
| COMPOSICAO | 88310 | PINTOR COM ENCARGOS COMPLEMENTARES | H | 0.3805 |
| INSUMO | 7292 | TINTA ESMALTE SINTETICO PREMIUM BRILHANTE | L | 0.1253 |
| INSUMO | 5318 | DILUENTE AGUARRAS | L | 0.0125 |

### CU001BR Retirada de Cobertura de Telha de Aço Galvanizado [m2] ↔ SINAPI 97647 [M2] — profundidad de anidado: 1

_REMOÇÃO DE TELHAS DE FIBROCIMENTO METÁLICA E CERÂMICA, DE FORMA MANUAL, SEM REAPROVEITAMENTO. AF_09/2023_

| ArqOn: insumo | coef. | SINAPI equivalente del insumo |
|---|---:|---|
| Servente (Hr) | 0.7012 | 88316 ×1 |

| SINAPI: tipo | código | descripción | unidad | coef. |
|---|---|---|---|---:|
| COMPOSICAO | 88323 | TELHADISTA COM ENCARGOS COMPLEMENTARES | H | 0.0408 |
| COMPOSICAO | 88316 | SERVENTE COM ENCARGOS COMPLEMENTARES | H | 0.1153 |

### CU015BR Cobertura Termoacústica (Telha Sanduíche) E=30 Mm Densidade 40 [m2] ↔ SINAPI 94216 [M2] — profundidad de anidado: 1

_TELHAMENTO COM TELHA METÁLICA TERMOACÚSTICA E = 30 MM, COM ATÉ 2 ÁGUAS, INCLUSO IÇAMENTO. AF_06/2026_

| ArqOn: insumo | coef. | SINAPI equivalente del insumo |
|---|---:|---|
| Telha Sanduíche com Poliuretano E=30 Mm (m2) | 1.027 | 40740 ×1 |
| Parafuso Tirefond de 4 1/2X1/4″ (Pza) | 2.442 | 13294 ×1 |
| Técnico Especializado (Hr) | 0.4393 | 88279 ×1 |
| Servente (Hr) | 0.4596 | 88316 ×1 |

| SINAPI: tipo | código | descripción | unidad | coef. |
|---|---|---|---|---:|
| COMPOSICAO | 93282 | GUINCHO ELÉTRICO DE COLUNA, CAPACIDADE 400 KG, COM MOTO FREIO, MOTOR TRIFÁSICO DE 1,25 CV - CHI | CHI | 0.0021831 |
| COMPOSICAO | 93281 | GUINCHO ELÉTRICO DE COLUNA, CAPACIDADE 400 KG, COM MOTO FREIO, MOTOR TRIFÁSICO DE 1,25 CV - CHP | CHP | 0.000976 |
| COMPOSICAO | 88323 | TELHADISTA COM ENCARGOS COMPLEMENTARES | H | 0.1089338 |
| COMPOSICAO | 88316 | SERVENTE COM ENCARGOS COMPLEMENTARES | H | 0.1952328 |
| INSUMO | 40740 | TELHA GALVALUME COM ISOLAMENTO TERMOACUSTICO EM ESPUMA RIGIDA DE POLIURETANO (PU) INJETADO, ESP | M2 | 1.1456858 |
| INSUMO | 11029 | HASTE RETA PARA GANCHO DE FERRO GALVANIZADO, COM ROSCA 1/4" X 30 CM PARA FIXACAO DE TELHA METAL | CJ | 4.15 |

### CU018BR Cumeeira de Telha Colonial [m] ↔ SINAPI 94221 [M] — profundidad de anidado: 2

_CUMEEIRA PARA TELHA CERÂMICA EMBOÇADA COM ARGAMASSA TRAÇO 1:2:9 (CIMENTO, CAL E AREIA) PARA TELHADOS COM ATÉ 2 ÁGUAS, INCLUSO TRANSPORTE VERTICAL. AF_06/2026_

| ArqOn: insumo | coef. | SINAPI equivalente del insumo |
|---|---:|---|
| Telha Colonial Cerâmica (Pza) | 3.4479 | 7173 ×0.001 |
| Madeira para Construção (p2) | 1.9563 | 4006 ×0.00236 |
| Pregos (Kg) | 0.02764 | 5069 ×1 |
| Pedreiro (Hr) | 0.3501 | 88309 ×1 |
| Servente (Hr) | 0.4367 | 88316 ×1 |

| SINAPI: tipo | código | descripción | unidad | coef. |
|---|---|---|---|---:|
| COMPOSICAO | 93282 | GUINCHO ELÉTRICO DE COLUNA, CAPACIDADE 400 KG, COM MOTO FREIO, MOTOR TRIFÁSICO DE 1,25 CV - CHI | CHI | 0.0140741 |
| COMPOSICAO | 93281 | GUINCHO ELÉTRICO DE COLUNA, CAPACIDADE 400 KG, COM MOTO FREIO, MOTOR TRIFÁSICO DE 1,25 CV - CHP | CHP | 0.0062922 |
| COMPOSICAO | 88323 | TELHADISTA COM ENCARGOS COMPLEMENTARES | H | 0.1654262 |
| COMPOSICAO | 88316 | SERVENTE COM ENCARGOS COMPLEMENTARES | H | 0.2265251 |
| COMPOSICAO | 87337 | ARGAMASSA TRAÇO 1:2:9 (EM VOLUME DE CIMENTO, CAL E AREIA MÉDIA ÚMIDA) PARA EMBOÇO/MASSA ÚNICA/A | M3 | 0.0117264 |
| INSUMO | 7181 | CUMEEIRA PARA TELHA CERAMICA, COMPRIMENTO DE *41* CM, RENDIMENTO DE *3* TELHAS/M | UN | 3 |

### IE006BR Fornecimento e Instalação de Fio de Cobre 10 mm² (AWG 8) [m] ↔ SINAPI 91932 [M] — profundidad de anidado: 1

_CABO DE COBRE FLEXÍVEL ISOLADO, 10 MM², ANTI-CHAMA 450/750 V, PARA CIRCUITOS TERMINAIS - FORNECIMENTO E INSTALAÇÃO. AF_03/2023_

| ArqOn: insumo | coef. | SINAPI equivalente del insumo |
|---|---:|---|
| Fio de Cobre 10 mm² (AWG 8) (m) | 0.9792 | 980 ×1 |
| Eletricista (Hr) | 0.0277 | 88264 ×1 |
| Servente (Hr) | 0.02634 | 88316 ×1 |

| SINAPI: tipo | código | descripción | unidad | coef. |
|---|---|---|---|---:|
| COMPOSICAO | 88264 | ELETRICISTA COM ENCARGOS COMPLEMENTARES | H | 0.076 |
| COMPOSICAO | 88247 | AUXILIAR DE ELETRICISTA COM ENCARGOS COMPLEMENTARES | H | 0.076 |
| INSUMO | 21127 | FITA ISOLANTE ADESIVA ANTICHAMA, USO ATE 750 V, EM ROLO DE 19 MM X 5 M | UN | 0.0094 |
| INSUMO | 980 | CABO DE COBRE, FLEXIVEL, CLASSE 4 OU 5, ISOLACAO EM PVC/A, ANTICHAMA BWF-B, 1 CONDUTOR, 450/750 | M | 1.2434 |

### IE007BR Fornecimento e Instalação de Fio de Cobre 6 mm² (AWG 10) [m] ↔ SINAPI 91930 [M] — profundidad de anidado: 1

_CABO DE COBRE FLEXÍVEL ISOLADO, 6 MM², ANTI-CHAMA 450/750 V, PARA CIRCUITOS TERMINAIS - FORNECIMENTO E INSTALAÇÃO. AF_03/2023_

| ArqOn: insumo | coef. | SINAPI equivalente del insumo |
|---|---:|---|
| Fio de Cobre 6 mm² (AWG 10) (m) | 0.9711 | 982 ×1 |
| Eletricista (Hr) | 0.02634 | 88264 ×1 |
| Servente (Hr) | 0.0278 | 88316 ×1 |

| SINAPI: tipo | código | descripción | unidad | coef. |
|---|---|---|---|---:|
| COMPOSICAO | 88264 | ELETRICISTA COM ENCARGOS COMPLEMENTARES | H | 0.051 |
| COMPOSICAO | 88247 | AUXILIAR DE ELETRICISTA COM ENCARGOS COMPLEMENTARES | H | 0.051 |
| INSUMO | 21127 | FITA ISOLANTE ADESIVA ANTICHAMA, USO ATE 750 V, EM ROLO DE 19 MM X 5 M | UN | 0.0094 |
| INSUMO | 982 | CABO DE COBRE, FLEXIVEL, CLASSE 4 OU 5, ISOLACAO EM PVC/A, ANTICHAMA BWF-B, 1 CONDUTOR, 450/750 | M | 1.2434 |

### IE008BR Fornecimento e Instalação de Fio de Cobre 4 mm² (AWG 12) [m] ↔ SINAPI 91928 [M] — profundidad de anidado: 1

_CABO DE COBRE FLEXÍVEL ISOLADO, 4 MM², ANTI-CHAMA 450/750 V, PARA CIRCUITOS TERMINAIS - FORNECIMENTO E INSTALAÇÃO. AF_03/2023_

| ArqOn: insumo | coef. | SINAPI equivalente del insumo |
|---|---:|---|
| Fio de Cobre 4 mm² (AWG 12) (m) | 0.9721 | 981 ×1 |
| Eletricista (Hr) | 0.02781 | 88264 ×1 |
| Servente (Hr) | 0.02777 | 88316 ×1 |

| SINAPI: tipo | código | descripción | unidad | coef. |
|---|---|---|---|---:|
| COMPOSICAO | 88264 | ELETRICISTA COM ENCARGOS COMPLEMENTARES | H | 0.039 |
| COMPOSICAO | 88247 | AUXILIAR DE ELETRICISTA COM ENCARGOS COMPLEMENTARES | H | 0.039 |
| INSUMO | 21127 | FITA ISOLANTE ADESIVA ANTICHAMA, USO ATE 750 V, EM ROLO DE 19 MM X 5 M | UN | 0.0094 |
| INSUMO | 981 | CABO DE COBRE, FLEXIVEL, CLASSE 4 OU 5, ISOLACAO EM PVC/A, ANTICHAMA BWF-B, 1 CONDUTOR, 450/750 | M | 1.2434 |

### IS005BR Lavatório (Louça) [Pza] ↔ SINAPI 86940 [UN] — profundidad de anidado: 2

_LAVATÓRIO LOUÇA BRANCA COM COLUNA, 45 X 55 CM OU EQUIVALENTE, PADRÃO MÉDIO, INCLUSO SIFÃO TIPO GARRAFA, VÁLVULA E ENGATE FLEXÍVEL DE 40 CM EM METAL CROMADO, COM APARELHO MISTURADOR PADRÃO MÉDIO - FORNECIMENTO E INSTALAÇÃO. AF_02/2026_

| ArqOn: insumo | coef. | SINAPI equivalente del insumo |
|---|---:|---|
| Cimento Branco (Kg) | 0.3908 | 1380 ×1 |
| Engate Flexível (Pza) | 1.0259 | 6141 ×1 |
| Lavatório Branco com Acessórios (Pza) | 1.0271 | 10426 ×1 |
| Misturador para Lavatório Bras. (Pza) | 1.0227 | 11769 ×1 |
| Sifão de PVC (Pza) | 1.0201 | 6149 ×1 |
| Encanador Especializado (Hr) | 2.0339 | 88267 ×1 |
| Servente (Hr) | 1.8525 | 88316 ×1 |

| SINAPI: tipo | código | descripción | unidad | coef. |
|---|---|---|---|---:|
| COMPOSICAO | 86905 | APARELHO MISTURADOR DE MESA PARA LAVATÓRIO, PADRÃO MÉDIO - FORNECIMENTO E INSTALAÇÃO. AF_02/202 | UN | 1 |
| COMPOSICAO | 86903 | LAVATÓRIO LOUÇA BRANCA COM COLUNA, *54 X 44* CM OU EQUIVALENTE, PADRÃO MÉDIO - FORNECIMENTO E I | UN | 1 |
| COMPOSICAO | 86887 | ENGATE FLEXÍVEL EM INOX, 1/2" X 40 CM - FORNECIMENTO E INSTALAÇÃO. AF_02/2026 | UN | 2 |
| COMPOSICAO | 86881 | SIFÃO DO TIPO GARRAFA EM METAL CROMADO 1" X 1.1/2" - FORNECIMENTO E INSTALAÇÃO. AF_02/2026 | UN | 1 |
| COMPOSICAO | 86877 | VÁLVULA EM METAL CROMADO 1.1/2" X 1.1/2" PARA TANQUE OU LAVATÓRIO, COM OU SEM LADRÃO - FORNECIM | UN | 1 |

### IS011BR Fornecimento e Instalação de Acessórios de Banheiro [Pza] ↔ SINAPI 95546 [UN] — profundidad de anidado: 1

_KIT DE ACESSÓRIOS PARA BANHEIRO EM METAL CROMADO, 5 PEÇAS, INCLUSO FIXAÇÃO. AF_02/2026_

| ArqOn: insumo | coef. | SINAPI equivalente del insumo |
|---|---:|---|
| Jogo de Acessórios para Banheiro (Pza) | 0.9746 | QUITAR |
| Pedreiro (Hr) | 0.9201 | 88309 ×1 |
| Servente (Hr) | 1.7605 | 88316 ×1 |

| SINAPI: tipo | código | descripción | unidad | coef. |
|---|---|---|---|---:|
| COMPOSICAO | 88316 | SERVENTE COM ENCARGOS COMPLEMENTARES | H | 0.8662572 |
| COMPOSICAO | 88267 | ENCANADOR OU BOMBEIRO HIDRÁULICO COM ENCARGOS COMPLEMENTARES | H | 2.256828 |
| INSUMO | 39398 | KIT DE ACESSORIOS PARA BANHEIRO EM METAL CROMADO, 5 PECAS | UN | 1 |

### IS013BR Mictório (Louça) [Pza] ↔ SINAPI 100858 [UN] — profundidad de anidado: 1

_MICTÓRIO SIFONADO COM VÁLVULA DE DESCARGA EM LOUÇA BRANCA - PADRÃO MÉDIO - FORNECIMENTO E INSTALAÇÃO. AF_02/2026_

| ArqOn: insumo | coef. | SINAPI equivalente del insumo |
|---|---:|---|
| Mictório Branco com Sifão (Pza) | 0.9781 | 10432 ×1 |
| Válvula para Mictório (Pza) | 1.0263 | 21112 ×1 |
| Engate Flexível (Pza) | 0.9745 | 6141 ×1 |
| Encanador Especializado (Hr) | 1.3847 | 88267 ×1 |

| SINAPI: tipo | código | descripción | unidad | coef. |
|---|---|---|---|---:|
| COMPOSICAO | 88316 | SERVENTE COM ENCARGOS COMPLEMENTARES | H | 0.4105986 |
| COMPOSICAO | 88267 | ENCANADOR OU BOMBEIRO HIDRÁULICO COM ENCARGOS COMPLEMENTARES | H | 1.0697173 |
| INSUMO | 21112 | VALVULA DE DESCARGA EM METAL CROMADO PARA MICTORIO COM ACIONAMENTO POR PRESSAO E FECHAMENTO AUT | UN | 1 |
| INSUMO | 10432 | MICTORIO INDIVIDUAL, SIFONADO, DE LOUCA BRANCA, SEM COMPLEMENTOS | UN | 1 |
| INSUMO | 4351 | PARAFUSO NIQUELADO 3 1/2" COM ACABAMENTO CROMADO PARA FIXAR PECA SANITARIA, INCLUI PORCA CEGA,  | UN | 2 |
| INSUMO | 3146 | FITA VEDA ROSCA, EM PTFE, ROLO DE 18 MM X 10 M (L X C) | UN | 0.021 |

### MP002BR Alvenaria de Bloco de Concreto 3 Furos E=15 Cm [m2] ↔ SINAPI 103318 [M2] — profundidad de anidado: 2

_ALVENARIA DE VEDAÇÃO DE BLOCOS VAZADOS DE CONCRETO DE 14X19X39 CM (ESPESSURA 14 CM) E ARGAMASSA DE ASSENTAMENTO COM PREPARO EM BETONEIRA. AF_08/2026_

| ArqOn: insumo | coef. | SINAPI equivalente del insumo |
|---|---:|---|
| Cimento Portland (Kg) | 8.7431 | 1379 ×1 |
| Areia Fina (m3) | 0.03915 | 366 ×1 |
| Bloco de Concreto 3 Furos E=15 Cm (Pza) | 12.9152 | 651 ×1 |
| Pedreiro (Hr) | 1.1426 | 88309 ×1 |
| Servente (Hr) | 1.3848 | 88316 ×1 |

| SINAPI: tipo | código | descripción | unidad | coef. |
|---|---|---|---|---:|
| COMPOSICAO | 88316 | SERVENTE COM ENCARGOS COMPLEMENTARES | H | 0.4898684 |
| COMPOSICAO | 88309 | PEDREIRO COM ENCARGOS COMPLEMENTARES | H | 0.9797368 |
| COMPOSICAO | 87292 | ARGAMASSA TRAÇO 1:2:8 (EM VOLUME DE CIMENTO, CAL E AREIA MÉDIA ÚMIDA) PARA EMBOÇO/MASSA ÚNICA/A | M3 | 0.0110741 |
| INSUMO | 37395 | PINO DE ACO COM FURO, HASTE = 27 MM (ACAO DIRETA) | CENTO | 0.019336 |
| INSUMO | 34547 | TELA DE ACO SOLDADA GALVANIZADA/ZINCADA PARA ALVENARIA, FIO D = *1,20 A 1,70* MM, MALHA 15 X 15 | M | 0.8057 |
| INSUMO | 651 | BLOCO DE VEDACAO DE CONCRETO 14 X 19 X 39 CM (CLASSE C - NBR 6136) | UN | 13.1499 |

### MP003BR Alvenaria de Bloco de Vidro 20x20 Cm [m2] ↔ SINAPI 101164 [M2] — profundidad de anidado: 2

_ALVENARIA DE VEDAÇÃO COM BLOCO DE VIDRO, TIPO CANELADO, DE 8X19X19CM E ARGAMASSA DE ASSENTAMENTO COM PREPARO EM BETONEIRA. AF_05/2020_

| ArqOn: insumo | coef. | SINAPI equivalente del insumo |
|---|---:|---|
| Bloco de Vidro 20 X 20 Cm (Pza) | 25.6509 | 716 ×1 |
| Cimento Portland (Kg) | 3.4102 | 1379 ×1 |
| Areia Fina (m3) | 0.02044 | 366 ×1 |
| Cimento Branco (Kg) | 0.4863 | 1380 ×1 |
| Pedreiro (Hr) | 2.2897 | 88309 ×1 |
| Servente (Hr) | 2.7796 | 88316 ×1 |

| SINAPI: tipo | código | descripción | unidad | coef. |
|---|---|---|---|---:|
| COMPOSICAO | 88316 | SERVENTE COM ENCARGOS COMPLEMENTARES | H | 2.1 |
| COMPOSICAO | 88309 | PEDREIRO COM ENCARGOS COMPLEMENTARES | H | 4.199 |
| COMPOSICAO | 87292 | ARGAMASSA TRAÇO 1:2:8 (EM VOLUME DE CIMENTO, CAL E AREIA MÉDIA ÚMIDA) PARA EMBOÇO/MASSA ÚNICA/A | M3 | 0.017 |
| INSUMO | 43059 | ACO CA-60, 4,2 MM, OU 5,0 MM, OU 6,0 MM, OU 7,0 MM, VERGALHAO | KG | 0.545 |
| INSUMO | 715 | BLOCO / TIJOLO DE VIDRO INCOLOR, CANELADO / ONDULADO, *19 X 19 X 8* CM (A X L X E) | UN | 25.68 |

## EQUIVALENTE

| Ítem | Unidad | Composición(es) SINAPI | Adaptación / nota | Hoy SP | Composición SP |
|---|---|---|---|---:|---:|
| AC002BR Reboco de Teto sobre Laje | m2 | 87415 | Gesso desempenado en teto 1,0 cm (17,07 kg vs 18,3 kg ArqOn); alt. cementicia: 87882 chapisco teto + 90406 massa única teto 17,5 mm | 132,71 | 40,73 |
| AC017BR Reboco Interno de Gesso | m2 | 87418 | Gesso desempenado en paredes 0,5 cm (9,66 kg vs 11,25 kg ArqOn) | 97,79 | 22,52 |
| AC019BR Contrapiso de Cimento sobre Laje | m2 | 87640 | Contrapiso 1:4 betoneira, áreas secas sobre laje, aderido, e=4 cm (ArqOn ~0,058 m3 areia ≈ 4-5 cm); alt. 87630 (3 cm) | 74,28 | 49,96 |
| AC030BR Piso de Porcelanato com Argamassa Colante | m2 | 87263 | Porcelanato 60x60 com argamassa colante AC III y rejunte (ArqOn con cimento branco) | 200,81 | 108,82 |
| AC033BR Piso de Tábua Corrida E=1.9 Cm | m2 | 101746 | Assoalho de madeira machihembrado (tábua 10x2) com cola PVA e pregos; composición _PS | 281,54 | 607,03 |
| AC034BR Piso Laminado Flutuante | m2 | 98683 | Piso laminado interno; sin costo SP publicado (0) en 08/2026 | 167,30 | — |
| AC035BR Piso de Madeira Macho-e-Fêmea de Cedro com Vigamento | m2 | 105090 | Piso de madeira macho-fêmea sobre vigotas 7,5x15; cambiar especie a cedro si se quiere | 273,09 | 593,91 |
| AC037BR Piso de Pedra São Tomé | m2 | 101731 | Pedra São Tomé sobre argamassa 1:3 (incluye colante AC III) | 194,43 | 392,49 |
| AC042BR Rodapé de Madeira Cedro | m | 101739 | Rodapé de madeira 7 cm (≈3″); ArqOn fija con parafuso+bucha en vez de cola+pregos | 51,52 | 62,63 |
| AC045BR Condutor de Esgoto em PVC 4″ | m | 89800 | Tubo PVC esgoto série normal DN100 en prumada; alt. 89714 si es ramal | 57,41 | 39,52 |
| AC048BR Pintura Anticorrosiva para Grade | m2 | 100722 | Fundo anticorrosivo tipo zarcão a rolo/pincel en superficie metálica, por demão (ArqOn 1 demão); medir área real de la grade | 24,47 | 30,20 |
| AC049BR Pintura de Beirais | m2 | 104640 | Látex acrílica standard en teto, 2 demãos (intradós del beiral); alt. 95626 si se trata como fachada | 33,87 | 15,62 |
| AC050BR Pintura de Concreto Aparente Externo | m2 | 95626 | Látex acrílica externa 2 demãos sobre concreto aparente; selador aparte 88415 | 39,49 | 18,58 |
| AC057BR Divisória Interna em Vidro Temperado (10 Mm) | m2 | 102235 | Divisória fixa em vidro temperado 10 mm sin abertura (_PS) | 725,75 | 532,67 |
| AC058BR Fachada Pele de Vidro Refletivo com Estrutura de Alumínio | m2 | 104099 | Fachada cortina stick sin abertura; sin costo SP publicado (0) | 818,44 | — |
| AC059BR Assentamento de Vidro (6 Mm) | m2 | 102156 | Vidro liso incolor 6 mm en esquadria de madeira; alt. 102166 en alumínio/PVC | 139,94 | 243,15 |
| AC061BR Assentamento de Vidro Duplo (3 Mm) | m2 | 102151 | «Duplo» es la designación boliviana del espesor 3 mm, no vidrio insulado: vidro liso 3 mm en madeira | 81,57 | 180,29 |
| AC062BR Assentamento de Vidro Triplo (4 Mm) | m2 | 102152 | «Triplo» = 4 mm (designación boliviana): vidro liso 4 mm en madeira | 205,28 | 199,11 |
| AC063BR Piso em Carpete | m2 | 106784 | Carpete em manta e=9-10 mm; sin costo SP (0). ArqOn con 37 % de pérdida | 88,95 | — |
| AC064BR Piso em Carpete em Rolo | m2 | 106783 | Carpete em manta (agulhado) e=6-7 mm; sin costo SP (0) | 63,89 | — |
| AC069BR Batente de Madeira 2″x4″ (Guanandi) | Pza | 90806 | Batente de madeira fijado con argamassa, padrão médio (jogo); ArqOn 2″x4″ guanandi vs marco 3x14 cm | 245,83 | 541,55 |
| UA002BR Reboco de Gesso Liso | m2 | 87418 | Gesso desempenado en paredes 0,5 cm; ArqOn consume 4,6 kg/m2 vs 9,66 kg SINAPI (revisar consumo) | 27,15 | 22,52 |
| UA003BR Revestimento Cerâmico Nacional | m2 | 87269 | Cerámica esmaltada parede interna 25x35 (ArqOn 30x30, mismo insumo ≤2025 cm2) con argamassa colante AC I; SINAPI incluye rejunte (0,29 kg) que ArqOn no trae | 72,84 | 66,03 |
| UA004BR Pintura Látex Interna | m2 | 104642 | Látex acrílica standard paredes, 2 demãos; no incluye selador ni massa (ArqOn tampoco, sólo lixa) | 20,95 | 12,62 |
| UA005BR Pintura Látex Externa | m2 | 95626 | Látex acrílica paredes externas de casas, 2 demãos; selador aparte (88415) si se quiere | 34,31 | 18,58 |
| UA006BR Piso de Cimento Queimado | m2 | 106788 | Piso cimentado 1:3 liso e=1,5 cm (queimado = liso con polvilhado de cimento); SINAPI incluye junta plástica 1 m/m2 | 38,69 | 33,88 |
| UA007BR Impermeabilização | m2 | 98557 | Emulsão asfáltica 2 demãos, 1,5 kg/m2 (ArqOn 1,47 kg) | 28,72 | 45,74 |
| CR002BR Pintura de Portas | m2 | 102220 | Esmalte sintético brillante en madera 2 manos; fondo 102197 opcional | 53,67 | 19,60 |
| CR018BR Portão Metálico com Tela de Alambrado | m2 | 106463 | Portão de abrir tubos galvanizados con tela, completo; sin precio SP (0) | 737,74 | — |
| CU001BR Retirada de Cobertura de Telha de Aço Galvanizado | m2 | 97647 | remoção manual de telhas sin reaprovechamiento; si hay reaprovechamiento no existe composición | 21,37 | 4,91 |
| CU015BR Cobertura Termoacústica (Telha Sanduíche) E=30 Mm Densidade 40 | m2 | 94216 | telha termoacústica PU 30 mm, sin estructura, incluye fijación | 262,18 | 215,91 |
| CU018BR Cumeeira de Telha Colonial | m | 94221 | cumeeira telha cerâmica até 2 águas; SINAPI emboça con argamassa 1:2:9, ArqOn fija con madera | 46,15 | 47,65 |
| CU020BR Forro de Gesso Acartonado (Drywall) 10 Mm | m2 | 96110 | forro drywall con estructura; SINAPI placa ST 12,5 mm vs ArqOn 10 mm; alternativa 96114 (comercial) | 160,40 | 80,47 |
| IE004BR Luminária Tipo Calha 2X20W LED | Pza | 100910 | Luminária calha de sobrepor 2 lámparas LED tubulares 18 W (~2x20 W); de embutir 100916; sin precio SP | 166,52 | — |
| IE006BR Fornecimento e Instalação de Fio de Cobre 10 mm² (AWG 8) | m | 91932 | Cabo cobre flexível 10 mm² 450/750 V circuitos terminais (ArqOn «fio» rígido) | 14,11 | 21,21 |
| IE007BR Fornecimento e Instalação de Fio de Cobre 6 mm² (AWG 10) | m | 91930 | Cabo cobre flexível 6 mm² 450/750 V | 8,26 | 11,97 |
| IE008BR Fornecimento e Instalação de Fio de Cobre 4 mm² (AWG 12) | m | 91928 | Cabo cobre flexível 4 mm² 450/750 V (ArqOn dice AWG 12 ~ 3,3 mm²) | 6,41 | 8,61 |
| IE010BR Fornecimento e Instalação de Eletroduto Flexível Corrugado 20 Mm | m | 91852 | Eletroduto flexível corrugado PVC DN 20 en pared; en losa 91843 (reforzado), en forro 91831 | 15,70 | 11,51 |
| IE011BR Fornecimento e Instalação de Eletroduto Flexível Corrugado 32 Mm | m | 91856 | Eletroduto flexível corrugado PVC DN 32 en pared | 12,25 | 15,22 |
| IE012BR Fornecimento e Instalação de Aparelho de Ar-Condicionado (9.000 Btu) | Pza | 103244 | Split inverter hi-wall 9000 BTU/h ciclo frío (incluye instalación); ArqOn no dice inverter | 3188,53 | 2269,51 |
| IE022BR Transformador 150 KVA | Glb | 102106 | Transformador 150 kVA trifásico en poste, clase 15 kV (ArqOn 10,5 kV, norma boliviana); suporte 102109/102110 aparte | 52515,38 | 25339,52 |
| IE026BR Luminária Painel LED 24 de Sobrepor | Pza | 103785 | Plafon cuadrado de sobrepor LED 24 W; sin precio SP (0) | 90,09 | — |
| IS005BR Lavatório (Louça) | Pza | 86940 | Lavatório louça com coluna padrão médio, incl. sifão, válvula, engate e misturador. Alternativa popular com torneira: 86939. | 869,42 | 1167,14 |
| IS011BR Fornecimento e Instalação de Acessórios de Banheiro | Pza | 95546 | Kit de acessórios para banheiro metal cromado 5 peças, incl. fixação. | 214,68 | 234,64 |
| IS013BR Mictório (Louça) | Pza | 100858 | Mictório sifonado louça com válvula de descarga, padrão médio. | 452,18 | 856,37 |
| IS015BR Fornecimento e Instalação de Registro 1/2″ | Pza | 89352 | Registro de gaveta bruto latão roscável 1/2; luva roscável ArqOn desprezível. Com acabamento cromado: 89986. | 91,11 | 31,26 |
| IS016BR Fornecimento e Instalação de Registro 3/4″ | Pza | 89353 | Registro de gaveta bruto latão roscável 3/4. Com acabamento cromado: 89987. | 78,14 | 35,43 |
| IS028BR Caixa Sifonada de PVC 6″ X 30 Cm | Pza | 89708 | Caixa sifonada PVC 150x185x75 em ramal de esgoto; altura ArqOn 30 cm ≈ com prolongamento. | 112,86 | 126,17 |
| IS029BR Caixa Sifonada de PVC 100 mm com Sifão | Pza | 89707 | Caixa sifonada PVC 100x100x50 junta elástica. | 86,04 | 61,45 |
| IS033BR Caixa de Inspeção em Tijolo Maciço | Pza | 97902 | Caixa enterrada de tijolo maciço p/ esgoto 0,6x0,6x0,6 (ArqOn não fixa medida: 0,4=97901, 0,8=97903); inclui tampa de concreto. | 972,13 | 655,96 |
| IS034BR Caixa de Gordura de Polietileno 25x35x35 Cm | Pza | 98110 | Caixa de gordura pequena plástica (PVC Ø0,3, 19 L) com assentamento em areia; ArqOn PE 25x35x35 cm. | 150,52 | 461,79 |
| IS052BR Locação e Marcação de Tubulações | m | 99063 | Locação de rede de água ou esgoto (gabarito de madeira); ArqOn usa estação total — mesmo serviço. | 5,38 | 11,70 |
| IS053BR Fornecimento e Assentamento de Tubulação de PVC Classe 9 (3″) com Junta | m | 106107 | Tubo PVC PBA JEI DN75 fornecimento+assentamento (classe 15; 'classe 9' não existe no Brasil). | 43,47 | 49,59 |
| IS054BR Fornecimento e Assentamento de Tubulação de PVC Classe 9 (4″) com Junta | m | 106109 | Tubo PVC PBA JEI DN100; idem nota de classe. | 60,98 | 80,87 |
| IS055BR Fornecimento e Assentamento de Tubulação de PVC E-40 (2″) com Junta | m | 106105 | Tubo PVC PBA JEI DN50 (E-40 2 com junta ≈ PBA). | 35,85 | 26,53 |
| IS056BR Fornecimento e Assentamento de Tubulação de PVC E-40 (3″) com Junta | m | 106107 | Tubo PVC PBA JEI DN75. | 68,78 | 49,59 |
| IS057BR Fornecimento e Assentamento de Tubulação de PVC E-40 (4″) com Junta | m | 106109 | Tubo PVC PBA JEI DN100. | 83,89 | 80,87 |
| IS058BR Fornecimento e Instalação de Tubulação de PEAD de 20 Mm (1/2″) SDR9 PN20 | m | 104060 | Tubo PEAD PE-80 DE20 para ligação predial (junta mecânica/compressão como ArqOn). Alternativa rede: 103372. | 4,01 | 10,21 |
| IS060BR Fornecimento e Instalação de Tubulação de PEAD de 32 Mm (1″) Sdr 13.6 PN12.5 | m | 104061 | Tubo PEAD PE-80 DE32 para ligação predial. | 6,39 | 18,04 |
| IS063BR Fornecimento e Instalação de Tubulação de PEAD de 63 Mm (2″) SDR21 PN6 | m | 103374 | Tubo PEAD liso DE63 rede de água (não inclui execução de solda; ArqOn usa luva de compressão). Sem preço SP em 08/2026. | 15,85 | — |
| IS065BR Fornecimento e Instalação de Tubulação de PEAD de 90 Mm (3″) | m | 103375 | Tubo PEAD liso DE90; sem preço SP em 08/2026. | 33,37 | — |
| IS066BR Fornecimento e Instalação de Tubulação de PEAD de 110 Mm (4″) | m | 103376 | Tubo PEAD liso DE110 SDR11. | 54,08 | 133,92 |
| IS074BR Escavação de Vala com Retroescavadeira | m3 | 90106 | Escavação mecanizada de vala com retroescavadeira, prof. até 1,5 m, larg. 0,8-1,5 m, solo 1ª cat. Escolher variante por prof./largura/solo (90105, 90108...). | 30,89 | 9,76 |
| IS077BR Fornecimento e Assentamento de Tubo de Concreto D/12″ | m | 95567 | Tubo de concreto simples DN300 junta rígida argamassada (rede pluvial). Para esgoto JE: 92833. | 166,10 | 104,58 |
| IS078BR Fornecimento e Assentamento de Tubo de Concreto D/16″ | m | 95568 | Tubo de concreto simples DN400 junta rígida. Esgoto JE: 92835. | 244,95 | 129,91 |
| IS081BR Fornecimento e Assentamento de Tubulação de Esgoto em PVC Sdr 4″ | m | 90694 | Tubo PVC rede coletora parede maciça DN100 JE (NBR 7362 ≈ SDR); ArqOn colado. | 51,43 | 60,74 |
| IS082BR Fornecimento e Assentamento de Tubulação de Esgoto em PVC Sdr 6″ | m | 90695 | Tubo PVC rede coletora DN150 JE (SDR 35). | 92,12 | 115,39 |
| IS083BR Reaterro e Compactação de Vala com Compactador | m3 | 93382 | Reaterro manual de vala com compactador de percussão (sapo). | 71,64 | 34,92 |
| IS088BR Vaso Sanitário (Louça) | Pza | 86931 | Bacia com caixa acoplada louça branca + engate flexível; SINAPI não inclui assento (ArqOn 'com acessórios'). | 499,35 | 600,49 |
| MP002BR Alvenaria de Bloco de Concreto 3 Furos E=15 Cm | m2 | 103318 | Bloco de concreto 14x19x39 (nominal 15x20x40, 12,9 un/m2); SINAPI incluye tela y pinos de amarração | 152,96 | 114,18 |
| MP003BR Alvenaria de Bloco de Vidro 20x20 Cm | m2 | 101164 | Bloco de vidro 19x19 (modular 20x20); alt. 101163 (veneziana 6x20x20) | 558,38 | 689,62 |
| OG001BR Contrapiso de Concreto Magro | m3 | 96620 | lastro concreto magro en pisos; ArqOn trae 20 kg cemento/m3 (probable error, SINAPI ~250 kg) | 496,29 | 772,60 |
| OG005BR Alvenaria de Pedra Bruta | m3 | 103800 | pedra argamassada 1:3; ArqOn trae además madera/clavos (escantillón) | 641,33 | 600,57 |
| OG013BR Aço para Armadura | Kg | 92762 | armación genérica CA-50; usar 92759-92766 por diámetro, 92771 (losas) o 104919 (fundaciones) | 12,01 | 9,97 |
| OG018BR Escada de Concreto Armado | m3 | 102073 | escalera 1 lance losa plana fck25 con fôrma y armação incluidas; SINAPI 66 kg/m3 vs ArqOn 110 kg; otras geometrías 102074-102076 | 3025,12 | 3877,63 |
| OG021BR Laje Pré-moldada com Vigota Protendida | m2 | 106058 | laje vigota protendida EPS LT=20 (16+4); SINAPI capa usinada bomba, ArqOn concreto en obra; vãos ≤3 m: 106054 | 257,09 | 197,97 |
| OG022BR Laje H=20 com Vigota, Concreto Usinado H-25 | m2 | 106058 | laje vigota protendida EPS LT=20 con capa C25 usinada; vãos ≤3 m: 106054 | 247,47 | 197,97 |
| OG023BR Laje H=20 com Vigota, Concreto Usinado H-21 | m2 | 106058 | igual a OG022BR con H-21 (SINAPI C25); vãos ≤3 m: 106054 | 243,00 | 197,97 |
| OG024BR Laje H=20 com Vigota, Concreto Usinado H-21 com Bomba Adicional | m2 | 106058 | SINAPI ya considera concretagem con bomba (103674); vãos ≤3 m: 106054 | 252,38 | 197,97 |
| OG049BR Calçamento de Pista em Pedra | m2 | 101170 | pavimento de piedra poliédrica rejunte pó de pedra; ArqOn 0,153 m3 piedra vs 0,119 | 65,47 | 49,19 |
| OG050BR Pavimentação de Pista com Bloquete Sextavado | m2 | 92395 | piso intertravado sextavado e=10 cm | 188,41 | 167,73 |
| OG051BR Pavimentação de Pista com Bloquete Ondulado | m2 | 92406 | bloque ondulado = 16 faces 22x11 e=10 cm | 175,16 | 195,73 |
| OG055BR Remoção e Recomposição de Calçamento de Pedra | m2 | 101853 | reassentamento de pedras poliédricas con retirada y colocación | 48,29 | 63,89 |
| OG056BR Gabião Tipo Colchão (Colchão Reno) 4x2x0.30 M | m3 | 92757 ×3.333 | colchão reno 30 cm por m2 -> m3: 1/0,30 = 3,333 m2/m3 | 642,14 | 1145,65 |
| OG058BR Muro de Arrimo em Gabião | m3 | 92743 | muro de gabión caja 2 m, h≤4 m | 465,81 | 700,42 |
| OG061BR Escavação Comum | m3 | 93358 | excavación común manual; si es mecanizada usar escavação mecanizada (p.ej. 101114 según equipo) | 117,39 | 120,57 |
| OG064BR Aço Estrutural p/ Concreto Simples Tipo A (Encontros) | Kg | 92919 | armação estruturas diversas CA-50 (usar diámetro real) | 13,15 | 11,26 |
| OG065BR Aço Estrutural p/ Concreto Simples Tipo A (Laje) | Kg | 92771 | armação de laje CA-50 (usar diámetro real) | 13,05 | 9,40 |
| OG075BR Contrapiso de Cimento sem Pedra E=7cm - Calçadas | m2 | 94990 ×0.07 | e=7 cm en el nombre (m3->m2 exacto); ArqOn 180 kg cemento/m3 | 38,13 | 56,75 |
| OG082BR Concreto Simples para Sarjetas R=210 kg/cm² B=0.30m | m | 94287 | sarjeta 30x10 moldada in loco; SINAPI usinado C20, ArqOn betoneira | 37,26 | 35,89 |
| OG083BR Verga de Concreto Armado | m | 93187 | verga moldada in loco 20 cm; ArqOn ≈0,06 m3/m y 5 kg acero vs SINAPI 0,043 m3 y 0,8 kg: revisar sección | 315,19 | 84,99 |
| UH002BR Escavação de Valas | m3 | 93358 | escavação manual de vala; para fundaciones usar 96527/96523 | 89,95 | 120,57 |
| UH003BR Camada de Concreto Magro | m3 | 96616 | lastro de concreto magro en sapatas/blocos; alternativa m2 96619 (5 cm) | 466,79 | 851,08 |
| UH004BR Fundação Corrida (Alicerce) | m3 | 102487 | concreto ciclópico fck15; SINAPI 30 % piedra, ArqOn ~50 % | 534,20 | 645,31 |
| UH021BR Escada de Concreto Armado por Degraus | m3 | 102077 | escalera 1 lance losa cascata (por degraus) fck25, todo incluido; acero ArqOn 110 kg vs SINAPI | 3025,12 | 5318,38 |
| OT003BR Escavação Manual | m3 | 93358 | Escavação manual de vala AF_09/2024 (sólo servente 3,96 h/m3); ArqOn pedreiro+servente 4,16 h | 133,45 | 120,57 |
| OT004BR Reaterro e Compactação | m3 | 93382 | Reaterro manual de valas con compactador de percusión; ArqOn sin equipo (apisonado manual); alternativa 104737 placa vibratoria | 55,63 | 34,92 |
| OT005BR Limpeza do Terreno | m2 | 98524 | Limpeza manual de vegetação com enxada; si es mecanizada usar 98525 | 2,82 | 6,49 |
| OT007BR Remoção de Calçamento de Pedra | m2 | 97635 | Remoção de piso de bloco intertravado ou pedra portuguesa, manual, con reaprovechamiento | 9,79 | 23,25 |
| OT010BR Limpeza e Capina do Terreno | m2 | 98524 | Limpeza manual de vegetação com enxada (capina) | 2,41 | 6,49 |
| OT011BR Retirada de Reboco Interno | m2 | 97631 | Demolição de argamassas manual (retiro de revoque) | 25,23 | 15,84 |
| OT014BR Retirada de Forro (Gesso sob Laje) | m2 | 97641 | Remoção de forro de gesso manual | 16,07 | 4,06 |
| OT016BR Escavação 0-1.5 M em Terreno Mole | m3 | 93358 | Escavação manual de vala (1ª categoria / suelo blando) | 98,52 | 120,57 |
| OT017BR Escavação 0-1.5 M em Terreno Semiduro | m3 | 93358 | Escavação manual de vala; SINAPI no separa semiduro (ArqOn +8 % MO) | 104,98 | 120,57 |
| OT021BR Escavação em Rocha | m3 | 102358 | Desmonte de 3ª categoria con emulsión explosiva, exclusive carga y transporte; sin precio SP (0) | 170,05 | — |
| OT022BR Movimentação de Terra com Trator de Esteiras | m3 | 101116 | Escavação horizontal 1ª cat. con trator de esteiras 170 HP (ArqOn D7G ~200 HP); con carga usar 101126 | 11,25 | 2,60 |
| OT025BR Reaterro e Compactação Mecanizada com Material Comum | m3 | 94319 | Aterro manual con solo argilo-arenoso de jazida + compactador de percusión (ArqOn terra comum 1,13 m3); sin transporte del material | 108,44 | 91,87 |
| OT026BR Reaterro e Compactação com Solo Selecionado | m3 | 94319 | Aterro con material importado (solo selecionado ~ argilo-arenoso); alternativa 94342 con areia | 351,24 | 91,87 |
| OT033BR Alambrado com Tela e Tubo de Ferro Galvanizado 2″ C/2.5 M | m2 | 102363 | Alambrado con tubos galvanizados 2" + tela 12 BWG malla 5x5 (ArqOn 7x7); sin mureta | 189,19 | 171,25 |
| OT046BR Demolição de Pilares, Vigas e Lajes de Concreto Armado | m3 | 97627 | Demolição de pilares e vigas CA mecanizada con martelete (ArqOn perfuratriz+compressor); para losas usar 97629; sin carga/transporte | 248,78 | 250,71 |
| OT049BR Demolição de Concreto Simples | m3 | 104789 | Demolição de concreto simples manual (SINAPI la titula «piso»); ArqOn 11,95 h servente/m3 | 364,35 | 279,34 |

## PARCIAL

| Ítem | Unidad | Composición(es) SINAPI | Adaptación / nota | Hoy SP | Composición SP |
|---|---|---|---|---:|---:|
| AC011BR Revestimento com Azulejo Colorido Nacional 22x34 Cm | m2 | 87269 + 87535*1;87879*1 | ArqOn asienta azulejo con argamassa cimento-areia; SINAPI con colante AC I — ArqOn incluye mortero de base (~0,05 m3 areia): sumar chapisco + emboço 17,5 mm; azulejo 22x34 ≈ 25x35 | 192,48 | 108,21 |
| AC012BR Revestimento com Azulejo Importado 20x30 Cm | m2 | 87269 + 87535*1;87879*1 | Azulejo 20x30 asentado con argamassa cimento-areia en vez de colante — Igual que AC011: chapisco + emboço incluidos en ArqOn; alt. 87265 (20x20) | 197,06 | 108,21 |
| AC016BR Reboco Externo de Cal e Cimento | m2 | 87775 + 87905*1 | Revoque externo = chapisco fachada + emboço/massa única 1:2:8 25 mm (con vãos); ArqOn ~0,049 m3 areia ≈ 25 mm | 201,70 | 75,22 |
| AC021BR Lastro de Pedra e Contrapiso de Concreto | m2 | 96620 ×0.07 + 105742*0.15 | Lastro de pedra de mão 15 cm (base de rachão 105742, m3) + contrapiso de concreto magro e≈7 cm (96620, m3); alt. 95241 (concreto magro 5 cm, m2) | 123,93 | 70,70 |
| AC022BR Piso Cerâmico | m2 | 87248 + 87630*1 | ArqOn asienta sobre argamassa cimento-areia en vez de colante AC I — Mortero ArqOn (~0,05 m3 areia) = regularización + asiento: sumar contrapiso 3 cm; cerámica 35x35 >10 m² | 205,34 | 93,57 |
| AC024BR Piso Cerâmico Importado | m2 | 87248 + 87630*1 | ArqOn asienta sobre argamassa cimento-areia — Igual que AC022 | 232,18 | 93,57 |
| AC027BR Piso de Mármore Travertino Nacional | m2 | 98672 + 87630*1 | Cambiar mármol blanco por travertino nacional; ArqOn asienta con argamassa cimento-areia — Piso de mármol interno (colante AC III + rejunte) + contrapiso por el mortero de base | 458,86 | 764,50 |
| AC028BR Piso de Ladrilho Hidráulico Marmorizado | m2 | 101726 + 87630*1 | Ladrillo marmorizado 40x40 en vez de hidráulico 20x20 — Ladrilho hidráulico interno 5-15 m² (incluye resina) + contrapiso por el mortero ArqOn | 249,58 | 299,01 |
| AC036BR Piso de Parquete de Ipê | m2 | 101751 + 102499*1 | Cola PVA en vez de PU; agregar selador — Taco de madera 7x21 (_PS) + enceramento; ArqOn incluye selador y cera | 163,42 | 424,50 |
| AC055BR Envernizamento de Madeira | m2 | 102214 + 102193*1 | Agregar selador para madera (102195 sin costo SP) — Verniz alquídico interno 2 demãos + lixamento | 45,03 | 27,58 |
| AC056BR Raspagem e Lustração de Piso de Madeira | m2 | 102193 + 102499*1 | Agregar óleo de linhaça — Raspagem ≈ lixamento de madeira + enceramento de piso; SINAPI sin raspagem mecánica (sinteco) | 41,47 | 6,94 |
| AC067BR Pintura Externa Super Látex | m2 | 95626 + 88415*1 | Látex externa 2 demãos + fundo selador; receta ArqOn con 0,037 L de tinta/m2 (10x menor de lo normal): revisar | 23,41 | 24,28 |
| UA001BR Reboco de Cimento | m2 | 104958 + 87879*1 | ArqOn usa argamassa cimento-areia sin cal; SINAPI massa única 1:2:8 — Revoque = chapisco (87879) + massa única e=10 mm (consumo ArqOn ~0,015 m3 ≈ 1 cm); interno, área >10 m²; alt. 87529 (5-10 m², 17,5 mm) | 43,15 | 31,73 |
| CR004BR Porta de Madeira Tipo Almofadada 0.80x2.10 M | Pza | 100693 + 102214*3.8 | Kit porta mexicana (almofadada) maciça 80x210 con fechadura y batente + barniz interno 2 manos (~3,8 m2) | 1467,13 | 2314,85 |
| CR007BR Porta Interna Moldurada 0.90 X 2.10 M | Pza | 90844 + 102214*4.2 | Kit porta p/ pintura semi-oca leve 90x210 con fechadura y batente + acabado (ArqOn barniz) | 1203,15 | 1563,32 |
| CR019BR Guarda-corpo Tipo P-3 | m | 94964 ×0.09 + 103670*0.09;96533*1.4;92762*29.3 | Parapeto CA tipo P-3: concreto fck20 betoneira (~0,09 m3/m) + lanzamiento + fôrma madera 2 usos (~1,4 m2/m) + armação CA-50 29,3 kg/m; P-3 es tipología boliviana | 897,85 | 514,89 |
| CU002BR Cobertura com Telha de Aço Galvanizado N° 28 | m2 | 94213 + 92543*1 | telha ondulada zincada N°28 (~0,4 mm) en lugar de trapezoidal 0,5 mm (insumo 7243) — ArqOn incluye madera de apoyo: sumar trama 92543; mismo servicio que UC001BR | 233,01 | 106,87 |
| CU003BR Cobertura com Telha de Aço Galvanizado N° 33 | m2 | 94213 + 92543*1 | telha ondulada zincada N°33 (~0,2 mm) en lugar de trapezoidal 0,5 mm — ArqOn incluye madera: sumar 92543; chapa N°33 muy fina, no usual en BR | 203,83 | 106,87 |
| CU004BR Cobertura com Telha Ondulada de Policarbonato | m2 | 94207 + 92543*1 | cambiar telha fibrocimento 6 mm (insumo 7194) por telha ondulada de policarbonato; tornillos tirefond — sumar trama de madera 92543; 94449 (fibra de vidro) usa el mismo insumo de fibrocimento en SINAPI | 256,37 | 80,38 |
| CU005BR Cobertura com Telha Plástica de PVC | m2 | 107142 + 92543*1 | telha PVC colonial; sumar trama 92543; 107142 SIN costo SP en 08/2026 (sp=0) | 227,09 | — |
| CU009BR Cobertura com Placa Ondulada de Fibrocimento | m2 | 94207 + 92543*1 | telha ondulada fibrocimento 6 mm; ArqOn incluye madera: sumar trama 92543 (terças) | 247,10 | 80,38 |
| CU011BR Cobertura com Telha Cerâmica Colonial | m2 | 94201 + 92539*1 | telha colonial capa-canal; sumar trama madeira ripas+caibros+terças 92539; ArqOn incluye lona polietileno (subcobertura) que SINAPI no trae | 376,84 | 228,29 |
| CU023BR Cobertura de Policarbonato (6 Mm) | m2 | 107143 + 92580*1;107144*1 | policarbonato 6 mm; sumar trama de aço (terças) 92580 y perfil U 107144; 107143/107144 SIN costo SP (sp=0); ArqOn policarbonato 'bronze' | 328,50 | — |
| UC001BR Cobertura com Telha de Aço Galvanizado N°28 | m2 | 94213 + 92543*1 | telha ondulada zincada N°28 (~0,4 mm) en lugar de trapezoidal 0,5 mm (insumo 7243) — ArqOn incluye la trama de madera (terças): sumar 92543; duplicado de CU002BR | 84,38 | 106,87 |
| IE001BR Ponto de Luz | pto | 91953 + 91926*11.74;91940*1.02 | Punto de luz = interruptor simple c/placa + cable + caja; SINAPI 2026 no tiene «ponto» agregado. 12 AWG (3,3 mm²) llevado a 2,5 mm² (práctica NBR 5410); ArqOn no incluye electroducto ni caja de techo | 172,93 | 129,93 |
| IE002BR Ponto de Tomada | pto | 92008 + 91926*9.76;91941*1.03 | Punto de tomada doble = tomada baja 2 módulos 2P+T 10A c/placa + cable 2,5 + caja 4x2 baja; sin electroducto (igual que ArqOn) | 141,13 | 132,16 |
| IE003BR Quadro de Distribuição | Pza | 101876 + 91928*5.86 | Quadro PVC de embutir 6 disjuntores (sin disjuntores, igual que ArqOn) + cable; 12 AWG llevado a 4 mm²; disjuntores 93657/93664 aparte si se requieren | 349,93 | 174,27 |
| IE009BR Fornecimento e Instalação de Campainha | pto | 91987 + 91985*1;91940*0.98;91852*24.39;98280*24.4 | Campainha cigarra c/placa + pulsador + caja + electroducto 20 mm (por PVC 5/8") + cable telefónico 1 par (por UD 2x22) | 322,91 | 626,76 |
| IE013BR Fornecimento e Instalação de Iluminação Incandescente 100W | pto | 91953 + 91926*13.59;91852*6.8;91940*1.03;91936*0.98 | Punto de luz completo; soquete + lámpara incandescente 100 W sin composición SINAPI (insumos sueltos; incandescente obsoleta en BR) | 301,24 | 240,45 |
| IE014BR Fornecimento e Instalação de Iluminação LED 14W | Pza | 91953 + 91926*13.69;91852*6.86;91940*0.98;91936*0.97 | Unidad Pza pero es punto completo; soquete + lámpara LED 14 W como insumo (o 103782 plafon LED 12/13 W) | 291,10 | 240,25 |
| IE015BR Fornecimento e Instalação de Ponto de Internet | pto | 98307 + 91854*14.39;91940*0.98 | Tomada RJ45 + electroducto 25 mm + caja; cable UTP sin composición SINAPI 2026 (insumo suelto, ~13,6 m) | 268,99 | 268,22 |
| IE016BR Fornecimento e Instalação de Ponto de TV | pto | 98300 ×14.69 + 91852*14.65;91940*0.98 | Cable coaxial RG6 + electroducto + caja; placa TV con splitter sin composición (insumo) | 286,68 | 321,17 |
| IE018BR Ponto de Ar-Condicionado | pto | 91928 ×22.63 + 91854*10.69;91941*0.98;93664*1.02 | Circuito AC: cable 4 mm² + electroducto 25 mm + caja + disjuntor bipolar 32 A (ArqOn 2x30 A) | 283,81 | 408,72 |
| IE019BR Ponto de Telefone | pto | 98308 + 98280*13.67;91852*6.79;91940*1.03;91936*0.98 | Tomada RJ11 + cable CCI 1 par + electroducto 20 + cajas | 268,27 | 300,37 |
| IE020BR Ponto para Chuveiro Elétrico | pto | 91930 ×3.91 + 91854*1.94;91939*1.02;93665*0.98 | Circuito ducha: cable 6 mm² + electroducto 25 + caja 4x2 alta + disjuntor bipolar 40 A; ArqOn sólo 3,9 m de cable (bajo) | 239,62 | 185,16 |
| IE023BR Luminária de Parque LED 80W Classe II + Poste Metálico Galvanizado H=5m + Base de Concreto Armado Enterrada | pto | 101656 + 105960*1;91931*35.0;91927*20.53;97667*18.51 | Luminaria LED pública 68-97 W + poste aço cônico h=5 m (sin precio SP) + cables + PEAD enterrado; la base de CA enterrada no tiene composición (armar con concreto/armação) | 4628,20 | — |
| IE024BR Haste de Aterramento | pto | 96985 + 91932*9.74;91854*5.12 | Haste 5/8" 3 m (ArqOn haste de cobre 0,80 m) + cable 10 mm² + electroducto flex 25 (por manguera PE 3/4"); caja de inspección 98111 opcional | 393,92 | 356,71 |
| IS001BR Ponto de Água Fria | pto | 89355 ×5.86 + 89358*1;89393*0.5 | Ponto = 5,86 m tubo PVC 20 mm em sub-ramal + conexões; SINAPI não tem composição 'ponto', somar tubo por m e joelho/tê por UN. Sem rasgo/chumbamento. | 185,59 | 185,66 |
| IS002BR Ponto de Esgoto | pto | 89714 ×3.91 + 89744*1 | Ponto de esgoto = 3,9 m tubo PVC esgoto DN100 em ramal + joelho 90 DN100; conexões globais ArqOn → peças SINAPI. Alternativa DN50 (89712) para lavatório/pia. | 240,49 | 238,64 |
| IS006BR Pia de Cozinha 1 Cuba 1 Escorredor | Pza | 106772 + 86908*1 | Pia de aço inox 0,55x1,20 com 1 cuba (≈ 1 cuba + escorredor) + misturador de mesa para pia; sifão/válvula não explícitos. | 618,90 | 819,56 |
| IS014BR Ramal de Entrada de Água Potável | Pza | 95657 + 95675*1 | Ramal de entrada = kit cavalete PPR 3/4 p/ 1 medidor (tubos, registro) + hidrômetro 3/4 5 m3/h. Ligação à rede pública (colar de tomada, PEAD) não incluída. | 665,73 | 561,34 |
| IS017BR Fornecimento e Instalação de Registro 1″ de Controle de Entrada | Pza | 94495 + 92906*1 | Registro de gaveta 1 + união galvanizada 1 (composição de gás, mesma peça); niple e fita desprezíveis. | 157,33 | 122,24 |
| IS020BR Fornecimento e Instalação de Tubulação de Ferro Galvanizado 2″ | m | 92341 + 92676*0.82 | Tubo galvanizado 2 rosqueado em prumadas; conexões separadas (joelho 2 92676, comp. de sprinkler). Alternativa reservação: 94462. | 150,92 | 192,43 |
| IS021BR Fornecimento e Instalação de Tubulação Hidráulica de PVC Soldável 1/2″ | m | 89355 + 89358*0.51 | Tubo PVC soldável 20 mm em ramal/sub-ramal; conexões à parte. ATENÇÃO: receita ArqOn usa tubo PPR e conexões galvanizadas (incoerente com o nome); se for PPR usar 104194. | 37,10 | 34,10 |
| IS022BR Fornecimento e Instalação de Tubulação Hidráulica de PVC Soldável 3/4″ | m | 89356 | Tubo PVC soldável 25 mm em ramal/sub-ramal; conexões à parte. Receita ArqOn usa PPR 3/4 (alternativa 96635). | 43,75 | 32,92 |
| IS036BR Bomba d'Água de 1.5 Hp | Pza | 102116 + 99620*1;89353*1;92906*1;92905*1;102137*1 | Bomba centrífuga 1,5 CV (trifásica; ArqOn hidropneumática) + válvula de retenção 1 + registro 3/4 + uniões + chave-boia. Niples/buchas desprezados. | 4134,48 | 2108,34 |
| IS038BR Reservatório Inferior (Cisterna) com Bomba d'Água - Instalação | Pza | 102116 + 103011*1;102137*1;94495*2;99620*2;92906*2;89357*9.8 | Conjunto de recalque: bomba 1,5 CV + válvula de pé com crivo 1 + chave-boia + 2 registros + 2 retenções + 2 uniões + 9,8 m tubo (PVC 32 mm como proxy do roscável 1). Joelhos/tês roscáveis e caixa de disjuntor sem composição. | 5234,70 | 2977,41 |
| IS039BR Reservatório Elevado de Água - Instalação | Pza | 94495 ×2 + 99620*2;92906*2;94797*1;89357*4.9 | Instalação do reservatório elevado: 2 registros 1 + 2 retenções + 2 uniões + torneira de boia 1 + 4,9 m tubo 32 mm (proxy roscável 1). Conexões roscáveis sem composição. | 1112,29 | 1055,78 |
| IS068BR Fornecimento e Termofusão de Tubulação de PEAD de 160 Mm (6″) SDR26 PN6 | m | 103377 + 103443*1 | Tubo PEAD liso DE160 + execução de junta por termofusão (coef. ArqOn ≈1/m; real ≈0,1-0,17/m). | 107,21 | — |
| IS069BR Fornecimento e Termofusão de Tubulação de PEAD de 200 Mm (8″) SDR26 PN6 | m | 103379 + 103445*1 | Tubo PEAD DE200 + junta termofusão 200. | 147,96 | — |
| IS070BR Fornecimento e Termofusão de Tubulação de PEAD de 250 Mm (10″) SDR26 PN6 | m | 103381 + 103447*1 | Tubo PEAD DE250 + junta termofusão 250; 103381 sem preço SP. | 213,63 | — |
| IS087BR Chuveiro | Pza | 89354 + 92687*5.13;92699*2.92 | Misturador de chuveiro SINAPI; somar tubo galvanizado 1/2 (comp. de gás, mesmo tubo) e joelhos. Base/receptáculo 0,80x0,80 sem composição SINAPI (manter insumo próprio). | 1304,45 | 781,57 |
| OG003BR Laje de Fundação (Radier) de Concreto Armado | m3 | 97096 + 97086*3;107281*100 | sustituir insumo concreto usinado por concreto feito em obra 94965 (fck25 betoneira) — radier: concretagem + fôrma borde 97086 (~3 m2/m3 est.) + armação 107281 (100 kg) | 2306,06 | 2047,18 |
| OG004BR Radier com Concreto Usinado H-21 | m3 | 97096 + 97086*1.5;107281*50 | concreto C30 usinado en lugar de H-21 — radier usinado: + fôrma 97086 (~1,5 m2/m3 est.) + armação 107281 (50 kg); alternativa m2 97101/97102 | 1283,09 | 1345,03 |
| OG006BR Muro de Arrimo de Concreto Ciclópico | m3 | 102487 + 92411*2.4 | muro de arrimo ciclópico: + fôrma 92411 (~2,4 m2/m3 est.); receta ArqOn (0,8 m3 piedra, 100 kg) se parece más a 103800 pedra argamassada | 857,91 | 1071,48 |
| OG007BR Muro de Concreto Armado E=25 Cm | m3 | 103685 + 92411*8;92919*60 | sustituir insumo concreto usinado por concreto feito em obra 94965 (fck25 betoneira) — muro e=25 cm: concretagem muretas + fôrma 2 caras (8 m2/m3) + armação 92919 (60 kg); alternativa cortina 100349/100341/100344 | 2864,33 | 2751,19 |
| OG012BR Ábaco em Lajes com Concreto Usinado H-21 | m3 | 103675 + 92484*1.45;92771*58.8 | concreto C25 en lugar de H-21 — ábaco con usinado bombeado: + fôrma laje 92484 (~1,45 m2/m3 est.) + armação 92771; Sikadur 32 no está en SINAPI | 2639,99 | 1610,91 |
| OG015BR Pilar de Concreto Usinado H-21 | m3 | 103669 + 92411*12;92762*125 | concreto usinado C20/H-21 en lugar de C25 (insumo 38408) — pilar usinado sin bomba: + fôrma + armação; aditivo acelerante ArqOn no está en SINAPI | 2567,54 | 4404,55 |
| OG016BR Pilar de Concreto Usinado H-21 com Bomba | m3 | 103672 + 92411*12;92762*125 | concreto C20/H-21 bombeado en lugar de C25 — pilar con bomba: + fôrma 92411 + armação 92762 | 2625,42 | 4026,67 |
| OG017BR Pilar de Concreto Usinado H-25 | m3 | 103669 + 92411*12;92762*125 | pilar usinado C25 = H-25: + fôrma 92411 (~12 m2/m3 est.) + armação 92762 (125 kg) | 2641,70 | 4404,55 |
| OG025BR Cinta de Amarração de Concreto Armado | m3 | 103682 + 92447*12.7;92762*90 | sustituir insumo concreto usinado por concreto feito em obra 94965 (fck25 betoneira) — concretagem vigas + fôrma 92447 (~12,7 m2/m3 est.) + armação 92762 (90 kg) | 2840,78 | 5140,52 |
| OG036BR Calçada de Concreto sobre Lastro de Pedra E=4 Cm | m2 | 94990 ×0.04 + 100322*0.15 | lastro de pedra de mão en lugar de brita n.3 — calzada e=4 cm (nombre) sobre lastro de piedra: sumar lastro ~15 cm; EPS de juntas aparte | 144,33 | 58,39 |
| OG039BR Bueiro Tubular de Concreto Armado Ø 1 M | m | 92216 + 96624*0.8 | tubo concreto DN1000 fornecimento e assentamento; sumar berço granular (~0,8 m3/m brita, ArqOn tiene 0,8 brita + 0,4 arena) | 1148,61 | 803,48 |
| OG040BR Compactação com Rolo Pé de Carneiro | m3 | 96385 | compactación rolo pé de carneiro (argiloso 15 cm); SINAPI excluye material: sumar suelo seleccionado (1,21 m3) y transporte | 445,40 | 13,62 |
| OG041BR Capa Asfáltica em CBUQ E=5 Cm | m2 | 95995 ×0.05 | CBUQ capa de rolamento e=5 cm (m3->m2 exacto); SINAPI compra CBUQ en usina y excluye carga/transporte e imprimación/pintura de ligação (104375) | 109,71 | 73,24 |
| OG062BR Concreto Simples Tipo A (Encontros) | m3 | 103685 + 92411*6 | sustituir insumo concreto usinado por concreto feito em obra 94965 (fck25 betoneira) — estribos/encontros de puente: + fôrma 92411 (~6 m2/m3 est.); acero aparte (OG064BR); aditivo no en SINAPI; ideal SICRO | 2746,06 | 1720,45 |
| OG063BR Concreto Simples Tipo A (Laje) | m3 | 103682 + 92484*5 | sustituir insumo concreto usinado por concreto feito em obra 94965 (fck25 betoneira) — losa de puente: + fôrma 92484 (1/e m2/m3, ≈5 para e=0,20); acero aparte (OG065BR); ideal SICRO | 2859,62 | 2464,36 |
| UH005BR Baldrame | m3 | 102487 + 96533*2.3 | baldrame ciclópico sin acero; sumar fôrma viga baldrame 96533 (~2,3 m2/m3, estimado de la madera ArqOn) | 760,83 | 881,59 |
| UH006BR Sapata de Concreto Armado | m3 | 96556 + 96532*3.7;104919*55 | SINAPI separa: concretagem sapata (feito em obra fck30) + fôrma 96532 (~3,7 m2/m3 estimado) + armação 104919 (55 kg) | 2342,07 | 2369,40 |
| UH007BR Pilar de Concreto Armado | m3 | 103669 + 92411*12;92762*125 | sustituir insumo concreto usinado por concreto feito em obra 94965 (fck25 betoneira) — concretagem pilares + fôrma 92411 (~12 m2/m3 estimado) + armação 92762 (125 kg; separar estribos en 92759) | 3175,05 | 4404,55 |
| UH008BR Cinta de Amarração Superior | m3 | 103682 + 92447*6.7;92762*60 | sustituir insumo concreto usinado por concreto feito em obra 94965 (fck25 betoneira) — cinta como viga: concretagem vigas 103682 + fôrma 92447 (~6,7 m2/m3 est.) + armação 60 kg; alternativa por m 93205 (canaleta) | 2315,37 | 3334,40 |
| UH025BR Laje Maciça de Concreto Armado | m2 | 103682 ×0.07 + 92484*1;92769*10 | sustituir insumo concreto usinado por concreto feito em obra 94965 (fck25 betoneira) — losa maciza por m2: e≈7 cm inferido (25 kg cemento); + fôrma 92484 + armação 92769 (10 kg/m2) | 310,21 | 476,14 |
| UH026BR Parede de Concreto Armado | m2 | 103685 ×0.09 + 92411*2;92919*8 | sustituir insumo concreto usinado por concreto feito em obra 94965 (fck25 betoneira) — muro de concreto por m2: e≈9 cm inferido; fôrma 2 caras 92411 + armação 92919 (8 kg/m2); alternativa sistema paredes de concreto 99432 | 370,70 | 504,17 |
| OT015BR Transporte de Material Excedente | m3 | 97914 + 100981*1 | Transporte basculante 6 m3 vía urbana (fator/coef por km: multiplicar por DMT y empolamiento) + carga; ArqOn carga a mano (2 h servente), SINAPI sólo carga mecanizada 100981 | 100,76 | 13,87 |
| OT019BR Escavação com Esgotamento | m3 | 93358 + 104482*0.28 | Escavação manual + esgotamento com bomba submersível (H) 0,28 h/m3 como ArqOn | 144,51 | 132,75 |
| OT020BR Escavação com Retroescavadeira | m3 | 90105 + 95875*1 | Escavação mecanizada vala retro 0,26 m3 1ª cat. + transporte (coef por km, ×DMT); para zapatas usar 96521 | 32,29 | 13,57 |
| OT027BR Retirada e Transporte de Entulho com Carga | m3 | 100981 + 97914*1 | Carga de entulho en basculante 6 m3 + transporte (coef por km, ×DMT); ArqOn carga con retro, SINAPI con escavadeira | 70,86 | 13,87 |
| OT028BR Área Verde em Jardim com Grama em Tepe | m2 | 98504 + 105521*1 | Plantio grama em placas (batatais) + espalhamento de terra vegetal; turba/estiércol como insumos | 60,16 | 23,67 |
| OT032BR Alambrado com Tela e Mourão de Concreto Protendido | m2 | 106468 + 106480*0.16 | Tela para alambrado con mourões de concreto (m2) + mourão recto 10x10 (~0,16 un/m2; ArqOn 0,39 m/m2); malla ArqOn 7x7 #12 vs SINAPI 8x8 14 BWG | 109,06 | 38,68 |
| OT038BR Limpeza e Retirada de Entulho | m3 | 100981 + 97914*1 | Carga de entulho + transporte basculante 6 m3 (coef por km, ×DMT) | 79,29 | 13,87 |

## ADAPTADA

| Ítem | Unidad | Composición(es) SINAPI | Adaptación / nota | Hoy SP | Composición SP |
|---|---|---|---|---:|---:|
| AC001BR Forro de Madeira Macho-e-Fêmea (Guanandi) | m2 | 96112 | Cambiar forro pinus 10x1 por tábua macho-fêmea de guanandi; mantener estrutura de sarrafos/caibros — Forro de madeira residencial con estructura unidirecional | 371,47 | 169,01 |
| AC004BR Pingadeira de Concreto Armado 30x10 Cm | m | 105023 | Ajustar sección a 30x10 (0,03 m3 concreto/m) y acero a 2,36 kg/m; forma de borde de laje — Verga moldada in loco (forma+armação+concreto por m) es lo más cercano; alt. peitoril pré-moldado 101967 (sin costo SP) | 165,62 | 72,03 |
| AC005BR Pingadeira de Tijolo Maciço | m | 101159 ×0.35 | Convertir m→m2 (≈0,35 m2 de face por m, 19,3 tijolos 25x12x6,5); cambiar tijolo 5x10x20 por tijolo 18 furos — Pingadeira/cornija de tijolo, sin composición propia en SINAPI | 149,36 | 55,51 |
| AC008BR Rodapé Cerâmico | m | 88648 | Escalar por altura: ArqOn consume 0,376 m2 cerámica/m (h≈33 cm) vs 0,1225 m2 en SINAPI (h=7 cm); factor ≈3,1 en material, colante y MO — Revisar receta ArqOn: si el zócalo es de 7-10 cm usar 88648 tal cual | 25,55 | 7,84 |
| AC009BR Forro de Gesso | m2 | 87412 | El nombre dice forro pero la receta es gesso aplicado (5,5 kg/m2, sin placas ni arame): usar gesso desempenado en teto 0,5 cm (9,66 kg); escalar gesso x0,57 — Si de verdad es forro de placas, usar 96109 (forro placas de gesso residencial). Revisar nombre o rec | 37,45 | 29,82 |
| AC010BR Revestimento Texturizado Externo | m2 | 88423 | ArqOn es textura de argamassa cimento-areia (salpicado); SINAPI es tinta texturizada acrílica: sustituir insumo — Receta ArqOn inconsistente (0,26 kg cimento para 0,02 m3 areia); alt. 95305 textura acrílica en pared | 31,62 | 23,71 |
| AC013BR Revestimento em Pedra Ardósia Cortada | m2 | 101732 | Pasar de piso a pared: aumentar MO (~+20 %) y usar pedra ardósia 15x30 — SINAPI sólo tiene ardósia en piso (sobre argamassa 1:3) | 194,99 | 127,79 |
| AC014BR Revestimento de Madeira Macho-e-Fêmea de Cedro | m2 | 96112 | Aplicar en pared: quitar caibros de estructura (fijación con parafuso+bucha) y cambiar forro pinus por macho-fêmea de cedro — Sin composición de lambri en SINAPI | 210,69 | 169,01 |
| AC015BR Reboco Externo com Massa Fina Pronta | m2 | 87543 | Aplicación manual en fachada; escalar consumo de 5 mm a lo de ArqOn (1,37 kg/m2 ≈ 1 mm, revisar) — SINAPI ya no tiene reboco fino separado; massa única industrializada 5 mm es lo más cercano | 130,45 | 24,97 |
| AC018BR Reboco Interno Impermeável | m2 | 98562 | Escalar argamassa 1:3 de 0,02 a ~0,04 m3/m2 (ArqOn e≈3 cm) y aditivo proporcional — Impermeabilização con argamassa+aditivo impermeabilizante e=1,5 cm | 170,39 | 58,15 |
| AC023BR Piso de Ladrilho Granilite 40x40x0.50 Cm | m2 | 101726 + 87630*1 | Cambiar ladrillo hidráulico 20x20 por ladrillo de granilite 40x40 (quitar resina) — 104162 es granilite monolítico in situ, no placas; sumar contrapiso por el mortero de base ArqOn | 209,29 | 299,01 |
| AC029BR Piso de Porcelanato | m2 | 87263 | Sustituir argamassa colante AC III por pasta de cimento (ArqOn 15,4 kg cimento, 0,01 m3 areia) — Porcelanato 60x60 >10 m²; alt. 87262 (5-10 m²) | 200,19 | 108,82 |
| AC031BR Piso Vinílico | m2 | 101727 | Placa vinílica 1,6 mm en vez de 3,2 mm — Piso vinílico semiflexível em placas 30x30 fijado con cola | 107,07 | 198,95 |
| AC032BR Piso Cimentado com Acabamento Liso (Massa Fina) | m2 | 106788 | Agregar pigmento (0,175 kg/m2) — Piso cimentado liso 1:3 e=1,5 cm | 71,94 | 33,88 |
| AC038BR Grelha de Piso em Bronze 20x20 Cm | Pza | 103001 | Cambiar grelha de ferro fundido 150x1000 por grelha de bronce 20x20 y escalar MO — Sin composición de grelha pequeña de piso | 96,09 | 195,88 |
| AC039BR Ralo Sifonado Pluvial 6″ | Pza | 89491 | Agregar grelha de bronce 6″ (SINAPI trae la de PVC) — Caixa sifonada PVC 150x185x75 en ramal pluvial | 193,69 | 119,67 |
| AC040BR Rodapé de Cimento | m | 106788 ×0.10 | Convertir m2→m con altura 10 cm — SINAPI no tiene rodapé cimentado; receta ArqOn trae 0,039 m3 areia/m (excesivo, revisar) | 37,83 | 3,39 |
| AC041BR Rodapé Cerâmico com Argamassa | m | 88648 | Sustituir placa de piso por pieza de rodapé cerâmico (1,126 m/m) y colante por argamassa cimento-areia — Rodapé cerâmico 7 cm | 40,54 | 7,84 |
| AC043BR Rodapé de Granilite | m | 101741 | Sustituir granilha+cimento branco in situ por pieza pré-moldada de granilite 25x10 asentada con argamassa — Rodapé marmorite 10 cm | 42,66 | 58,04 |
| AC044BR Rodapé de Argamassa Desempenada | m | 106788 ×0.10 | Convertir m2→m con altura 10 cm; agregar pigmento — Sin rodapé de argamassa en SINAPI; receta ArqOn con 0,041 m3 areia/m (revisar) | 39,09 | 3,39 |
| AC046BR Impermeabilização com Manta Asfáltica Sika com Alumínio | m2 | 98546 | Cambiar manta asfáltica de poliéster 4 mm PP por manta aluminizada — Manta asfáltica 1 capa con primer | 104,57 | 135,46 |
| AC047BR Impermeabilização com Membrana Geotêxtil 3.5 Mm | m2 | 98546 | Manta aluminizada 3,5 mm en vez de 4 mm y quitar primer (ArqOn no lo trae) — Manta asfáltica 1 capa | 195,26 | 135,46 |
| AC052BR Pintura Interna Látex Acetinado | m2 | 88489 | Cambiar tinta látex premium por látex acetinada — Látex acrílica premium paredes, 2 demãos | 33,59 | 14,99 |
| AC054BR Pintura a Óleo Interna | m2 | 104642 + 88485*1;88495*1 | Cambiar tinta látex por esmalte sintético brilhante + aguarrás — SINAPI no tiene esmalte en pared; ArqOn incluye selador (88485) y massa (88495) | 51,59 | 32,09 |
| AC060BR Assentamento de Vidro Impresso Tipo Catedral (3 Mm) | m2 | 102160 | Vidro impresso 3 mm en vez de 4 mm — Vidro impresso (catedral) en esquadria de madeira | 74,32 | 174,02 |
| AC068BR Revestimento Cerâmico Externo | m2 | 104588 + 87905*1;87775*1 | Pieza 11x23 (253 cm2) vs grês ≤200 cm2; ArqOn asienta con argamassa cimento-areia en vez de colante AC III — ArqOn incluye mortero de base (≈0,039 m3/m2): sumar chapisco fachada + emboço 25 mm; si se presupuestan aparte, sólo 104588 | 221,87 | 300,61 |
| CA001BR Porta | Pza | 90822 | ArqOn fabrica la hoja en obra con madera bruta (29 p2) y clavos; usar porta p/ pintura 80x210 semi-oca con bisagras — adaptado de SINAPI 90822; sin batente ni cerradura (kit 91320/90849 si se quieren); medida de la puerta no definida en ArqOn | 301,80 | 460,55 |
| CA002BR Janela | Pza | 100666 ×1.20 | convertir Pza->m2 con ventana tipo 1,00x1,20 m; ArqOn es ventana rústica de madera bruta sin vidrio — adaptado de SINAPI 100666 (pinus/eucalipto, vidrio no incluido); alternativa 100669 basculante; ajustar fator al tamaño real | 199,24 | 820,36 |
| CA003BR Guarda-corpo Metálico | m | 106213 | sustituir tubos galvanizados por varilla CA-50 soldada (~5,1 kg/m); quitar epoxi/chumbadores — adaptado de SINAPI 106213 (guarda-corpo aço galv. 0,92 m; sin precio SP); alternativa 106221 (0,65 m, con precio). Receta ArqOn (varilla+madera+carpintero) es atípic | 134,82 | — |
| CR001BR Retirada de Porta - Janela | Pza | 97644 ×1.68 | convertir Pza->m2 con puerta 0,80x2,10; para ventanas usar 97645 con su área — adaptado de SINAPI 97644/97645 (remoção manual sin reaprovechamiento) | 52,72 | 22,16 |
| CR003BR Mola Hidráulica para Porta de Banheiro | Pza | 102188 | SINAPI sólo mola hidráulica de piso p/ vidrio; cambiar insumo por mola aérea (brazo) y MO ~1 h carpintero — adaptado de SINAPI 102188; costo SINAPI muy superior al de una mola aérea | 313,84 | 1100,58 |
| CR005BR Porta de Madeira Tipo Almofadada 1.00x2.10 M | Pza | 100693 + 102213*4.6 | SINAPI máx. 80x210 en maciça/mexicana; escalar hoja a 1,00 m (+25 % material de hoja) y fechadura externa — adaptado de SINAPI 100693 + barniz exterior 102213 | 1739,78 | 2331,91 |
| CR006BR Porta Externa Moldurada 1.00x2.10 M | Pza | 90852 + 102213*4.6 | kit semi-oca pesada 90x210 sin cerradura -> hoja 1,00 m HDF moldurada + fechadura externa (insumo) — adaptado de SINAPI 90852; ArqOn barniza HDF (normalmente se pinta) | 1699,02 | 1667,18 |
| CR008BR Janela de Madeira Cedro (Marco 2x3″) | m2 | 100667 | SINAPI cedro con venezianas+guilhotina; ArqOn ventana de abrir con bisagras y ferrolho — adaptado de SINAPI 100667 (imbuia/cedro); vidrio no incluido en ambos | 447,65 | 1065,85 |
| CR010BR Porta de Abrir em Vidro Temperado 10 Mm | m2 | 102182 ×0.529 | convertir m2->UN (1 hoja 90x210 = 1,89 m2); ArqOn con perfil U y sin mola — adaptado de SINAPI 102182 (pivotante 10 mm); con mola 102184 | 876,05 | 649,45 |
| CR011BR Porta em Chapa Metálica | m2 | 100701 | SINAPI porta de ferro tipo grade com chapa; ArqOn hoja de chapa 1/16" con cantoneira soldada en obra — adaptado de SINAPI 100701; alternativa por unidad 94807/106146 | 701,23 | 657,06 |
| CR012BR Portão de Garagem em Chapa Metálica 3.0x2.4 M | m2 | 100701 | igual que puerta de chapa; portón 3,0x2,4 de 2 hojas — adaptado de SINAPI 100701; SINAPI no tiene portão de garagem em chapa | 661,19 | 657,06 |
| CR013BR Grade Metálica para Janela com Marco | m2 | 99861 | SINAPI barras chatas 25x4,8; ArqOn tubo 20x20 + marco cantoneira — adaptado de SINAPI 99861 (gradil em aço em vãos de janela) | 332,63 | 596,25 |
| CR014BR Janela de Correr em Alumínio 3 Folhas 2.40x1.20 M | m2 | 94570 | SINAPI 2 hojas p/ vidrio (vidrio incluido) 100x120; ArqOn 3 hojas 2,40x1,20 + vidrio 4 mm — adaptado de SINAPI 94570; 94573 = 4 hojas con bandeira; 94572 = 3 hojas con 2 venezianas | 616,31 | 376,17 |
| CR015BR Janela Metálica (Cantoneira 1″x1/8″) | m2 | 94559 | SINAPI basculante de aço sin vidrio; ArqOn ventana de cantoneira 1"x1/8" de abrir fabricada en obra — adaptado de SINAPI 94559 | 362,57 | 700,83 |
| CR016BR Bancada de Concreto Armado com Revestimento em Azulejo Colorido | m2 | 86889 ×1.11 | SINAPI bancada de granito 1,50x0,60 (0,90 m2); sustituir tampo de piedra por losa de CA + ladrillo + azulejo — adaptado de SINAPI 86889; alternativa armar por partes (concreto+fôrma+armação+87265 azulejo) | 531,46 | 926,17 |
| CR017BR Bancada de Concreto Armado com Revestimento em Mármore | m2 | 86893 ×1.11 | SINAPI bancada mármore branco 1,50x0,60 (0,90 m2); ArqOn losa de CA + ladrillo revestida en mármol travertino — adaptado de SINAPI 86893; SINAPI no incluye la base de concreto | 950,47 | 928,29 |
| CR020BR Protetor Metálico Tipo Folha H=0.70m | m | 106221 | SINAPI guarda-corpo galv. 0,65 m con tubos; ArqOn barras lisas CA-25 soldadas H=0,70 pintadas — adaptado de SINAPI 106221 (protetor tipo folha es tipología boliviana) | 106,55 | 217,01 |
| CU008BR Cobertura em Steel Frame com Telha Ondulada de Aço Galvanizado | m2 | 94213 + 92580*1 | telha ondulada N°28 por trapezoidal; perfiles LSF galvanizados (PCG/PGG) en lugar de trama de aço 92580 — SINAPI no tiene cubierta steel frame; adaptado de SINAPI 94213 + 92580 (trama de aço, excl. pintura) | 223,01 | 125,64 |
| CU010BR Cobertura em Steel Frame com Telha Colonial | m2 | 94201 + 92574*1 | trama de aço (ripas, caibros e terças) en lugar de perfiles LSF galvanizados — SINAPI no tiene steel frame; adaptado de SINAPI 94201 + 92574 | 279,23 | 254,37 |
| CU012BR Cobertura com Telha Cerâmica Espanhola | m2 | 94195 + 92539*1 | telha cerâmica espanhola (encaixe tipo S) en lugar de portuguesa; ~15,4 pza/m2 vs 17,7 — sumar trama 92539; lona de polietileno aparte; alternativa 94442 (romana) | 322,25 | 198,29 |
| CU013BR Cobertura com Telha Espanhola de Fibrocimento | m2 | 94207 + 92543*1 | cambiar telha ondulada 6 mm por telha espanhola colorida de fibrocimento — SINAPI no tiene telha espanhola de fibrocimento; sumar trama 92543 | 284,35 | 80,38 |
| CU014BR Cobertura Termoacústica (Telha Sanduíche) - Densidade 13 | m2 | 94216 | cambiar telha PU 30 mm (insumo 40740) por telha sanduíche EPS 50 mm — receta ArqOn trae el insumo en m (no m2): revisar unidad; sin estructura (igual que SINAPI) | 231,47 | 215,91 |
| CU016BR Cobertura Termoacústica (Telha Sanduíche) E=50 Mm - Densidade 40 | m2 | 94216 | cambiar telha PU 30 mm por PU 50 mm (insumo 40740 -> e=50) — adaptado de SINAPI 94216 | 292,80 | 215,91 |
| CU017BR Cumeeira de Chapa Lisa de Aço Galvanizado | m | 94231 | chapa N°28 corte ~58 cm en lugar de N°24 corte 25 cm (escalar chapa x2,3) — cumeeira de chapa lisa ≈ rufo; alternativa 100326 (cumeeira p/ telha trapezoidal, sin costo SP) | 66,13 | 54,54 |
| CU021BR Condutor de Chapa Lisa de Aço Galvanizado N° 28 | m | 94227 | chapa N°28 desarrollo ~43 cm (tubo) en lugar de calha N°24 desarrollo 33 cm — SINAPI no tiene condutor de chapa galvanizada; alternativa PVC 89578 (condutor DN100) | 86,99 | 73,32 |
| CU022BR Calha de Chapa de Aço Galvanizado N° 28, Corte 50 Cm | m | 94228 | chapa N°28 en lugar de N°24 (mismo corte 50 cm) — calha chapa galvanizada; ArqOn con soldadura y barra chata de soporte | 118,10 | 95,79 |
| CU024BR Cobertura de Policarbonato (8 Mm) | m2 | 107143 + 92580*1;107144*1 | chapa policarbonato 8 mm en lugar de 6 mm — sumar trama 92580 y perfil U; 107143 SIN costo SP | 337,06 | — |
| CU025BR Impermeabilização de Cobertura com Telha Colonial | m2 | 98554 | aplicar sobre telha colonial (superficie irregular, +consumo) — membrana líquida acrílica 3 demãos; alternativa 98555 (argamassa polimérica) | 40,01 | 50,92 |
| CU026BR Pintura Anticorrosiva para Cobertura | m2 | 100722 ×1.5 | zarcão por demão sobre telha metálica; ArqOn 0,166 L/m2 ≈ 1,5 demãos (SINAPI 0,11 L/demão) — incluye lija en ArqOn; SINAPI no | 31,81 | 45,30 |
| CU027BR Pintura de Cobertura Externa | m2 | 95626 | aplicar sobre cubierta en lugar de pared externa — látex acrílica 2 demãos | 32,41 | 18,58 |
| IE005BR Luminária Tipo Spot de Embutir 16W LED | Pza | 105546 | SINAPI spot embutir con lámpara PAR20 (~7 W); cambiar por LED 16 W — adaptado de SINAPI 105546; alternativa 103787 plafon embutir 18 W | 114,89 | — |
| IE025BR Luminária Externa Tipo Tartaruga 18W | Pza | 97607 | cambiar lámpara LED 6 W por 18 W — adaptado de SINAPI 97607 (arandela tartaruga de sobrepor) | 102,59 | 95,97 |
| IS003BR Caixa de Inspeção | Pza | 97902 | Adaptado de SINAPI 97902: trocar tijolo maciço por bloco cerâmico 6 furos; confirmar dimensão (0,4/0,6 m) — Caixa enterrada de alvenaria p/ esgoto; SINAPI inclui tampa de concreto e fundo. Dimensão ArqOn não informada. | 385,52 | 655,96 |
| IS004BR Tanque de Lavar em Ferro Esmaltado | Pza | 86921 | Adaptado de SINAPI 86921: trocar tanque de louça c/ coluna por tanque de ferro esmaltado; base de alvenaria (26 blocos) no lugar da coluna — SINAPI só tem tanque de louça, mármore sintético ou inox; já inclui sifão, válvula e torneira. | 652,29 | 912,80 |
| IS007BR Pia de Cozinha 2 Cubas 1 Escorredor | Pza | 106772 + 86908*1 | Adaptado de SINAPI 106772: trocar pia inox 1 cuba por pia 2 cubas 1 escorredor (≈1,50-1,80 m) — SINAPI só tem pia inox 1 cuba; somar misturador 86908. | 776,89 | 819,56 |
| IS008BR Pia de Cozinha 2 Cubas 2 Escorredores | Pza | 106772 + 86908*1 | Adaptado de SINAPI 106772: trocar por pia inox 2 cubas 2 escorredores (≈2,00 m); M.O. +20% — SINAPI só tem pia inox 1 cuba; somar misturador 86908. | 1073,71 | 819,56 |
| IS009BR Tanque de Lavar Roupa em Concreto 1 Cuba | Pza | 86921 | Adaptado de SINAPI 86921: trocar tanque de louça por tanque de concreto/cimento 1 cuba; base de alvenaria (26 blocos) — Tanque de cimento não existe no SINAPI; composição já traz sifão, válvula e torneira. | 606,16 | 912,80 |
| IS010BR Tanque de Lavar Roupa em Concreto 2 Cubas | Pza | 86921 | Adaptado de SINAPI 86921: tanque de cimento 2 cubas; duplicar sifão e torneira; base de alvenaria (51 blocos) — Tanque de cimento não existe no SINAPI; sem composição de 2 cubas. | 822,04 | 912,80 |
| IS018BR Fornecimento e Instalação de Tubulação de Ferro Galvanizado 1/2″ | m | 92687 + 92699*0.51 | Adaptado de SINAPI 92687 (tubo galv. 1/2 em ramal de GÁS): mesmo tubo classe média rosqueado, aplicar em água fria — SINAPI só tem galvanizado 1/2 em gás; conexões ArqOn (0,51/m) → joelho 92699. | 48,29 | 44,33 |
| IS019BR Fornecimento e Instalação de Tubulação de Ferro Galvanizado 3/4″ | m | 92688 + 92701*0.64 | Adaptado de SINAPI 92688 (tubo galv. 3/4 em ramal de GÁS) aplicado em água fria — Mesma observação de IS018; conexões → joelho 3/4 92701. | 54,53 | 71,46 |
| IS023BR Fornecimento e Instalação de Tubulação de PVC Roscável 1/2″ | m | 89355 | Adaptado de SINAPI 89355: trocar tubo PVC soldável 20 mm por PVC roscável 1/2 (+fita veda-rosca) — SINAPI 08/2026 não tem tubo PVC roscável por metro (só registros/luvas roscáveis). | 29,76 | 28,54 |
| IS024BR Fornecimento e Instalação de Tubulação de PVC Roscável 3/4″ | m | 89356 | Adaptado de SINAPI 89356: trocar por PVC roscável 3/4 — Idem IS023. | 39,80 | 32,92 |
| IS025BR Fornecimento e Instalação de Tubulação de PVC Roscável E-40 1″ | m | 89357 | Adaptado de SINAPI 89357: trocar por PVC roscável 1 — Idem IS023. | 52,27 | 44,80 |
| IS026BR Caixa de Inspeção de Concreto 40x40 Cm | Pza | 97896 | Adaptado de SINAPI 97896 (caixa pré-moldada 0,4x0,4x0,4): concreto moldado in loco com forma de madeira — Mesma dimensão; SINAPI usa peça pré-moldada. Alternativa alvenaria: 97901. | 276,21 | 399,49 |
| IS027BR Caixa Sifonada de Concreto | Pza | 97895 | Adaptado de SINAPI 97895 (caixa pré-moldada 0,3x0,3x0,3): incluir peça caixa sifonada de cimento — SINAPI não tem caixa sifonada de concreto; sifonadas só em PVC (89707/89708). | 171,66 | 215,37 |
| IS030BR Caixa Receptora Pluvial de PVC 8″ X 40 Cm | Pza | 89491 | Adaptado de SINAPI 89491 (caixa sifonada 150 pluvial): trocar por caixa receptora PVC 8x40 cm — Sem caixa receptora 200 mm no SINAPI. | 128,19 | 119,67 |
| IS032BR Caixa de Inspeção de Polietileno Ø 60 Cm (Sanear) | Pza | 97897 | Adaptado de SINAPI 97897 (caixa pré-moldada 0,6x0,6x0,5): trocar por caixa de inspeção de polietileno Ø60 + anel de borracha — SINAPI só tem caixa PE Ø0,3 para aterramento (98111). | 298,57 | 518,14 |
| IS035BR Caixa de Gordura em Tijolo 30x50 Cm | Pza | 98104 | Adaptado de SINAPI 98104 (0,2x0,4 m h 0,8, tijolo maciço): escalar para 0,3x0,5 m (≈ ×1,35 alvenaria/revestimento) — Caixa de gordura simples em tijolo; alternativa dupla 0,4x0,7: 98105. | 647,83 | 427,65 |
| IS037BR Bomba d'Água de 2 Hp | Pza | 102116 + 99620*1;89353*1;92906*1;92905*1;102137*1 | Adaptado de SINAPI 102116: trocar bomba 1,48 HP por 2 HP (SINAPI salta de 1,5 CV a 3 CV: 102118) — Mesmos acessórios de IS036. | 5143,37 | 2108,34 |
| IS040BR Caixa d'Água de Polietileno 600 L. com Acessórios | Pza | 102622 | Adaptado de SINAPI 102622 (500 L com tubos, conexões e boia): trocar caixa 500 L por 600 L — Alternativa 750 L só caixa: 102606 + boia 94796. | 739,40 | 717,37 |
| IS041BR Caixa d'Água de Polietileno 1200 L. com Acessórios | Pza | 102623 | Adaptado de SINAPI 102623 (1000 L com tubos, conexões e boia): trocar caixa por 1200 L — Alternativa 1500 L: 102608 + 94796. | 1134,87 | 982,47 |
| IS042BR Caixa d'Água de Polietileno 2300 L. com Acessórios | Pza | 102609 + 94796*1 | Adaptado de SINAPI 102609 (2000 L): trocar por 2300 L — Composição só caixa; somar torneira de boia. Alternativa 3000 L: 102610. | 2136,10 | 1401,62 |
| IS043BR Caixa d'Água de Polietileno 5000 L. com Acessórios | Pza | 102617 + 94796*1 | Adaptado de SINAPI 102617 (fibra de vidro 5000 L): trocar material por polietileno — Polietileno no SINAPI vai só até 3000 L. | 4201,21 | 3826,92 |
| IS044BR Caixa d'Água de Polietileno 10 000 L. com Acessórios | Pza | 102619 + 94796*1 | Adaptado de SINAPI 102619 (fibra de vidro 10000 L): trocar por polietileno — Idem IS043. | 8728,99 | 6152,58 |
| IS045BR Fossa Séptica de Polietileno 1.200 L | Pza | 98052 | Adaptado de SINAPI 98052 (tanque séptico pré-moldado Ø1,10 h2,50, 2138 L): trocar anéis de concreto por fossa PE 1200 L — SINAPI não tem fossa plástica; 98052 é o menor tanque séptico. | 1163,59 | 2357,66 |
| IS046BR Fossa Séptica de Polietileno 2.300 L | Pza | 98052 | Adaptado de SINAPI 98052 (2138 L): fossa PE 2300 L — Idem IS045. | 2056,04 | 2357,66 |
| IS047BR Fossa Séptica 1.100 L. (Sanear) | Pza | 98052 | Adaptado de SINAPI 98052: fossa PE 1100 L (Sanear) — Idem IS045. | 1205,18 | 2357,66 |
| IS048BR Fossa Séptica 2.500 L. (Sanear) | Pza | 98052 | Adaptado de SINAPI 98052 (2138 L): fossa PE 2500 L (Sanear) — Idem IS045; alternativa 98053 (3464 L). | 2367,87 | 2357,66 |
| IS049BR Poço Absorvente (Sumidouro) de Concreto Ciclópico Ø 2 M | m | 98062 ×0.5 | Adaptado de SINAPI 98062 (sumidouro pré-moldado Ø1,88 h2,00 por UN): converter por metro de profundidade (1/2 UN/m); concreto ciclópico em vez de anéis — ArqOn por m de profundidade Ø2 m. | 1193,81 | 1722,50 |
| IS050BR Poço Absorvente (Sumidouro) em Tijolo Maciço Ø 2 M | m | 98078 ×0.3333 | Adaptado de SINAPI 98078 (sumidouro retangular tijolo maciço 0,8x1,4 h3,0): circular Ø2 m por metro (1/3 UN/m, escalar perímetro ≈ ×1,5) — SINAPI não tem sumidouro circular de tijolo. | 2142,25 | 1567,65 |
| IS059BR Fornecimento e Instalação de Tubulação de PEAD de 25 Mm (3/4″) SDR11 PN16 | m | 104060 | Adaptado de SINAPI 104060: trocar tubo PEAD DE20 por DE25 — Sem PEAD 25 mm no SINAPI. | 5,00 | 10,21 |
| IS061BR Fornecimento e Instalação de Tubulação de PEAD de 40 Mm (1 1/4″) SDR17 PN10 | m | 104061 | Adaptado de SINAPI 104061: trocar DE32 por DE40 — Sem PEAD 40 mm. | 8,69 | 18,04 |
| IS062BR Fornecimento e Instalação de Tubulação de PEAD de 50 Mm (1 1/2″) SDR17 PN8 | m | 103374 | Adaptado de SINAPI 103374 (PEAD liso 63 mm): trocar por DE50 — Sem PEAD 50 mm; 103374 sem preço SP em 08/2026. | 10,91 | — |
| IS064BR Fornecimento e Instalação de Tubulação de PEAD de 75 Mm (2 1/2″) SDR21 PN8 | m | 103375 | Adaptado de SINAPI 103375 (PEAD 90 mm): trocar por DE75 — Sem PEAD 75 mm; 103375 sem preço SP. | 23,72 | — |
| IS067BR Fornecimento e Termofusão de Tubulação de PEAD de 125 Mm (5″) SDR21 PN6 | m | 103377 + 103443*1 | Adaptado de SINAPI 103377 (PEAD 160): trocar por DE125; junta por termofusão via 103443 (160) — Sem PEAD 125 mm. ArqOn conta ~1 união/m (verificar: barras de 6-12 m). | 85,25 | — |
| IS071BR Berço de Assentamento para Tubulação (E=5 Cm) | m | 101618 ×0.03 | Adaptado de SINAPI 101618 (preparo de fundo de vala com areia, m3): converter m→m3 com e=0,05 m e largura 0,60 m; trocar areia por terra peneirada — ATENÇÃO: receita ArqOn tem 1,13 m3 de terra/m (incompatível com e=5 cm). | 133,25 | 7,92 |
| IS072BR Poço de Visita de Concreto Ciclópico H=1 M Ø 1.2 M | Pza | 97988 | Adaptado de SINAPI 97988 (base PV Ø1,20 tijolo maciço, prof. 1,40): trocar alvenaria por concreto ciclópico; H=1,0 m — SINAPI PV só em alvenaria ou pré-moldado (102139); tampão excluído. | 1596,15 | 3370,12 |
| IS073BR Poço de Visita de Concreto Ciclópico H=2 M Ø 1.2 M | Pza | 97988 + 97989*0.6 | Adaptado de SINAPI 97988 + acréscimo 97989 (0,6 m) para H=2,0 m; concreto ciclópico em vez de tijolo — Tampão excluído. | 2502,37 | 4542,90 |
| IS076BR Fornecimento e Assentamento de Tubo de Concreto D/10″ | m | 95567 | Adaptado de SINAPI 95567 (concreto simples 300 mm junta rígida): trocar por tubo 250 mm (10) — Sem tubo de concreto 250 mm; SINAPI é rede pluvial (esgoto em concreto só ≥300 JE). | 100,99 | 104,58 |
| IS079BR Fornecimento e Assentamento de Tubulação de Esgoto em PVC C-9 3″ | m | 89713 | Adaptado de SINAPI 89713 (PVC série normal esgoto DN75): 'C-9' não existe; usar série normal/reforçada — Tubo sem conexões, como ArqOn. | 54,64 | 46,79 |
| IS080BR Fornecimento e Assentamento de Tubulação de Esgoto em PVC C-9 4″ | m | 104085 | Adaptado de SINAPI 104085 (PVC ocre JE DN100 coletor predial) em lugar de C-9 colado — Alternativa predial aérea: 89714/89848. | 75,22 | 70,54 |
| IS086BR Bidê | Pza | 95469 | Adaptado de SINAPI 95469 (bacia com tubo de ligação): trocar insumo bacia por bidê com torneira; manter M.O. — SINAPI não tem bidê; mesma família de louças fixadas ao piso. | 526,59 | 373,00 |
| MP001BR Demolição de Alvenaria de Tijolo | m2 | 97622 ×0.15 | Convertir m3→m2 con e=0,15 m (ajustar al espesor real de la pared) — Demolição manual de alvenaria de bloco furado sem reaproveitamento; si es tijolo maciço usar 97624. Sin retiro de escombros | 66,92 | 11,91 |
| MP006BR Alvenaria de Tijolo 12 Cm 6 Furos com Argamassa Polimérica | m2 | 103354 | Cambiar bloco por 24x15x11 (e=11); sustituir argamassa 87292 por argamassa polimérica en bisnaga (~2,05 kg/m2; SINAPI sin insumo: usar 371 argamassa industrializada multiuso o cotización) — SINAPI no tiene alvenaria com argamassa polimérica; MO ArqOn menor (0, | 63,43 | 106,15 |
| MP007BR Alvenaria de Tijolo 16 Cm 6 Furos | m2 | 103334 | Cambiar bloco 14x9x19 deitado por 24x15x11 deitado (e≈15, 37,6 un/m2); ajustar argamassa a ~0,05 m3/m2 — Alt. 103360 (14x19x29, e=14 em pé) | 169,31 | 160,61 |
| MP008BR Alvenaria de Tijolo 9.8 Cm 6 Furos com Argamassa Colante Valkure (Hz) | m2 | 103352 | Cambiar bloco 9x14x24 por 24x15x9,8 ranhurado (28,7 un/m2); sustituir argamassa 87292 por argamassa colante para blocos (2,05 kg/m2) — SINAPI sin alvenaria com argamassa colante | 63,94 | 122,21 |
| MP009BR Alvenaria de Tijolo Maciço Tipo Adobito 15 Cm | m2 | 101159 | Cambiar tijolo maciço 5x10x20 (e=10) por tijolo maciço pequeno (69,6 un/m2, e=15); escalar argamassa por espesor x1,5 — Muro de tijolo maciço | 120,72 | 158,61 |
| MP012BR Parede de Drywall 1 Face 12 Cm, Placa 1.2x2.4 M | m2 | 96370 | Cambiar perfiles 70 mm por 90/92 mm — Drywall uso interno 1 face simples, guias simples, sin vãos | 157,30 | 61,95 |
| MP013BR Parede de Drywall 2 Faces 12 Cm, Placa 1.2x2.4 M | m2 | 96358 | Cambiar perfiles 70 mm por 90/92 mm — Drywall 2 faces simples; ArqOn trae sólo 1,76 m2 de placa por m2 (SINAPI 2,106): revisar | 190,01 | 94,59 |
| MP014BR Parede de Drywall 1 Face 92 Mm, Placa 0.90x2.40 M | m2 | 96370 | Cambiar perfiles 70 mm por 90/92 mm; placa 0,90x2,40 en vez de 1,20x2,40 — Drywall 1 face simples | 186,63 | 61,95 |
| MP015BR Parede de Drywall 2 Faces 92 Mm, Placa 0.90x2.40 M | m2 | 96358 | Cambiar perfiles 70 mm por 90/92 mm; placa 0,90x2,40 — Drywall 2 faces; ArqOn trae sólo 1,48 m2 de placa por m2 (debería ser ~2,1): revisar | 224,41 | 94,59 |
| MP020BR Parede com Placa Cimentícia 1 Face Externa | m2 | 96370 | Sustituir chapa de gesso por placa cimentícia 8 mm, massa/fita por massa com fibra de vidro, parafusos autoatarraxantes com aleta — SINAPI no tiene parede de placa cimentícia (steel frame); estructura drywall como base | 162,45 | 61,95 |
| MP021BR Parede com Placa Cimentícia 2 Faces, Interna e Externa | m2 | 96358 | Sustituir chapas de gesso por placa cimentícia 8 mm (2 faces) y tratamiento de juntas — Sin composición SINAPI de placa cimentícia | 252,57 | 94,59 |
| UH009BR Alvenaria de Tijolo Cerâmico 6 Furos | m2 | 103354 | Cambiar bloco 11,5x14x24 por tijolo 6 furos 24x15x11 con 53,9 un/m2 (pared a uma vez, e≈24 cm); escalar argamassa 87292 x~2 (0,0149→0,03 m3) y MO x~1,5 — SINAPI no tiene pared cerámica de e=24; alt. 103362 (19x19x29, e=19). Confirmar espesor del ítem ArqOn | 119,24 | 106,15 |
| OG019BR Juntas de Dilatação | m | 98575 | relleno de EPS + alcatrão en lugar de tarugo de polietileno + sellante PU — tratamiento de junta de dilatación | 8,82 | 80,50 |
| OG027BR Pilar de Tijolo Maciço 25x25 Cm | m | 101159 ×0.625 | convertir pilar 25x25 por m (0,0625 m3) a m2 de muro e=10 cm; tijolo maciço 5x10x20 por 25x12x6,5 — SINAPI no tiene pilar de ladrillo; adaptado de SINAPI 101159 | 129,41 | 99,13 |
| OG028BR Calçada de Concreto Simples | m2 | 94990 ×0.05 | convertir m3->m2 con e≈5 cm (inferido de la receta, no está en el nombre) — passeio concreto feito em obra não armado | 43,78 | 40,54 |
| OG030BR Impermeabilização de Baldrame H=30 Cm | m | 98557 ×0.5 | convertir m->m2 (~0,5 m2/m, desarrollo del baldrame H=30); alcatrão + lona en lugar de emulsão asfáltica — impermeabilización de baldrame | 14,88 | 22,87 |
| OG031BR Impermeabilização de Baldrame H=30 Cm com Manta Asfáltica (Asfaltex) | m | 98557 ×0.5 | convertir m->m2 (~0,5 m2/m); tinta asfáltica tipo Asfaltex — el nombre dice 'manta' pero la receta es pintura asfáltica; si es manta usar 98546 | 18,74 | 22,87 |
| OG037BR Pavimentação de Rua com Blocos Intertravados | m2 | 101167 | insumo ArqOn = paralelepípedo de pedra (22,5 pza/m2) con arena; nombre dice 'intertravado' — si es bloque de concreto intertravado usar 92400 (retangular 10 cm vía) | 167,03 | 149,51 |
| OG042BR Placa de Concreto para Pavimento Rígido E=17 Cm | m2 | 97112 | e=17 cm en lugar de 17,5 (x0,97 en concreto); C25 en lugar de C30 — pavimento de concreto armado PCA; receta ArqOn trae sólo 0,08 m3/m2 (incoherente con e=17) | 302,76 | 223,92 |
| OG043BR Meio-fio de Concreto para Calçada 20x40 Cm | m | 94265 | sección 20x40 moldada manualmente (0,08 m3/m) en lugar de 15x30 con extrusora (x1,8 concreto) — alternativa pré-fabricado 94273 | 120,62 | 52,70 |
| OG044BR Corte de Capa Asfáltica | m | 91283 ×0.0613 + 88309*0.0613 | componer con cortadora de piso (CHP) + pedreiro por hora — no hay composición de corte de asfalto sola; 97636 incluye demolición | 2,16 | 2,78 |
| OG045BR Sarjeta em Alvenaria | m2 | 103800 ×0.15 | convertir m3->m2 con e≈15 cm (0,154 m3 piedra/m2) — sarjeta de piedra argamasada con juntas EPS/alcatrão | 113,15 | 90,09 |
| OG046BR Demolição de Meio-fio | m | 104796 | demolición manual en lugar de mecanizada (martelete) | 17,33 | 17,39 |
| OG047BR Demolição de Capa Asfáltica | m3 | 97636 ×20 | convertir m3->m2 con e≈5 cm (20 m2/m3) — demolición parcial de pavimento asfáltico mecanizada | 21,42 | 523,00 |
| OG052BR Juntas de Dilatação com Alcatrão e Areia | m | 98577 | alcatrão y arena en lugar de tarugo + sellante silicone — junta de pavimento | 4,92 | 57,30 |
| OG053BR Fornecimento e Assentamento de Bloquete Cerâmico Tipo Pavic Padrão | m2 | 92397 | bloque cerámico 20x10x6,5 en lugar de bloque de concreto 20x10 e=6 | 167,46 | 100,50 |
| OG054BR Reaterro e Compactação com Rolo Liso | m3 | 96386 | rolo liso en lugar de rolo de pneus; SINAPI excluye material — sumar suelo seleccionado (1,28 m3) y transporte; para valas usar 93382/104737 | 406,88 | 7,25 |
| OG057BR Alvenaria de Pedra Cortada | m3 | 103800 | piedra cortada 20x20x20 en lugar de rachão — receta ArqOn 5,86 m3 de piedra por m3 (incoherente) | 1028,80 | 600,57 |
| OG059BR Fornecimento e Assentamento de Blocos de Pedra Aparelhada Tipo A 60x40x30 Cm | Pza | 103800 ×0.072 | sillar 60x40x30 (0,072 m3/pza) en lugar de rachão — receta 5,06 pza por pza: revisar unidad | 529,21 | 43,24 |
| OG060BR Fornecimento e Assentamento de Blocos de Pedra Aparelhada Tipo B 40x40x30 Cm | Pza | 103800 ×0.048 | sillar 40x40x30 (0,048 m3/pza) en lugar de rachão — insumo es 40x30x30; receta 8,17 pza por pza: revisar unidad | 554,47 | 28,83 |
| OG072BR Tubos de Drenagem em PVC (Ø = 4″) | m | 89714 | tubo PVC DN100 como dreno de tablero en lugar de ramal de esgoto — alternativa 106545 (tubo dreno PEAD DN100) | 83,02 | 52,39 |
| OG073BR Meio-fio 0.35x0.15x1.00 m (Moldado In Loco) | m | 94265 | sección 35x15 moldada manualmente (0,05 m3/m) en lugar de 15x30 con extrusora | 55,75 | 52,70 |
| OG074BR Lastro (Solado) de Pedra Rolada | m2 | 100322 ×0.12 | pedra rolada/rachão en lugar de brita n.3; m3->m2 con e≈12 cm (0,147 m3 suelto) — lastro granular | 21,06 | 20,77 |
| OG076BR Meio-fio para Jardineira em Concreto Simples R=180 kg/cm² 0.10x0.30m | m | 94263 | sección 10x30 moldada manualmente en lugar de 13x22 con extrusora | 65,82 | 39,99 |
| OG081BR Corte de Pavimento Rígido | m | 91283 ×0.1322 + 88316*0.1381 | componer con cortadora de piso (CHP) + servente por hora — no hay composición de corte de pavimento rígido sola | 5,56 | 5,56 |
| UH001BR Locação da Obra | Glb | 99059 ×10 | Glb -> m de gabarito; ArqOn ~14 h/Glb ≈ 10 m de gabarito (1,45 h/m) — medir perímetro real del gabarito; alternativa 105009 (pontaletes cada 1,5 m) | 514,94 | 788,30 |
| UH012BR Contrapiso sobre Lastro de Pedra | m2 | 95240 + 100322*0.10 | lastro de pedra de mão ~10 cm en lugar de brita n.3 (100322) + capa concreto magro 3 cm (95240) — contrapiso boliviano de piedra y concreto | 65,96 | 37,60 |
| UH022BR Estaca de Concreto Armado | m | 101176 | diámetro/armado según proyecto (broca 30 cm inteiramente armada) — receta ArqOn por m trae cantidades de 1 m3 (350 kg cemento, 80 kg acero): revisar unidad; si es pre-moldada cravada usar 100656 | 1665,27 | 164,68 |
| OT002BR Locação e Marcação da Obra | m2 | 99059 ×0.40 | convertir m2 de área a m de gabarito (perímetro+1 m): ~0,40 m/m2 para una planta de ~100 m2 — adaptado de SINAPI 99059 (gabarito tábuas c/2,00 m, 2 usos); alternativa 105009 (c/1,50 m). Fator depende de la forma de la planta | 2,28 | 31,53 |
| OT006BR Desmonte de Gabiões | m3 | 97624 | desmonte manual de gaviones (corte de malla y retiro de piedra) asimilado a demolición manual de alvenaria — adaptado de SINAPI 97624; baja aderencia, SINAPI no tiene desmonte de gabião | 58,97 | 149,23 |
| OT008BR Escoramento e Travamento | m2 | 101576 | asumir escoramento de vala descontínuo prof. 0-1,5 m, largura <1,5 m; ArqOn no indica tipo — adaptado de SINAPI 101576; si es escoramiento de encofrado/losa no aplica | 184,07 | 52,52 |
| OT009BR Placa de Obra 3x2 M | m2 | 103689 | cambiar chapa galvanizada + estructura de madera por lona impresa + tubo metálico 50x30 soldado — adaptado de SINAPI 103689 (placa de obra, _PS) | 427,51 | 504,61 |
| OT018BR Escavação 0-1.5 M em Terreno Duro | m3 | 93358 | aumentar servente ~+20 % para terreno duro; si es roca usar 102355 — adaptado de SINAPI 93358 | 120,75 | 120,57 |
| OT023BR Reaterro e Apiloamento Manual de Terra | m3 | 93382 | sustituir compactador de percusión por apisonado manual (más horas de servente) — adaptado de SINAPI 93382; SINAPI no tiene apiloamento manual | 82,75 | 34,92 |
| OT029BR Área Verde em Jardins | m2 | 105521 | sumar semilla de ray-grass, paja y turba como insumos (SINAPI no tiene semeadura de gramado) — adaptado de SINAPI 105521 (espalhamento terra vegetal) | 130,11 | 5,05 |
| OT030BR Meio-fio Ornamental em Tijolo Maciço | m | 94275 | cambiar guia pré-moldada de concreto por ladrillo macizo asentado sobre concreto — adaptado de SINAPI 94275; baja aderencia (meio-fio ornamental de ladrillo no existe en SINAPI) | 328,71 | 44,30 |
| OT031BR Cerca de Arame Farpado com Mourões de Madeira Roliça | m | 106257 | SINAPI 5 hilos, mourão roliço 11 cm c/2,5 m; ArqOn 4 hilos (reducir arame x0,8) — adaptado de SINAPI 106257 | 69,76 | 41,23 |
| OT036BR Grade Metálica para Cercamento | m2 | 98523 ×0.50 | convertir m2->m con altura ~2,0 m — adaptado de SINAPI 98523 (alambrado perfis retangulares com gradil, sin mureta; sin precio SP); alternativa 99861 m2 | 485,06 | — |
| OT037BR Limpeza Geral de Superfícies | m2 | 99803 | limpieza final genérica asimilada a limpieza de piso con paño húmedo; ArqOn 0,22 h/m2 (más pesado) — adaptado de SINAPI 99803; SINAPI 2026 no tiene «limpeza final de obra» | 7,86 | 5,26 |
| OT041BR Placa de Obra (Lona de PVC) | Pza | 103689 ×3.50 | convertir Pza->m2 (lona ~3,5 m2 por placa); lona PVC + estructura metálica en lugar de chapa galvanizada + madera — adaptado de SINAPI 103689 | 587,15 | 1766,13 |
| OT042BR Locação e Marcação de Superfície | m2 | 105137 ×0.15 | convertir m2 de superficie a m de eje de pavimentación (vía ~7 m de ancho) — adaptado de SINAPI 105137 (sin precio SP); para edificación 99059 | 3,24 | — |
| OT045BR Fornecimento e Plantio de Grama Kikuyu | m2 | 98504 | cambiar grama batatais por kikuyu + turba — adaptado de SINAPI 98504; alternativa 103946 (esmeralda) | 51,06 | 18,62 |
| OT047BR Demolição de Piso e Contrapiso | m2 | 104789 ×0.07 | convertir m2->m3 con espesor piso+contrapiso ~7 cm; si hay cerámica sumar 97633 (m2) — adaptado de SINAPI 104789 (piso de concreto simples manual); ajustar espesor real | 32,00 | 19,55 |
| OT048BR Demolição de Concreto Ciclópico | m3 | 104790 | mismo método (martelete) pero concreto ciclópico (piedra desplazadora) en lugar de piso de concreto simple; +10-20 % MO — adaptado de SINAPI 104790; SINAPI no distingue ciclópico | 187,80 | 131,17 |
| OT050BR Demolição de Alvenaria de Pedra | m3 | 97624 | cambiar alvenaria de tijolo maciço por alvenaria de pedra (mayor densidad, +MO) — adaptado de SINAPI 97624 (manual, sin reaprovechamiento) | 324,90 | 149,23 |

## NINGUNA (lista corta para Oscar)

| Ítem | Unidad | Motivo | Sugerencia |
|---|---|---|---|
| AC003BR Beiral | m2 | Beiral estucado sobre madera/tela/palha (técnica boliviana), sin composición SINAPI; mantener receta propia no-SINAPI o reemplazar por forro de beiral 96112/96111 |  |
| AC006BR Friso ou Pingadeira de Argamassa | m | Friso/pingadeira de argamassa por metro: SINAPI no tiene; mantener receta propia (revisar: 0,039 m3 de areia por m es mucho) |  |
| AC007BR Rejuntamento com Cimento Branco | m2 | SINAPI no tiene rejuntamento suelto: el rejunte está incluido en cada revestimento/piso cerâmico; sacar del catálogo BR para no duplicar o marcar no-SINAPI |  |
| AC020BR Contrapiso de Tijolo Maciço | m2 | Contrapiso de tijolo maciço (técnica boliviana) sin SINAPI; sugerir reemplazar por lastro de concreto magro 95241 o mantener no-SINAPI |  |
| CU019BR Reboco de Forro Falso | m2 | cielo falso de estuque sobre malla y listones (sistema boliviano); SINAPI no lo tiene. Mantener receta propia no-SINAPI o reemplazar por 96109 (forro placas de gesso) |  |
| IS012BR Banheira | Pza | SINAPI 08/2026 não tem banheira (nem hidromassagem). Manter receita própria marcada como não-SINAPI. |  |
| IS051BR Teste Hidráulico de Estanqueidade | m | SINAPI só tem teste de estanqueidade para gás (107319, por UN). Manter receita própria não-SINAPI ou considerar incluído no assentamento. |  |
| IS084BR Aquecedor a Gás de Tiragem Natural Q=11 L/Min | Pza | SINAPI 08/2026 não tem aquecedor de passagem a gás (só solar/boiler). Manter receita própria não-SINAPI. |  |
| IS085BR Aquecedor a Gás de Tiragem Natural Q=14 L/Min | Pza | Idem IS084. |  |
| MP016BR Parede Interna Termoacústica em Painel de EPS com Malha de Aço E=60 Mm (sem Reboco) | m | Painel EPS com malha de aço (sistema tipo Construpanel) no existe en SINAPI; mantener no-SINAPI. Unidad ArqOn m pero receta por m2 (0,98 m2): revisar |  |
| MP017BR Parede Interna Termoacústica em Painel de EPS com Malha de Aço E=75 Mm (sem Reboco) | m | Painel EPS e=75 mm: sin SINAPI; mantener no-SINAPI. Unidad m vs receta por m2 |  |
| MP018BR Parede Externa Autoportante Termoacústica em Painel de EPS com Malha de Aço E=100 Mm (sem Reboco) | m | Painel EPS autoportante e=100 mm: sin SINAPI; mantener no-SINAPI. Unidad m vs receta por m2 |  |
| MP019BR Parede Externa Autoportante Termoacústica em Painel de EPS com Malha de Aço E=120 Mm (sem Reboco) | m | Painel EPS autoportante e=120 mm: sin SINAPI; mantener no-SINAPI. Unidad m vs receta por m2 |  |
| OG029BR Verga de Madeira | m | dintel de madera con estuque (sistema boliviano); SINAPI no lo tiene; sacar del catálogo BR o mantener receta propia no-SINAPI |  |
| OG032BR Aplicação de Isolamento Acústico Projetado E=45-60 Mm | m2 | aislamiento acústico proyectado (spray) no existe en SINAPI; mantener receta propia no-SINAPI |  |
| OG033BR Aplicação de Isolamento Térmico Projetado E=20-25 Mm | m2 | aislamiento térmico proyectado no existe en SINAPI; mantener receta propia no-SINAPI |  |
| OG034BR Aplicação de Isolamento Térmico Projetado E=10-15 Mm | m2 | aislamiento térmico proyectado no existe en SINAPI; mantener receta propia no-SINAPI |  |
| OG035BR Aplicação de Isolamento Térmico Projetado E=15-20 Mm | m2 | aislamiento térmico proyectado no existe en SINAPI; mantener receta propia no-SINAPI |  |
| OG038BR Bueiro de Chapa Metálica Corrugada Ø 1 M | m | bueiro metálico corrugado no está en SINAPI (sí en SICRO/DNIT); mantener receta propia no-SINAPI |  |
| OG048BR Fabricação de Bloquetes Sextavados | m2 | fabricación in situ de adoquines; SINAPI sólo tiene el insumo comercial (711 bloquete sextavado); sacar del catálogo BR |  |
| OG066BR Viga Pré-moldada de Concreto Protendido (f'c=350 Kg/cm2) L=20,60 M | m | viga pre-moldada protendida L=20,60 m para puente: no existe en SINAPI (sí en SICRO); mantener receta propia no-SINAPI |  |
| OG067BR Viga Pré-moldada de Concreto Protendido (f'c=350 Kg/cm2) L=25,60 M | m | viga pre-moldada protendida L=25,60 m para puente: no existe en SINAPI (sí en SICRO); mantener receta propia no-SINAPI |  |
| OG068BR Viga Pré-moldada de Concreto Protendido (f'c=350 Kg/cm2) L=35,60 M | m | viga pre-moldada protendida L=35,60 m para puente: no existe en SINAPI (sí en SICRO); mantener receta propia no-SINAPI |  |
| OG069BR Viga Pré-moldada de Concreto Protendido (f'c=350 Kg/cm2) L=45,60 M | m | viga pre-moldada protendida L=45,60 m para puente: no existe en SINAPI (sí en SICRO); mantener receta propia no-SINAPI |  |
| OG070BR Aparelhos de Apoio em Neoprene Fretado | dm3 | aparato de apoyo neopreno zunchado (dm3) no está en SINAPI (sí en SICRO) |  |
| OG071BR Junta de Dilatação | m | junta de dilatación metálica de puente (angulares) no está en SINAPI (sí en SICRO) |  |
| OT001BR Instalação do Canteiro de Obras | Glb | SINAPI 08/2026 no trae barracão/almoxarifado de madera (sólo tapume 98458/98459 y contenedor 105115/105116). Mantener receta propia marcada no-SINAPI o presupuestar como verba de canteiro |  |
| OT034BR Fornecimento e Instalação de Grama Sintética Bicolor H=5 Mm | m2 | SINAPI no tiene grama sintética (sólo equipo varredeira). Mantener receta propia marcada no-SINAPI |  |
| OT035BR Fornecimento e Instalação de Grama Sintética Monofilamento H=6 Mm | m2 | SINAPI no tiene grama sintética. Mantener receta propia marcada no-SINAPI |  |
| OT040BR Biossegurança em Obra de Médio Porte (Projetos 500k-1M Bs) | Glb | Bioseguridad COVID (Bolivia, rango en Bs): sin equivalente SINAPI. Sacar del catálogo BR |  |
| OT044BR Preenchimento com Lama (Lameado) com Fornecimento de Material | m3 | Lameado (relleno con limo/lodo) es práctica boliviana; sin equivalente. Sacar del catálogo BR o sustituir por aterro 94316 |  |

## Cuidado con los datos

- Las composiciones SINAPI describen el método brasileño (bloques 9×14×19/24, argamassa 1:2:8 preparada en betonera, hormigón usinado bombeado, forma de chapa resinada); sus coeficientes de mano de obra traen la productividad medida por la Caixa, que no es la boliviana.
- El SINAPI trabaja con muchas composiciones auxiliares anidadas (mortero, concreto, mano de obra «com encargos complementares», costo horario de equipo CHP/CHI). Para cargarlas en ArqOn hay que aplanarlas (llevar cada auxiliar a sus insumos) o crear ítems auxiliares; la columna «profundidad» dice cuántos niveles hay.
- 24 composiciones elegidas no tienen costo en São Paulo en 08/2026 (celda vacía/0 en CCD: p. ej. 98683, 106783/106784, 104099, 107142-107144, 103374/103375/103381, 106463…). En esos casos usar el costo de otra UF o sumar los insumos a mano.
- Transporte (97914/95875) está **por km** (m³×km o t×km): hay que multiplicar por la DMT y el esponjamiento de cada obra.
- Algunos factores de unidad son estimados, no exactos (m² de encofrado por m³ de hormigón, replanteo por m², demolición de piso con e ≈ 7 cm): están marcados en la nota del ítem.
- Puentes y carreteras (vigas protendidas, neopreno, bueiros de chapa corrugada, capa asfáltica) son del SICRO/DNIT, no del SINAPI.
- Las demoliciones y el movimiento de tierra del SINAPI no incluyen carga/transporte salvo que lo digan; los ítems ArqOn a veces sí.

## Nota legal

El SINAPI es dato oficial y público (Caixa Econômica Federal / IBGE, Decreto 7.983/2013), de uso libre y citable. Cómo citarlo en ArqOn: «SINAPI (Caixa/IBGE), ref. MM/AAAA, UF, COM/SEM desoneração, composição/insumo NNNN». Las recetas adaptadas deben decir «adaptado de SINAPI NNNN» y no presentarse como la composición oficial. La copia usada es un espejo sin cambios del libro nacional (se registra su sha256).

## Plan para que todo Brasil siga SINAPI

### Cuántos

- Insumos estimados hoy: 613 → **MAPEAR 160** · **SUSTITUIR 301** · **QUITAR 152** (detalle en `precios/fuentes/propuesta_sinapi_BR_20260928.csv`). Más los 138 ya mapeados (incluida toda la mano de obra y los equipos).
- Ítems: EQUIVALENTE 111 · PARCIAL 80 · ADAPTADA 153 · NINGUNA 31.

### Fases (en este orden)

1. **Precios, fase 1 (lista ya):** aprobar y correr `tools/aplicar-propuesta-sinapi-br.py --clase SEGURO --aplicar` (160 insumos). Sin tocar recetas. Ítems 100 % SINAPI: 123 → 140.
2. **Corregir las recetas ArqOn incoherentes** listadas arriba (≈20 ítems): son errores de la receta boliviana, no de Brasil; conviene hacerlo antes de comparar con el SINAPI.
3. **Recetas EQUIVALENTE** (111): adoptar los coeficientes SINAPI. Primero las que ya tienen todos sus insumos mapeados (se pueden cargar sin decisiones de precios); luego el resto cuando entren sus insumos (fase 4). Nota en cada ítem: «SINAPI NNNN, ref. 08/2026».
4. **Precios, fase 2 — SUSTITUIR** (301 insumos): reemplazar en las recetas el insumo estimado por el SINAPI propuesto (coeficiente × factor). Revisar a mano los DUDOSO marcados por ratio y los factores supuestos (densidades, piezas por m²).
5. **Recetas PARCIAL** (80): aplanar las composiciones auxiliares (mortero, concreto, encofrado, armadura) o partir el ítem ArqOn en los ítems SINAPI correspondientes; decidir con Oscar si el catálogo BR mantiene ítems «todo en uno» por m³ (y cómo se prorratea el encofrado).
6. **Recetas ADAPTADA** (153): copiar la composición de la misma familia, aplicar la adaptación descrita (medida, espesor, bloque, unidad) y marcar «adaptado de SINAPI NNNN».
7. **QUITAR** (152 insumos) y **NINGUNA** (31 ítems): sacar de las recetas y de la lista BR lo que no tiene rol en Brasil; para los NINGUNA, Oscar decide entre sacarlos del catálogo BR (bioseguridad, lameado, sistemas bolivianos, puentes) o dejarlos como receta propia marcada «no SINAPI».
8. **Mantenimiento mensual:** bajar el libro nuevo, registrar su sha256 y correr `tools/precios-sinapi-br.py`; volver a comprobar que las composiciones adoptadas no cambiaron de código (AF_mm/aaaa).

### Cambio estimado del costo directo por familia (São Paulo)

Mediana, por categoría, del cociente contra el costo de hoy. «Precios» = misma receta con precios SINAPI; «Composición» = costo CCD de la composición propuesta (EQUIVALENTE/PARCIAL/ADAPTADA con costo calculable).

| Categoría | Ítems | Mediana precios/hoy | Ítems con composición | Mediana composición/hoy | Suma hoy | Suma composición (mismos ítems) |
|---|---:|---:|---:|---:|---:|---:|
| Inst. Sanitarias | 86 | 1,00 | 74 | 0,98 | 61711,42 | 57647,35 |
| Obra Gruesa | 84 | 1,00 | 71 | 0,96 | 54894,20 | 62860,31 |
| Acabados | 70 | 1,00 | 62 | 0,68 | 8467,23 | 8565,51 |
| Otros | 45 | 1,00 | 37 | 0,63 | 4914,76 | 4664,60 |
| Cubiertas | 26 | 1,00 | 22 | 0,68 | 3900,19 | 2487,55 |
| Inst. Eléctricas | 24 | 0,98 | 20 | 0,94 | 59183,76 | 31157,69 |
| Carpintería | 22 | 1,00 | 20 | 1,32 | 13514,31 | 17589,54 |
| Mampostería | 18 | 0,98 | 14 | 0,62 | 2488,27 | 1939,06 |

