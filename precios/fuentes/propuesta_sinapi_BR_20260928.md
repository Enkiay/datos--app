# Cruce de los precios ESTIMADOS de Brasil con el SINAPI (propuesta, 28-sep-2026)

**Nada aplicado.** Propuesta para revisar. El detalle, fila por fila, está en `propuesta_sinapi_BR_20260928.csv` (columnas pedidas + `accion`, `usoItems`, `lineasCatalogo`).

- Fuente: SINAPI (Caixa/IBGE), libro nacional `SINAPI_Referência` 08/2026, hoja **ICD** (insumos, COM desoneração). Es el mismo libro de `sinapi_BR.json` (sha256 `1587f458…4aec89` comprobado). El libro NO está en el repo: se guardó fuera, en `%LOCALAPPDATA%\Temp\sinapi\SINAPI_Referencia_2026_08.xlsx`.
- Se revisaron los **613** insumos que hoy dicen «ESTIMADO por relación con Bolivia» (todos los que no están en `mapa_sinapi_BR.csv`). La mano de obra ya estaba toda en el mapa (CCD).
- Criterio: mismo producto (material, medida/sección/diámetro/capacidad) y unidad igual o con factor exacto. Ante la duda, DUDOSO. Nunca un material suelto contra un conjunto armado (ventana entera, puerta completa, instalado) ni al revés.
- Precio de control: São Paulo, precio SINAPI × factor contra el estimado actual. Ratio fuera de 0,33-3 se marca.

## Cuántos

| Clase | Insumos | Acción propuesta |
|---|---:|---|
| SEGURO | 160 | MAPEAR (se agregan al mapa y el script les pone precio SINAPI por estado) |
| DUDOSO | 256 | SUSTITUIR por el insumo SINAPI más parecido (con factor de receta) |
| SIN_EQUIVALENTE | 197 | 45 SUSTITUIR por un sustituto de práctica brasileña, 152 QUITAR |
| **Total** | **613** | MAPEAR 160 · SUSTITUIR 301 · QUITAR 152 |

QUITAR: 48 no se usan en ninguna receta BR (salen sólo de la lista de precios); 104 sí se usan y salen de sus recetas (varios dejan su ítem sin material principal → ese ítem va a NINGUNA en el análisis de composiciones).

### Por tipo de insumo

| Tipo | SEGURO | DUDOSO | SIN_EQUIVALENTE |
|---|---:|---:|---:|
| HERRAMIENTA | 0 | 0 | 4 |
| MATERIAL | 160 | 256 | 193 |

### Por categoría

| Categoría | SEGURO | DUDOSO | SIN_EQUIVALENTE |
|---|---:|---:|---:|
| Plomería | 74 | 61 | 40 |
| Acero y Metal | 31 | 29 | 34 |
| Ferretería | 6 | 34 | 36 |
| Eléctrico | 12 | 19 | 10 |
| Ladrillos y Cerámicos | 13 | 19 | 8 |
| Cemento y Cal | 3 | 12 | 16 |
| Cubiertas | 5 | 19 | 5 |
| Impermeabilización | 2 | 22 | 5 |
| Agregados | 2 | 12 | 13 |
| Obras Civiles | 1 | 7 | 14 |
| Adhesivos | 6 | 8 | 5 |
| Madera | 2 | 8 | 4 |
| Pinturas | 3 | 6 | 3 |
| Herramientas | 0 | 0 | 2 |
| Maquinaria | 0 | 0 | 2 |

## Cuánto del catálogo se mueve

- Líneas de receta del catálogo BR: 2210; con insumo estimado hoy: **557**.
- Fase 1 (sólo SEGURO → MAPEAR): pasan a SINAPI **101** líneas, en 61 ítems. Ítems 100 % SINAPI: 123 hoy → **140** de 375.
- Plan completo (MAPEAR + SUSTITUIR + QUITAR): 101 + 319 líneas pasan a SINAPI y 137 salen de sus recetas → **375 de 375** ítems quedan 100 % con precio SINAPI (cero estimados).

## Conversiones que vale la pena mirar

- **Hierro de construcción en barra** (CA-50 y CA-25): el SINAPI da el kg; barra de 12 m × masa nominal NBR 7480 (6,3 mm 0,245 · 8 mm 0,395 · 10 mm 0,617 · 12,5 mm 0,963 · 16 mm 1,578 · 20 mm 2,466 · 25 mm 3,853 kg/m). Ø 6 mm → bitola brasileña 6,3; Ø 12 mm → 12,5.
- **Perfiles en «Barra»** (barra chata, ángulo, cañería galvanizada en pieza): barra comercial de 6 m. Sólo son SEGURO cuando el SINAPI trae la misma sección por metro; cuando hay que calcular kg/m con la densidad del acero quedan DUDOSO.
- **Placas por pieza ↔ m²**: drywall 1,2 × 2,4 = 2,88 m²; EPS 100 × 50 = 0,5 m²; alambre de púas rollo 500 m; limpiador PVC 2 L = 2 frascos de 1000 cm³; rejunte bolsa 5 kg; argamassa colante bolsa 20 kg; agente de curado 20 kg.
- **Madera**: listón 2"×2" en p2 ↔ caibro 5×5 por m: 1 p2 = 0,9144 m. Tablas en p2 ↔ m³: 1 p2 = 0,00236 m³ (el mismo del mapa).
- **Sellador PU en cm³** ↔ cartucho 310 ml: factor 1/310. **Adoquín** por pieza ↔ paralelepípedo por millar: 0,001.
- **Cobre**: 1/2" = 15 mm, 3/4" = 22 mm (NBR 13206); los «(12 mm)/(16 mm)» del nombre ArqOn son nominales bolivianos.

## 25 ejemplos SEGURO (al azar)

| idCanonico | ArqOn | SINAPI | factor | est. SP | SINAPI SP | ratio |
|---|---|---|---:|---:|---:|---:|
| `br_tee_de_cobre_o_1_2_12_mm_pza` | Tê de cobre Ø 1/2″ (12 mm) (Pza) | 12733 TE DE COBRE SEM ANEL DE SOLDA, BOLSA X BOLSA X BOLSA, 15 MM (UN) | 1 | 16,63 | 10,21 | 0,61 |
| `br_ceramica_esmaltada_brasilena_30_30_cm_m2` | Revestimento cerâmico esmaltado brasileiro 30×30 cm (m2) | 536 REVESTIMENTO PARA PAREDE, EM CERAMICA ESMALTADA, FORMATO MENOR OU IGUA (M2) | 1 | 58,38 | 27,55 | 0,47 |
| `br_fierro_corrugado_o_10_mm_3_8_barra` | Vergalhão de aço CA-50 Ø 10 mm (3/8″) (Barra) | 34 ACO CA-50, 10,0 MM, VERGALHAO (KG) | 7.404 | 52,42 | 49,53 | 0,94 |
| `br_plaqueta_interruptor_simple_pza` | Placa com Interruptor Simples (Pza) | 38062 INTERRUPTOR SIMPLES 10A, 250V, CONJUNTO MONTADO PARA EMBUTIR 4" X 2" ( (UN) | 1 | 14,44 | 7,03 | 0,49 |
| `br_perfil_track_de_92_mm_l_4_m_pza` | Perfil Guia (Track) 92 Mm L=4 M (Pza) | 39420 PERFIL GUIA, FORMATO U, EM ACO ZINCADO, PARA ESTRUTURA PAREDE DRYWALL, (M) | 4 | 23,23 | 27,12 | 1,17 |
| `br_copla_galvanizada_o_1_1_2_37_mm_pza` | Luva galvanizada Ø 1 1/2″ (37 mm) (Pza) | 3939 LUVA DE FERRO GALVANIZADO, COM ROSCA BSP, DE 1 1/2" (UN) | 1 | 21,66 | 24,50 | 1,13 |
| `br_caneria_fg_3_l_6m_pza` | Tubo de Ferro Galvanizado 3″ L=6m (Pza) | 7694 TUBO ACO GALVANIZADO COM COSTURA, CLASSE MEDIA, DN 3", E = *4,05* MM,  (M) | 6 | 447,00 | 768,96 | 1,72 |
| `br_electroducto_flexible_corrugado_20_mm_1_2_m` | Eletroduto Flexível Corrugado 20 Mm (1/2″) (m) | 2689 ELETRODUTO PVC FLEXIVEL CORRUGADO, COR AMARELA, DE 20 MM (M) | 1 | 2,20 | 2,09 | 0,95 |
| `br_pintura_sintetica_color_azul_gal` | Tinta Esmalte Sintético Azul (L) | 43647 TINTA ESMALTE SINTETICO STANDARD BRILHANTE (L) | 1 | 21,83 | 31,28 | 1,43 |
| `br_niple_hexagonal_galvanizado_o_2_50_mm_pza` | Niple hexagonal galvanizado Ø 2″ (50 mm) (Pza) | 4181 NIPLE DE FERRO GALVANIZADO, COM ROSCA BSP, DE 2" (UN) | 1 | 32,33 | 37,55 | 1,16 |
| `br_union_universal_galvanizada_o_3_4_16_mm_pza` | União universal galvanizada Ø 3/4″ (16 mm) (Pza) | 9885 UNIAO DE FERRO GALVANIZADO, COM ROSCA BSP, COM ASSENTO PLANO, DE 3/4" (UN) | 1 | 33,58 | 34,36 | 1,02 |
| `br_copla_galvanizada_o_3_4_16_mm_pza` | Luva galvanizada Ø 3/4″ (16 mm) (Pza) | 3909 LUVA DE FERRO GALVANIZADO, COM ROSCA BSP, DE 3/4" (UN) | 1 | 10,36 | 8,80 | 0,85 |
| `br_fierro_corrugado_3_8_10mm_l_12m_barra` | Vergalhão de Aço CA-50 3/8″ (10mm) L=12m (Barra) | 34 ACO CA-50, 10,0 MM, VERGALHAO (KG) | 7.404 | 32,64 | 49,53 | 1,52 |
| `br_sika_1_impermeabilizante_de_masa_l` | Sika 1, impermeabilizante de massa (L) | 123 ADITIVO IMPERMEABILIZANTE DE PEGA NORMAL PARA ARGAMASSAS E CONCRETOS S (L) | 1 | 16,32 | 6,93 | 0,42 |
| `br_codo_de_cobre_con_terminal_rosca_interna_o_3_4_pza` | Joelho de cobre com rosca interna Ø 3/4″ (Pza) | 39871 COTOVELO BRONZE/LATAO SEM ANEL DE SOLDA, BOLSA X ROSCA F, 22MM X 3/4" (UN) | 1 | 28,25 | 34,37 | 1,22 |
| `br_reduccion_galvanizada_de_2_a_1_pza` | Bucha de redução galvanizada de 2″ para 1″ (Pza) | 771 BUCHA DE REDUCAO DE FERRO GALVANIZADO, COM ROSCA BSP, DE 2" X 1" (UN) | 1 | 28,88 | 29,68 | 1,03 |
| `br_pletina_3_4_1_8_m` | Barra Chata 3/4″ - 1/8″ (m) | 566 BARRA DE ACO CHATO, RETANGULAR, 19,05 MM X 3,17 MM (L X E), 0,47 KG/M (M) | 1 | 4,83 | 4,22 | 0,87 |
| `br_fierro_corrugado_o_8_mm_5_16_barra` | Vergalhão de aço CA-50 Ø 8 mm (5/16″) (Barra) | 33 ACO CA-50, 8,0 MM, VERGALHAO (KG) | 4.74 | 37,66 | 33,65 | 0,89 |
| `br_cable_enchaquetado_2x6_mm_m` | Cabo Multipolar 2x6 mm² (m) | 34609 CABO FLEXIVEL PVC 750 V, 2 CONDUTORES DE 6,0 MM2 (M) | 1 | 8,79 | 17,89 | 2,04 |
| `br_bloque_de_vidrio_20_x_20_cm_pza` | Bloco de Vidro 20 X 20 Cm (Pza) | 716 BLOCO / TIJOLO DE VIDRO INCOLOR, XADREZ, *20 X 20 X 10* CM (A X L X E) (UN) | 1 | 15,07 | 20,44 | 1,36 |
| `br_fierro_corrugado_1_4_6mm_l_12m_barra` | Vergalhão de Aço CA-50 1/4″ (6mm) L=12m (Barra) | 32 ACO CA-50, 6,3 MM, VERGALHAO (KG) | 2.94 | 12,55 | 20,76 | 1,65 |
| `br_flotador_electrico_pza` | Chave Boia Elétrica (Pza) | 7588 AUTOMATICO DE BOIA SUPERIOR / INFERIOR, *15* A / 250 V (UN) | 1 | 136,00 | 44,90 | 0,33 |
| `br_cruz_galvanizada_o_1_2_12_mm_pza` | Cruzeta galvanizada Ø 1/2″ (12 mm) (Pza) | 1647 CRUZETA DE FERRO GALVANIZADO, COM ROSCA BSP, DE 1/2" (UN) | 1 | 19,77 | 22,98 | 1,16 |
| `br_ceramica_esmaltada_nal_20x30cm_m2` | Revestimento Cerâmico Esmaltado NAC. 20x30cm (m2) | 536 REVESTIMENTO PARA PAREDE, EM CERAMICA ESMALTADA, FORMATO MENOR OU IGUA (M2) | 1 | 45,51 | 27,55 | 0,60 |
| `br_terminal_de_cobre_con_rosca_interna_o_3_4_pza` | Conector de cobre com rosca interna Ø 3/4″ (Pza) | 39864 CONECTOR BRONZE/LATAO SEM ANEL DE SOLDA, BOLSA X ROSCA F, 22 MM X 3/4" (UN) | 1 | 27,62 | 25,40 | 0,92 |

## Marcados (ratio fuera de 0,33-3)

Los SEGURO marcados se mantienen SEGURO sólo si es el mismo producto con la misma unidad y factor 1 (no puede haber error de unidad); el resto quedó DUDOSO.

| idCanonico | clase | SINAPI | factor | est. SP | SINAPI SP | ratio | nota |
|---|---|---|---:|---:|---:|---:|---|
| `br_estiercol_de_ovino_kg` | DUDOSO | 38125 | 1 | 109,00 | 1,88 | 0,02 | Fertilizante orgánico compuesto clase A (38125), kg: no es estiércol ovino. |
| `br_soldadura_para_calamina_kg` | DUDOSO | 13388 | 1 | 10,04 | 227,94 | 22,70 | Soldadura en barra estaño-plomo 50/50, kg; el precio SINAPI es ~20× el estimado (el estimado no es de estaño): |
| `br_tablero_medidor_8_espacios_pza` | DUDOSO | 39690 | 1 | 193,00 | 2756,94 | 14,29 | Caja de medición colectiva para 8 medidores (39690): alcance mucho mayor; revisar. |
| `br_revoque_fino_facil_kg` | DUDOSO | 371 | 1 | 8,47 | 0,76 | 0,09 | Revoque fino premezclado ↔ «argamassa industrializada multiuso»; no es el mismo producto exacto. |
| `br_luminaria_tipo_farola_led_80w_clase_ii_pza` | DUDOSO | 42246 | 1 | 2134,00 | 208,44 | 0,10 | Luminaria LED de alumbrado público 68-97 W; el precio SINAPI es ~1/10 del estimado: revisar. |
| `br_plancha_metalica_1_4_2x1_m_pza` | DUDOSO | 1330 | 99.58 | 91,02 | 862,36 | 9,47 | Chapa ASTM A36 1/4" (49,79 kg/m²) × 2 m² = 99,58 kg. Factor exacto, pero el precio SINAPI sale ~9× el estimado |
| `br_parket_tajibo_m2` | DUDOSO | 6214 | 1 | 40,80 | 292,64 | 7,17 | Taco de ipê 7×42 e = 2 cm, m²; el precio SINAPI es ~7× el estimado: revisar. |
| `br_camara_desgrasadora_pvc_sanear_pza` | DUDOSO | 35277 | 1 | 65,91 | 441,28 | 6,70 | Caja de grasa de PVC 18 L con tapa y canasto; el precio SINAPI es ~7× el estimado: revisar tamaño. |
| `br_sika_top_107_seal_mortero_impermeabilizante_25_kg` | DUDOSO | 135 | 25 | 524,00 | 79,50 | 0,15 | Mortero polimérico impermeabilizante bicomponente, kg × 25; es de marca y el genérico sale ~6× más barato. |
| `br_colmafix_32_puente_de_adherencia_kg` | DUDOSO | 156 | 1 | 335,00 | 51,36 | 0,15 | Puente de adherencia epóxico (marca); genérico SINAPI «adesivo estrutural epóxi fluido». |
| `br_sika_aer_incorporador_de_aire_20_kg` | DUDOSO | 133 | 20 | 847,00 | 137,40 | 0,16 | Incorporador de aire (L); ArqOn en kg. Factor supuesto: densidad supuesta 1 kg/L. |
| `br_sikadur_31_hmg_adhesivo_epoxico_de_anclaje_kg` | DUDOSO | 131 | 1 | 266,00 | 43,92 | 0,17 | Epóxico tixotrópico (marca) ↔ genérico «adesivo estrutural epóxi pastoso»; el precio de marca es ~6× el genéri |
| `br_griferia_para_urinario_pza` | DUDOSO | 21112 | 1 | 57,75 | 327,02 | 5,66 | Válvula de descarga cromada para urinario (21112); el precio SINAPI es ~6× el estimado: revisar tipo. |
| `br_alambre_tejido_rollo_50_m_0_80_m_de_alto_rollo` | DUDOSO | 10928 | 40 | 117,00 | 621,60 | 5,31 | Rollo 50 × 0,80 m = 40 m²; hilo/malla no dichos y el SINAPI es de h = 2 m. |
| `br_sikalatex_adhesivo_y_aditivo_acrilico_5_kg` | DUDOSO | 7334 | 5 | 376,00 | 74,40 | 0,20 | Aditivo adhesivo líquido (L); ArqOn en kg. Factor supuesto: densidad supuesta 1 kg/L. |
| `br_alambre_tejido_m2` | DUDOSO | 10928 | 1 | 3,08 | 15,54 | 5,04 | Tela de alambre sin especificar; candidatos 14 BWG malla 8×8 (10928) o 5×5 (7167). |
| `br_zocalo_granitico_de_25x10_cm_m` | DUDOSO | 34680 | 1 | 9,42 | 44,95 | 4,77 | Zócalo premoldeado de granilite L = 10 cm, m. El precio SINAPI es ~5× el estimado: revisar. |
| `br_perno_1_1_2_autoperforante_pza` | DUDOSO | 44286 | 1 | 0,94 | 0,20 | 0,21 | Autobrocante 12 × 7/8" (44286); ArqOn 1 1/2". |
| `br_pegamento_para_cpvc_agua_caliente_1_l` | DUDOSO | 21114 | 13.33 | 99,18 | 452,29 | 4,56 | Idem, 1 L. Factor supuesto: 1 L ≈ 1000 g ≈ 13,3 envases de 75 g. |
| `br_bisagra_4_simple_pza` | DUDOSO | 2432 | 1 | 6,59 | 29,08 | 4,41 | Idem. |
| `br_sikadur_32_kg` | DUDOSO | 156 | 1 | 224,00 | 51,36 | 0,23 | Puente de adherencia epóxico fluido (marca) ↔ genérico. |
| `br_tornillo_hexagonal_pza` | DUDOSO | 13294 | 1 | 0,31 | 1,32 | 4,26 | Tornillo hexagonal sin medida; candidatos 13294 (3/8"×80) o 44738 (M10×30). Factor supuesto: pieza = pieza. |
| `br_tacos_de_plastico_pza` | DUDOSO | 4376 | 1 | 0,38 | 0,09 | 0,24 | Taco de nylon sin medida: S8 (4376) o S6 (4375). |
| `br_llave_de_paso_tipo_cortina_de_cobre_o_3_4_pza` | DUDOSO | 6016 | 1 | 115,00 | 27,46 | 0,24 | Latón bruto 3/4" (6016); idem. |
| `br_alambre_tejido_malla_m2` | DUDOSO | 10928 | 1 | 3,95 | 15,54 | 3,93 | Alambrado sin especificar; 14 BWG 8×8 (10928). |
| `br_disco_de_corte_pza` | DUDOSO | 44531 | 1 | 18,83 | 70,54 | 3,75 | Disco de corte sin tipo: diamantado 180 mm (44531) o para metal 300 mm (44495). |
| `br_supertubo_hdpe_200_mm_8_pn6_m` | DUDOSO | 44547 | 1 | 119,00 | 442,43 | 3,72 | SINAPI 200 SDR 11 PN 12,5; ArqOn PN 6. |
| `br_supertubo_hdpe_160_mm_6_pn6_m` | DUDOSO | 44545 | 1 | 77,09 | 283,81 | 3,68 | SINAPI 160 SDR 11 PN 12,5; ArqOn PN 6: otra pared. |
| `br_chicotillo_pza` | DUDOSO | 6141 | 1 | 23,23 | 6,34 | 0,27 | Flexible sin material/largo: PVC 1/2" × 30 cm (6141) o inox (11683). |
| `br_politubo_3_4_m` | DUDOSO | 9813 | 1 | 1,51 | 5,49 | 3,64 | Politubo (manguera negra de polietileno) 3/4" ↔ tubo PEAD 20 mm de conexión domiciliaria: otro producto. |
| `br_bomba_de_agua_1_5_hp_pza` | DUDOSO | 734 | 1 | 4614,00 | 1281,61 | 0,28 | Bomba centrífuga 1,48 HP (734/735). |
| `br_bisagra_4_doble_pza` | DUDOSO | 2432 | 1 | 8,16 | 29,08 | 3,56 | El SINAPI no tiene 4" (3" y 3 1/2"). |
| `br_pegamento_para_ladrillo_valkure_kg_kg` | DUDOSO | 371 | 1 | 2,70 | 0,76 | 0,28 | Pegamento de ladrillo ↔ argamassa industrializada multiuso. |
| `br_vidrio_catedral_blanco_3_mm_m2` | DUDOSO | 10499 | 1 | 36,41 | 125,41 | 3,44 | Vidrio impreso: el SINAPI tiene martelado/canelado 4 mm. |
| `br_zocalo_cedro_3_m` | DUDOSO | 6186 | 1 | 8,16 | 28,01 | 3,43 | Zócalo de madera maciza cumaru/ipê 1,5 × 7 cm (no cedro, 7 cm ≈ 3"). |
| `br_pisopak_30x30cmx1_6_mm_m2` | DUDOSO | 4790 | 1 | 30,13 | 101,80 | 3,38 | Placa vinílica semiflexible e = 2 mm (4790); ArqOn 30×30 × 1,6 mm (la de 30×30 del SINAPI es de 3,2 mm, 4792). |
| `br_tornillo_para_madera_pza` | DUDOSO | 11057 | 1 | 0,50 | 0,15 | 0,30 | Tornillo para madera sin medida; candidatos rosca soberba 4,8×40 (11057) o 4,2×32 (4377). Factor supuesto: pie |
| `br_perno_de_expansion_pza` | DUDOSO | 44179 | 1 | 4,71 | 1,43 | 0,30 | Anclaje de expansión sin medida; parabolt 3/8" × 3 3/4" (44179). |
| `br_bisagra_de_metal_pza` | DUDOSO | 2433 | 1 | 3,01 | 9,85 | 3,27 | Bisagra sin medida. |
| `br_fullcaneria_para_tubos_de_pvc_envase_18_l_pza` | DUDOSO | 122 | 21.18 | 432,00 | 1401,48 | 3,24 | Adhesivo PVC: el SINAPI en frasco de 850 g; ArqOn envase de 18 L. Factor supuesto: 18 L ≈ 18 kg ÷ 0,85 kg por  |
| `br_pegamento_para_cpvc_agua_caliente_1_4_l` | DUDOSO | 21114 | 3.33 | 34,84 | 112,99 | 3,24 | Adhesivo CPVC: el SINAPI es un envase de 75 g; ArqOn 1/4 L (sin densidad no hay factor exacto). Factor supuest |
| `br_pegaladrillo_facil_kg` | DUDOSO | 371 | 1 | 2,45 | 0,76 | 0,31 | Argamassa industrializada multiuso para asentar bloques; el precio SINAPI sale ~1/3 del estimado. |
| `br_piedra_tarija_m2` | DUDOSO | 4712 | 1 | 25,11 | 79,77 | 3,18 | Piedra laja irregular ↔ «pedra quartzito/calcário laminado, caco, tipo São Tomé». |
| `br_chapa_exterior_p_puerta_metalica_pza` | DUDOSO | 11484 | 1 | 217,00 | 69,85 | 0,32 | Cerradura de sobreponer para portón (11484). |
| `br_supertubo_hdpe_75_mm_2_1_2_m` | DUDOSO | 44524 | 1 | 20,90 | 62,99 | 3,01 | SINAPI 75 SDR 11 PN 12,5; ArqOn sin clase. |
| `br_cal_kg` | SEGURO | 1106 | 1 | 8,47 | 1,10 | 0,13 | Cal hidratada CH-I para argamassas, kg. Ratio fuera de rango revisado: misma unidad y sin factor; el estimado  |
| `br_yute_m2` | SEGURO | 44529 | 1 | 3,45 | 20,96 | 6,08 | Tela de arpillera (yute), m². [Ratio 6.075 fuera de 0,33-3 revisado: mismo producto, misma unidad, factor 1; l |
| `br_cola_fresca_kg` | SEGURO | 44396 | 1 | 10,67 | 44,16 | 4,14 | Cola blanca base PVA, kg. Ratio fuera de rango revisado: misma unidad y sin factor; la diferencia viene de la  |
| `br_anillo_de_goma_stp_2_pza` | SEGURO | 296 | 1 | 6,28 | 1,69 | 0,27 | Anillo de goma para tubo de desagüe DN 50 (2"), NBR 5688. [Ratio 0.269 fuera de 0,33-3 revisado: mismo product |
| `br_fulminante_pza` | SEGURO | 2759 | 1 | 3,14 | 11,37 | 3,62 | Espoleta simple N° 8. [Ratio 3.621 fuera de 0,33-3 revisado: mismo producto, misma unidad, factor 1; la difere |
| `br_vidrio_plano_arg_incoloro_3_mm_m2` | SEGURO | 10490 | 1 | 40,80 | 131,68 | 3,23 | Vidrio liso incoloro 2 a 3 mm sin colocación, m². [Ratio 3.227 fuera de 0,33-3 revisado: mismo producto, misma |
| `br_eq_estacion_total` | SIN_EQUIVALENTE | 7247 | 1 | 30,95 | 2,81 | 0,09 | El SINAPI no tiene estación total (sólo alquiler de teodolito, 7247). Alquiler de teodolito electrónico con tr |
| `br_nitrato_kg` | SIN_EQUIVALENTE | 37534 | 1 | 5,34 | 30,20 | 5,66 | Sin equivalente. Explosivo: emulsión explosiva en cartucho, kg. |
| `br_aditivo_kg` | SIN_EQUIVALENTE | 132 | 0.87 | 27,62 | 6,19 | 0,22 | Aditivo sin especificar. Aditivo plastificante para concreto (L); densidad supuesta 1,15 kg/L. |
| `br_luminaria_panel_led_24_de_sobreponer_pza` | SIN_EQUIVALENTE | 39385 | 1 | 37,66 | 9,10 | 0,24 | Sin panel LED de sobreponer. Plafón LED redondo de sobreponer 12/13 W (el SINAPI no tiene panel de 24 W). |
| `br_parketek_para_parket_l` | SIN_EQUIVALENTE | 10478 | 1 | 10,04 | 39,48 | 3,93 | Sin sellador de parquet en el SINAPI. Barniz PU para madera (el mismo del br_barniz_para_madera_l), L. |
| `br_masilla_eterglass_l` | SIN_EQUIVALENTE | 39433 | 1.6 | 16,95 | 4,51 | 0,27 | Masilla de poliéster con fibra (automotriz); sin equivalente. Idem. |
| `br_estructura_metalica_galvanizado_3d_m2` | SIN_EQUIVALENTE | 39427 | 2 | 32,64 | 9,04 | 0,28 | Estructura armada; no es un insumo del SINAPI. Estructura de cielo raso drywall: perfil canaleta C por m, ~2 m |
| `br_turba_m3` | SIN_EQUIVALENTE | 7253 | 1 | 67,80 | 235,71 | 3,48 | Sin equivalente. Tierra vegetal a granel, m³. |
| `br_masilla_etercoart_l` | SIN_EQUIVALENTE | 39433 | 1.6 | 15,69 | 4,51 | 0,29 | Idem. Masa de juntas lista (kg); 1 L ≈ 1,6 kg supuesto. |
| `br_guia_m` | SIN_EQUIVALENTE | 2762 | 1 | 4,39 | 14,21 | 3,24 | Sin especificar. Mecha: estopim simples, m. |
| `br_pavic_estandar_ceramico_20x10x6_5_cm_pza` | SIN_EQUIVALENTE | 36155 | 0.02 | 5,21 | 1,62 | 0,31 | Adoquín CERÁMICO: el SINAPI sólo tiene de concreto. Adoquín de CONCRETO 20×10 e = 6 cm por m²; 50 piezas/m² →  |

## DUDOSO más usados en el catálogo

| idCanonico | ArqOn | ítems | mejor candidato SINAPI | por qué es dudoso |
|---|---|---:|---|---|
| `br_chicotillo_pza` | Engate Flexível (Pza) | 6 | 6141 ENGATE/RABICHO FLEXIVEL PLASTICO (PVC OU ABS) BRANCO 1/2" X  (×1) | Flexible sin material/largo: PVC 1/2" × 30 cm (6141) o inox (11683). |
| `br_aditivo_acelerante_kg` | Aditivo Acelerador de Pega (Kg) | 5 | 124 ADITIVO ACELERADOR DE PEGA E ENDURECIMENTO PARA ARGAMASSAS E (×0.833) | Acelerador de fraguado sin cloruros (L); ArqOn en kg. Factor supuesto: densidad supuesta 1,2 kg/L. |
| `br_flotador_plastico_pza` | Boia Plástica (Pza) | 5 | 40329 TORNEIRA PLASTICA DE BOIA CONVENCIONAL PARA CAIXA DE AGUA, A (×1) | Válvula de boya plástica 3/4" (40329); diámetro no dicho. |
| `br_tirafondos_de_4_1_2x1_4_pza` | Parafuso Tirefond de 4 1/2X1/4″ (Pza) | 5 | 13294 PARAFUSO DE ACO ZINCADO, SEXTAVADO, COM ROSCA SOBERBA, DIAME (×1) | Tirafondo = parafuso sextavado rosca soberba; el SINAPI es 3/8" × 80 mm, no 1/4". |
| `br_arena_clasificada_m3` | Areia Classificada (m3) | 4 | 370 AREIA MEDIA - POSTO JAZIDA/FORNECEDOR (RETIRADO NA JAZIDA, S (×1) | «Clasificada» sin granulometría: arena media (370) o gruesa (367). |
| `br_bisagra_4_doble_pza` | Dobradiça 4″ Dupla (Pza) | 4 | 2432 DOBRADICA EM ACO/FERRO, 3 1/2" X 3", E= 1,9 A 2 MM, COM ANEL (×1) | El SINAPI no tiene 4" (3" y 3 1/2"). |
| `br_cold_rolled_channel_pza` | Canaleta Cold Rolled (Pza) | 4 | 39427 PERFIL CANALETA, FORMATO C, EM ACO ZINCADO, PARA ESTRUTURA F (×3) | Canal de cielo raso: el SINAPI tiene «perfil canaleta C 46×18 drywall» por m; el largo de la pieza ArqOn no está dicho ( |
| `br_malla_flex_construpanel_m` | Tela de Fibra de Vidro para Painel de EPS (m) | 4 | 36887 TELA DE FIBRA DE VIDRO, ACABAMENTO ANTI-ALCALINO, MALHA 10 X (×0.25) | Tela de fibra de vidrio antialcalina (m²); ArqOn por metro sin ancho. Factor supuesto: tira de malla de 25 cm de ancho s |
| `br_plastoform_100x40x16_p_vigueta_pza` | Bloco de EPS (Isopor) 100X40X16 para Vigota (Pza) | 4 | 39995 POLIESTIRENO EXPANDIDO/EPS (ISOPOR), TIPO 2F, BLOCO (×0.064) | Bloque EPS para vigueta ↔ EPS tipo 2F en bloque, m³ × 0,064 m³ (el bloque moldeado no es el mismo producto). |
| `br_sifon_de_pvc_pza` | Sifão de PVC (Pza) | 4 | 6149 SIFAO PLASTICO TIPO COPO PARA PIA OU LAVATORIO, 1 X 1.1/2" (×1) | Sifón plástico tipo vaso 1"×1 1/2" (6149) o extensible (20262). |
| `br_valvula_de_retencion_galvanizado_1_pza` | Válvula de Retenção Galvanizada 1″ (Pza) | 4 | 10418 VALVULA DE RETENCAO VERTICAL, DE BRONZE (PN-16), 1", 200 PSI (×1) | Retención 1" de bronce vertical (10418) u horizontal (10410); el ArqOn dice galvanizada. |
| `br_accesorios_galvanizado_1_2_pza` | Conexões Galvanizadas Ø 1/2″ (Pza) | 3 | 3455 COTOVELO 90 GRAUS DE FERRO GALVANIZADO, COM ROSCA BSP, DE 1/ (×1) | «Conexiones» mezcladas (codo/tee/cupla): candidato codo 90° 1/2" (3455). |
| `br_accesorios_galvanizado_3_4_pza` | Conexões Galvanizadas Ø 3/4″ (Pza) | 3 | 3456 COTOVELO 90 GRAUS DE FERRO GALVANIZADO, COM ROSCA BSP, DE 3/ (×1) | Idem 3/4" (codo 3456). |
| `br_calamina_ondulada_n_28_m2` | Telha Ondulada de Aço Zincado N° 28 (m2) | 3 | 25007 TELHA ONDULADA EM ACO ZINCADO, ALTURA DE 17 MM, ESPESSURA DE (×1) | N°28 ~0,4 mm ↔ telha ondulada zincada 0,50 mm. |
| `br_calamina_plana_n_28_m2` | Chapa Plana de Aço Zincado N° 28 (m2) | 3 | 11051 CHAPA DE ACO GALVANIZADA BITOLA GSG 26, E = 0,50 MM (4,00 KG (×4) | Chapa galvanizada plana: N°28 (~0,4 mm) está entre GSG 26 (0,50 mm, 4,0 kg/m², 11051) y GSG 30 (0,35 mm, 2,8 kg/m²). |
| `br_griferia_para_lavanderia_pza` | Torneira para Tanque (Pza) | 3 | 7603 TORNEIRA DE METAL AMARELO, PARA TANQUE / JARDIM, DE PAREDE,  (×1) | Canilla para tanque: metal amarillo (7603) o plástica (11831). |
| `br_llave_de_paso_cortina_galvanizado_1_pza` | Registro de Gaveta Galvanizado 1″ (Pza) | 3 | 6019 REGISTRO GAVETA BRUTO EM LATAO FORJADO, BITOLA 1" (×1) | El SINAPI es de latón (6019); ArqOn dice galvanizado. |
| `br_mezcladora_p_lavaplatos_bras_pza` | Misturador para Pia de Cozinha Bras. (Pza) | 3 | 11771 MISTURADOR DE PAREDE, DE METAL CROMADO, PARA COZINHA, BICA A (×1) | Mezclador de pared para cocina (11771); ArqOn sin tipo. |
| `br_niple_hexagonal_1_pza` | Niple Hexagonal 1″ (Pza) | 3 | 4179 NIPLE DE FERRO GALVANIZADO, COM ROSCA BSP, DE 1" (×1) | Niple sin material (en Bolivia suele ser galvanizado): galvanizado 1" (4179). |
| `br_picaporte_15_cm_pza` | Ferrolho 15 Cm (Pza) | 3 | 3120 FERROLHO COM FECHO / TRINCO REDONDO, EM ACO GALVANIZADO / ZI (×1) | Pestillo 6" (3120, redondo) o de porta-candado (3106). |
| `br_tacos_de_plastico_pza` | Buchas Plásticas (Pza) | 3 | 4376 BUCHA DE NYLON SEM ABA S8 (×1) | Taco de nylon sin medida: S8 (4376) o S6 (4375). |
| `br_tornillo_para_madera_pza` | Parafuso para Madeira (Pza) | 3 | 11057 PARAFUSO ROSCA SOBERBA ZINCADO CABECA CHATA FENDA SIMPLES 4, (×1) | Tornillo para madera sin medida; candidatos rosca soberba 4,8×40 (11057) o 4,2×32 (4377). Factor supuesto: pieza = pieza |
| `br_alambre_tejido_m2` | Tela de Arame (m2) | 2 | 10928 TELA DE ARAME GALVANIZADA QUADRANGULAR / LOSANGULAR, FIO 2,1 (×1) | Tela de alambre sin especificar; candidatos 14 BWG malla 8×8 (10928) o 5×5 (7167). |
| `br_bisagra_4_simple_pza` | Dobradiça 4″ Simples (Pza) | 2 | 2432 DOBRADICA EM ACO/FERRO, 3 1/2" X 3", E= 1,9 A 2 MM, COM ANEL (×1) | Idem. |
| `br_calamina_galvanizada_m2` | Telha Galvanizada (m2) | 2 | 25007 TELHA ONDULADA EM ACO ZINCADO, ALTURA DE 17 MM, ESPESSURA DE (×1) | Calamina sin calibre ↔ telha ondulada zincada 0,50 mm. |
| `br_cera_kg` | Cera (Kg) | 2 | 41967 CERA LIQUIDA INCOLOR MULTIPISO (×1) | Cera líquida multipiso en L; ArqOn cera en kg. |
| `br_chapa_exterior_p_puerta_metalica_pza` | Fechadura Externa para Porta Metálica (Pza) | 2 | 11484 FECHADURA DE SOBREPOR PARA PORTAO, EM ACO INOX COM ACABAMENT (×1) | Cerradura de sobreponer para portón (11484). |
| `br_chapa_exterior_pza` | Fechadura Externa (Pza) | 2 | 11480 FECHADURA AUXILIAR DE SEGURANCA PARA PORTA EXTERNA, EM ACO I (×1) | Cerradura exterior: el SINAPI tiene varias (11480 auxiliar de seguridad, etc.). |
| `br_chapa_interior_embutida_pza` | Fechadura Interna de Embutir (Pza) | 2 | 38153 FECHADURA ESPELHO PARA PORTA DE BANHEIRO, EM ACO INOX (MAQUI (×1) | Cerradura de embutir interna: candidato conjunto para puerta de baño (38153). |
| `br_costanera_100x50x13_3_mm_m` | Terça Perfil Ue 100X50X13 3 Mm (m) | 2 | 43083 PERFIL "U" ENRIJECIDO, EM CHAPA DOBRADA DE ACO LAMINADO, E = (×5.32) | Ue por kg: 100×50×13×3 = 5,32 kg/m calculado. |

## Sustituciones en recetas (insumos usados)

Para «sólo SINAPI»: el insumo ArqOn se reemplaza en la receta por el insumo SINAPI indicado; el coeficiente de la línea se multiplica por `factor` (1 unidad ArqOn = factor unidades SINAPI).

| insumo ArqOn | → SINAPI | factor | ítems afectados |
|---|---|---:|---|
| `br_accesorios_galvanizado_1_2_pza` Conexões Galvanizadas Ø 1/2″ (Pza) | 3455 COTOVELO 90 GRAUS DE FERRO GALVANIZADO, COM ROSCA BSP, DE 1/2" (UN) | 1 | IS018BR, IS021BR, IS023BR |
| `br_accesorios_galvanizado_1_pza` Conexões Galvanizadas Ø 1″ (Pza) | 3472 COTOVELO 90 GRAUS DE FERRO GALVANIZADO, COM ROSCA BSP, DE 1" (UN) | 1 | IS025BR |
| `br_accesorios_galvanizado_2_pza` Conexões Galvanizadas Ø 2″ (Pza) | 3471 COTOVELO 90 GRAUS DE FERRO GALVANIZADO, COM ROSCA BSP, DE 2" (UN) | 1 | IS020BR |
| `br_accesorios_galvanizado_3_4_pza` Conexões Galvanizadas Ø 3/4″ (Pza) | 3456 COTOVELO 90 GRAUS DE FERRO GALVANIZADO, COM ROSCA BSP, DE 3/4" (UN) | 1 | IS019BR, IS022BR, IS024BR |
| `br_aditivo_acelerante_kg` Aditivo Acelerador de Pega (Kg) | 124 ADITIVO ACELERADOR DE PEGA E ENDURECIMENTO PARA ARGAMASSAS E CONCRETOS (L) | 0.833 | OG015BR, OG016BR, OG017BR, OG059BR, OG060BR |
| `br_aditivo_kg` Aditivo (Kg) | 132 ADITIVO PLASTIFICANTE RETARDADOR DE PEGA E REDUTOR DE AGUA PARA CONCRE (L) | 0.87 | CR019BR, OG062BR, OG063BR |
| `br_alambre_tejido_m2` Tela de Arame (m2) | 10928 TELA DE ARAME GALVANIZADA QUADRANGULAR / LOSANGULAR, FIO 2,11 MM (14 B (M2) | 1 | AC003BR, CU019BR |
| `br_alquitran_kg` Alcatrão (Kg) | 510 ASFALTO MODIFICADO TIPO I - NBR 9910 (ASFALTO OXIDADO PARA IMPERMEABIL (KG) | 1 | OG019BR, OG030BR, OG045BR, OG052BR |
| `br_arena_clasificada_m3` Areia Classificada (m3) | 370 AREIA MEDIA - POSTO JAZIDA/FORNECEDOR (RETIRADO NA JAZIDA, SEM TRANSPO (M3) | 1 | OG066BR, OG067BR, OG068BR, OG069BR |
| `br_asfaltex_de_monopol_kg` Tinta Asfáltica Impermeabilizante (Kg) | 7313 TINTA ASFALTICA IMPERMEABILIZANTE DILUIDA EM SOLVENTE, PARA MATERIAIS  (L) | 1 | OG031BR |
| `br_bisagra_3_doble_pza` Dobradiça 3″ Dupla (Pza) | 2433 DOBRADICA EM ACO/FERRO, 3" X 2 1/2", E= 1,2 A 1,8 MM, SEM ANEL, CROMAD (UN) | 1 | CR008BR |
| `br_bisagra_4_doble_pza` Dobradiça 4″ Dupla (Pza) | 2432 DOBRADICA EM ACO/FERRO, 3 1/2" X 3", E= 1,9 A 2 MM, COM ANEL, CROMADO  (UN) | 1 | CR005BR, CR006BR, CR011BR, CR012BR |
| `br_bisagra_4_simple_pza` Dobradiça 4″ Simples (Pza) | 2432 DOBRADICA EM ACO/FERRO, 3 1/2" X 3", E= 1,9 A 2 MM, COM ANEL, CROMADO  (UN) | 1 | CR004BR, CR007BR |
| `br_bisagra_de_metal_pza` Dobradiça de Metal (Pza) | 2433 DOBRADICA EM ACO/FERRO, 3" X 2 1/2", E= 1,2 A 1,8 MM, SEM ANEL, CROMAD (UN) | 1 | CR015BR |
| `br_bisagra_te_pza` Dobradiça Tipo T (Pza) | 2432 DOBRADICA EM ACO/FERRO, 3 1/2" X 3", E= 1,9 A 2 MM, COM ANEL, CROMADO  (UN) | 1 | CR018BR |
| `br_bloque_de_hormigon_3h_e_15_cm_pza` Bloco de Concreto 3 Furos E=15 Cm (Pza) | 651 BLOCO DE VEDACAO DE CONCRETO 14 X 19 X 39 CM (CLASSE C - NBR 6136) (UN) | 1 | MP002BR |
| `br_bomba_hidroneumatica_1_5_hp_pza` Bomba Hidropneumática 1.5 HP (Pza) | 734 BOMBA CENTRIFUGA, MOTOR ELETRICO TRIFASICO 1,48HP DIAMETRO DE SUCCAO X (UN) | 1 | IS036BR, IS038BR |
| `br_bomba_hidroneumatica_2_hp_pza` Bomba Hidropneumática 2 HP (Pza) | 736 BOMBA CENTRIFUGA MOTOR ELETRICO TRIFASICO 2,96HP, DIAMETRO DE SUCCAO X (UN) | 1 | IS037BR |
| `br_brazo_hidraulico_p_puerta_pza` Mola Hidráulica para Porta (Pza) | 43604 MOLA HIDRAULICA AEREA, PARA PORTAS DE ATE 850 MM E PESO DE ATE 50 KG,  (UN) | 1 | CR003BR |
| `br_cable_coaxial_para_tv_m` Cabo Coaxial para TV (m) | 43833 CABO COAXIAL RG6 95% DE MALHA (M) | 1 | IE016BR |
| `br_cable_cu_para_telefono_2_x_22_m` Cabo de Cobre Telefônico 2 X 22 (m) | 11901 CABO TELEFONICO CCI 50, 1 PAR, USO INTERNO, SEM BLINDAGEM (M) | 1 | IE019BR |
| `br_cable_enchaquetado_3x2_5_mm_m` Cabo Multipolar 3x2.5 mm² (m) | 39258 CABO MULTIPOLAR DE COBRE, FLEXIVEL, CLASSE 4 OU 5, ISOLACAO EM HEPR, C (M) | 1 | IE023BR |
| `br_cable_ud_para_telefono_2_x_22_m` Cabo UD Telefônico 2 X 22 (m) | 11901 CABO TELEFONICO CCI 50, 1 PAR, USO INTERNO, SEM BLINDAGEM (M) | 1 | IE009BR |
| `br_cable_utp_4_pares_unifilar_m` Cabo UTP 4 Pares Rígido (m) | 43971 CABO DE REDE, PAR TRANCADO U/UTP, 4 PARES, CATEGORIA 5E (CAT 5E), ISOL (M) | 1 | IE015BR |
| `br_caja_interceptora_cemento_pza` Caixa Sifonada de Cimento (Pza) | 11712 CAIXA SIFONADA, PVC, 150 X 150 X 50 MM, COM GRELHA QUADRADA, BRANCA (N (UN) | 1 | IS027BR |
| `br_caja_interceptora_e_40_6_x30_cm_pza` Caixa Sifonada E-40 6″X30 Cm (Pza) | 11714 CAIXA SIFONADA, PVC, 150 X *185* X 75 MM, COM GRELHA QUADRADA, BRANCA (UN) | 1 | IS028BR |
| `br_caja_protector_termico_pza` Caixa para Disjuntor Termomagnético (Pza) | 39804 QUADRO DE DISTRIBUICAO, EM PVC, DE EMBUTIR, COM BARRAMENTO TERRA / NEU (UN) | 1 | IS038BR |
| `br_caja_receptora_pvc_8_x40_cm_pza` Caixa Receptora de PVC 8″X40 Cm (Pza) | 11714 CAIXA SIFONADA, PVC, 150 X *185* X 75 MM, COM GRELHA QUADRADA, BRANCA (UN) | 1 | IS030BR |
| `br_caja_sifonada_pvc_e_40_4_pza` Caixa Sifonada de PVC E-40 4″ (Pza) | 5103 CAIXA SIFONADA PVC, 100 X 100 X 50 MM, COM GRELHA REDONDA, BRANCA (UN) | 1 | IS029BR |
| `br_caja_sifonada_pvc_porta_rejilla_6_pza` Caixa Sifonada de PVC com Porta-Grelha 6″ (Pza) | 11712 CAIXA SIFONADA, PVC, 150 X 150 X 50 MM, COM GRELHA QUADRADA, BRANCA (N (UN) | 1 | AC039BR |
| `br_calamina_galvanizada_m2` Telha Galvanizada (m2) | 25007 TELHA ONDULADA EM ACO ZINCADO, ALTURA DE 17 MM, ESPESSURA DE 0,50 MM,  (M2) | 1 | OT001BR, UC001BR |
| `br_calamina_ondulada_de_policarbonato_m2` Telha Ondulada de Policarbonato (m2) | 7184 TELHA DE FIBRA DE VIDRO ONDULADA, TRANSLUCIDA / INCOLOR, E = *0,6* MM, (M2) | 1 | CU004BR |
| `br_calamina_ondulada_n_28_m2` Telha Ondulada de Aço Zincado N° 28 (m2) | 25007 TELHA ONDULADA EM ACO ZINCADO, ALTURA DE 17 MM, ESPESSURA DE 0,50 MM,  (M2) | 1 | CU002BR, CU008BR, OT040BR |
| `br_calamina_ondulada_n_33_m2` Telha Ondulada de Aço Zincado N° 33 (m2) | 25007 TELHA ONDULADA EM ACO ZINCADO, ALTURA DE 17 MM, ESPESSURA DE 0,50 MM,  (M2) | 1 | CU003BR |
| `br_calamina_plana_n_28_m2` Chapa Plana de Aço Zincado N° 28 (m2) | 11051 CHAPA DE ACO GALVANIZADA BITOLA GSG 26, E = 0,50 MM (4,00 KG/M2) (KG) | 4 | CU017BR, CU021BR, CU022BR |
| `br_callapos_de_3_m` Escora de Eucalipto Ø 3″ (m) | 2745 PONTALETE ROLICO SEM TRATAMENTO, D = 8 A 11 CM, H = 3 M, EM EUCALIPTO  (M) | 1 | OT031BR |
| `br_camara_de_inspeccion_pvc_sanear_pza` Caixa de Inspeção de PVC (Pza) | 41474 CAIXA DE INSPECAO PARA ATERRAMENTO OU OUTRO USO, EM PVC, DN = 300 X *3 (UN) | 1 | IS032BR |
| `br_camara_desgrasadora_pvc_sanear_pza` Caixa de Gordura de PVC (Pza) | 35277 CAIXA DE GORDURA EM PVC, DIAMETRO MINIMO 300 MM, DIAMETRO DE SAIDA 100 (UN) | 1 | IS034BR |
| `br_cantoneras_2l_4_x4_x3_8_m` Cantoneiras 2L (4″X4″X3/8″) (m) | 4777 CANTONEIRA ACO ABAS IGUAIS (QUALQUER BITOLA), ESPESSURA ENTRE 1/8" E 1 (KG) | 28.96 | OG071BR |
| `br_cemento_cola_facil_porcelanato_kg` Argamassa Colante para Porcelanato (Kg) | 37595 ARGAMASSA COLANTE TIPO AC III (KG) | 1 | AC030BR |
| `br_cera_kg` Cera (Kg) | 41967 CERA LIQUIDA INCOLOR MULTIPISO (L) | 1 | AC036BR, AC056BR |
| `br_chapa_exterior_p_puerta_metalica_pza` Fechadura Externa para Porta Metálica (Pza) | 11484 FECHADURA DE SOBREPOR PARA PORTAO, EM ACO INOX COM ACABAMENTO CROMADO, (UN) | 1 | CR011BR, CR012BR |
| `br_chapa_exterior_pza` Fechadura Externa (Pza) | 11480 FECHADURA AUXILIAR DE SEGURANCA PARA PORTA EXTERNA, EM ACO INOX, BROCA (CJ) | 1 | CR005BR, CR006BR |
| `br_chapa_interior_embutida_pza` Fechadura Interna de Embutir (Pza) | 38153 FECHADURA ESPELHO PARA PORTA DE BANHEIRO, EM ACO INOX (MAQUINA, TESTA  (CJ) | 1 | CR004BR, CR007BR |
| `br_chicotillo_pza` Engate Flexível (Pza) | 6141 ENGATE/RABICHO FLEXIVEL PLASTICO (PVC OU ABS) BRANCO 1/2" X 30 CM (UN) | 1 | IS005BR, IS013BR, IS084BR, IS085BR, IS086BR, IS088BR |
| `br_cinta_m` Fita (m) | 39431 FITA DE PAPEL MICROPERFURADO, 50 X 150 MM, PARA TRATAMENTO DE JUNTAS D (M) | 1 | MP012BR, MP013BR, MP014BR, MP015BR, MP020BR, MP021BR |
| `br_clavos_para_calamina_kg` Pregos para Telha (Kg) | 5069 PREGO DE ACO POLIDO COM CABECA 17 X 27 (2 1/2 X 11) (KG) | 1 | CU002BR, CU003BR, CU017BR |
| `br_cold_rolled_channel_pza` Canaleta Cold Rolled (Pza) | 39427 PERFIL CANALETA, FORMATO C, EM ACO ZINCADO, PARA ESTRUTURA FORRO DRYWA (M) | 3 | MP012BR, MP013BR, MP014BR, MP015BR |
| `br_costanera_100x50x13_3_mm_m` Terça Perfil Ue 100X50X13 3 Mm (m) | 43083 PERFIL "U" ENRIJECIDO, EM CHAPA DOBRADA DE ACO LAMINADO, E = 3,75 MM,  (KG) | 5.32 | CU023BR, CU024BR |
| `br_cubierta_de_platoform_e_50_mm_m` Telha Sanduíche com EPS E=50 Mm (m) | 39521 TELHA TERMOISOLANTE REVESTIDA EM ACO GALVANIZADO, FACE SUPERIOR EM TEL (M2) | 1 | CU014BR |
| `br_cubierta_de_poliuretano_e_50_mm_m2` Telha Sanduíche com Poliuretano E=50 Mm (m2) | 43071 TELHA TERMOISOLANTE REVESTIDA EM ACO GALVALUME, FACE SUPERIOR TRAPEZOI (M2) | 1 | CU016BR |
| `br_dinamita_pza` Dinamite (Pza) | 37534 EMULSAO EXPLOSIVA EM CARTUCHOS DE 1" X 12", DENSIDADE 1.15 G/CM3, INIC (KG) | 0.1 | OT021BR |
| `br_entablonado_madera_e_1_9_cm_m2` Assoalho de Madeira E=1.9 Cm (m2) | 3287 FORRO DE MADEIRA CUMARU/IPE CHAMPANHE OU EQUIVALENTE DA REGIAO, ENCAIX (M2) | 1 | AC033BR |
| `br_eq_estacion_total` Estação Total (Hr) | 7247 LOCACAO DE TEODOLITO ELETRONICO, PRECISAO ANGULAR DE 5 A 7 SEGUNDOS, I (H) | 1 | IS052BR |
| `br_estacas_de_madera_pza` Estacas de Madeira (Pza) | 4491 PONTALETE *7,5 X 7,5* CM EM PINUS, MISTA OU EQUIVALENTE DA REGIAO - BR (M) | 0.5 | IS052BR |
| `br_estiercol_de_ovino_kg` Esterco Ovino (Kg) | 38125 FERTILIZANTE ORGANICO COMPOSTO, CLASSE A (KG) | 1 | OT028BR |
| `br_estructura_metalica_galvanizado_3d_m2` Estrutura Metálica Galvanizada 3D (m2) | 39427 PERFIL CANALETA, FORMATO C, EM ACO ZINCADO, PARA ESTRUTURA FORRO DRYWA (M) | 2 | CU020BR |
| `br_flotador_automatico_pza` Boia Automática (Pza) | 7588 AUTOMATICO DE BOIA SUPERIOR / INFERIOR, *15* A / 250 V (UN) | 1 | IS039BR |
| `br_flotador_plastico_pza` Boia Plástica (Pza) | 40329 TORNEIRA PLASTICA DE BOIA CONVENCIONAL PARA CAIXA DE AGUA, AGUA FRIA,  (UN) | 1 | IS040BR, IS041BR, IS042BR, IS043BR, IS044BR |
| `br_foco_100_w_pza` Lâmpada 100 W (Pza) | 38194 LAMPADA LED 10 W BIVOLT BRANCA, FORMATO TRADICIONAL (BASE E27) (UN) | 1 | IE013BR |
| `br_foco_led_14_w_pza` Lâmpada LED 14 W (Pza) | 38194 LAMPADA LED 10 W BIVOLT BRANCA, FORMATO TRADICIONAL (BASE E27) (UN) | 1 | IE014BR |
| `br_gavion_colchoneta_4x2x0_3_m_m3` Gabião Tipo Colchão 4X2X0.3 M (m3) | 34383 GABIAO MANTA (COLCHAO) MALHA HEXAGONAL 6 X 8 CM (ZN/AL REVESTIDO COM P (UN) | 0.41667 | OG056BR |
| `br_gavion_maccaferri_2x1x0_5_con_d_m` Gabião Maccaferri 2X1X0.5 com Diafragma (m) | 11596 GABIAO TIPO CAIXA, MALHA HEXAGONAL 8 X 10 CM (ZN/AL), FIO 2,7 MM, DIME (UN) | 1 | OG058BR |
| `br_gravilla_1_2_t200_m3` Pedrisco 1/2″ T200 (m3) | 4720 PEDRA BRITADA N. 0, OU PEDRISCO (4,8 A 9,5 MM) POSTO PEDREIRA/FORNECED (M3) | 1 | OG041BR |
| `br_griferia_para_lavanderia_pza` Torneira para Tanque (Pza) | 7603 TORNEIRA DE METAL AMARELO, PARA TANQUE / JARDIM, DE PAREDE, SEM BICO,  (UN) | 1 | IS004BR, IS009BR, IS010BR |
| `br_griferia_para_urinario_pza` Válvula para Mictório (Pza) | 21112 VALVULA DE DESCARGA EM METAL CROMADO PARA MICTORIO COM ACIONAMENTO POR (UN) | 1 | IS013BR |
| `br_guia_m` Guia (m) | 2762 ESTOPIM SIMPLES (M) | 1 | OT021BR |
| `br_hidro_de_1_2_m` Tubo de Polipropileno (PPR) 1/2″ (m) | 36274 TUBO PPR PN 20, DN 20 MM, PARA AGUA QUENTE PREDIAL (M) | 1 | IS021BR |
| `br_hidro_de_3_4_m` Tubo de Polipropileno (PPR) 3/4″ (m) | 36278 TUBO PPR PN 20, DN 25 MM, PARA AGUA QUENTE PREDIAL (M) | 1 | IS022BR |
| `br_igol_primer_kg` Igol Primer (Kg) | 511 PRIMER PARA MANTA ASFALTICA A BASE DE ASFALTO MODIFICADO DILUIDO EM SO (L) | 1.11 | AC046BR |
| `br_impermeabilizante_asfaltico_kg` Impermeabilizante Asfáltico (Kg) | 626 MANTA LIQUIDA DE BASE ASFALTICA MODIFICADA COM A ADICAO DE ELASTOMEROS (KG) | 1 | UA007BR |
| `br_inodoro_blanco_tanq_bajo_con_acc_pza` Vaso Sanitário Branco com Caixa Acoplada e Acessórios (Pza) | 10422 BACIA SANITARIA (VASO) COM CAIXA ACOPLADA, SIFAO APARENTE, DE LOUCA BR (UN) | 1 | IS088BR |
| `br_interruptor_simple_pza` Interruptor Simples (Pza) | 38112 INTERRUPTOR SIMPLES 10A, 250V (APENAS MODULO) (UN) | 1 | IE001BR |
| `br_jabalina_de_cobre_80_cm_pza` Haste de Aterramento de Cobre 80 Cm (Pza) | 3379 HASTE DE ATERRAMENTO EM ACO COM 3,00 M DE COMPRIMENTO E DN = 5/8", REV (UN) | 1 | IE024BR |
| `br_jabon_liquido_l` Sabão Líquido (L) | 44329 DETERGENTE NEUTRO USO GERAL, CONCENTRADO (L) | 1 | OT040BR |
| `br_junta_de_dilatacion_m` Junta de Dilatação (m) | 3678 PERFIL ELASTOMERICO PRE-FORMADO EM EPMD, PARA JUNTA DE DILATACAO DE US (M) | 1 | OG071BR |
| `br_kikuyo_m2` Grama Kikuyu (m2) | 3324 GRAMA BATATAIS EM PLACAS, SEM PLANTIO (M2) | 1 | OT045BR |
| `br_ladrillo_6h_24x15x9_8_cm_rayado_pza` Bloco Cerâmico 6 Furos 24X15X9.8 Cm (Ranhurado) (Pza) | 44458 BLOCO CERAMICO / TIJOLO VAZADO PARA ALVENARIA DE VEDACAO, 6 FUROS NA H (UN) | 1 | MP008BR |
| `br_ladrillo_gambote_pza` Tijolo Maciço (Pza) | 7258 TIJOLO CERAMICO MACICO COMUM DE *5 X 10 X 20* CM (L X A X C) (UN) | 1 | IE023BR |
| `br_lamina_sika_con_aluminio_m2` Manta Asfáltica Sika com Alumínio (m2) | 11621 MANTA ASFALTICA ELASTOMERICA EM POLIESTER ALUMINIZADA 3 MM, TIPO III,  (M2) | 1 | AC046BR |
| `br_lampara_tortuga_18w_pza` Arandela Tipo Tartaruga 18W (Pza) | 38775 LUMINARIA TIPO TARTARUGA PARA AREA EXTERNA EM ALUMINIO, COM GRADE, PAR (UN) | 1 | IE025BR |
| `br_lavadero_de_fierro_enlosado_pza` Tanque de Lavar de Ferro Esmaltado (Pza) | 11690 TANQUE SIMPLES EM MARMORE SINTETICO DE FIXAR NA PAREDE, CAPACIDADE *22 (UN) | 1 | IS004BR |
| `br_lavamanos_blanco_con_acc_pza` Lavatório Branco com Acessórios (Pza) | 10426 LAVATORIO DE LOUCA BRANCA, COM COLUNA, DIMENSOES *54 X 44* CM (L X C) (UN) | 1 | IS005BR |
| `br_lavaplatos_1_depos_1_fregadero_pza` Pia de Cozinha 1 Cuba 1 Escorredor (Pza) | 1746 BANCADA/BANCA/PIA DE ACO INOXIDAVEL (AISI 430) COM 1 CUBA CENTRAL, COM (UN) | 1 | IS006BR |
| `br_lavaplatos_2_depos_1_fregadero_pza` Pia de Cozinha 2 Cubas 1 Escorredor (Pza) | 1750 BANCADA/BANCA/PIA DE ACO INOXIDAVEL (AISI 430) COM 2 CUBAS, COM VALVUL (UN) | 1 | IS007BR |
| `br_lavaplatos_2_depos_2_fregaderos_pza` Pia de Cozinha 2 Cubas 2 Escorredores (Pza) | 1750 BANCADA/BANCA/PIA DE ACO INOXIDAVEL (AISI 430) COM 2 CUBAS, COM VALVUL (UN) | 1 | IS008BR |
| `br_lavarropa_de_cemento_2_depositos_pza` Tanque de Lavar Roupa de Cimento 2 Cubas (Pza) | 36790 TANQUE DUPLO EM MARMORE SINTETICO COM CUBA LISA E ESFREGADOR, *110 X 6 (UN) | 1 | IS010BR |
| `br_lavarropa_de_cemento_pza` Tanque de Lavar Roupa de Cimento (Pza) | 11690 TANQUE SIMPLES EM MARMORE SINTETICO DE FIXAR NA PAREDE, CAPACIDADE *22 (UN) | 1 | IS009BR |
| `br_lija_para_cubierta_hoja` Lixa para Cobertura (Hoja) | 3768 LIXA EM FOLHA PARA FERRO, NUMERO 150 (UN) | 1 | CU026BR |
| `br_llave_de_paso_cortina_galvanizado_1_pza` Registro de Gaveta Galvanizado 1″ (Pza) | 6019 REGISTRO GAVETA BRUTO EM LATAO FORJADO, BITOLA 1" (UN) | 1 | IS017BR, IS038BR, IS039BR |
| `br_loseta_hexagonal_10_cm_pza` Piso Intertravado Hexagonal 10 Cm (Pza) | 679 BLOQUETE/PISO INTERTRAVADO DE CONCRETO - MODELO SEXTAVADO / HEXAGONAL, (M2) | 0.05 | OG050BR |
| `br_loseta_ondulada_10_cm_m2` Piso Intertravado Ondulado 10 Cm (m2) | 40524 BLOQUETE/PISO INTERTRAVADO DE CONCRETO - MODELO ONDA/16 FACES/RETANGUL (M2) | 1 | OG051BR |
| `br_luminaria_panel_led_24_de_sobreponer_pza` Luminária Painel LED 24 de Sobrepor (Pza) | 39385 LUMINARIA LED PLAFON REDONDO DE SOBREPOR BIVOLT 12/13 W, D = *17* CM (UN) | 1 | IE026BR |
| `br_luminaria_pantalla_2x20_w_led_pza` Luminária de Calha 2X20 W LED (Pza) | 38784 LUMINARIA DE SOBREPOR EM CHAPA DE ACO COM ALETAS PLASTICAS, PARA 2 LAM (UN) | 1 | IE004BR |
| `br_luminaria_spot_embutir_16w_led_pza` Luminária Spot de Embutir 16W LED (Pza) | 12266 LUMINARIA SPOT DE SOBREPOR EM ALUMINIO COM ALETA PLASTICA PARA 1 LAMPA (UN) | 1 | IE005BR |
| `br_luminaria_tipo_farola_led_80w_clase_ii_pza` Luminária Pública LED 80W Classe II (Pza) | 42246 LUMINARIA DE LED PARA ILUMINACAO PUBLICA, DE 68 W ATE 97 W, INVOLUCRO  (UN) | 1 | IE023BR |
| `br_machihembre_cedro_p2` Tábua Macho-Fêmea de Cedro (p2) | 3287 FORRO DE MADEIRA CUMARU/IPE CHAMPANHE OU EQUIVALENTE DA REGIAO, ENCAIX (M2) | 0.0929 | AC014BR, AC035BR |
| `br_machihembre_palo_maria_p2` Tábua Macho-Fêmea de Guanandi (p2) | 3287 FORRO DE MADEIRA CUMARU/IPE CHAMPANHE OU EQUIVALENTE DA REGIAO, ENCAIX (M2) | 0.0929 | AC001BR |
| `br_madera_palo_maria_p2` Madeira Guanandi (p2) | 4006 MADEIRA SERRADA EM PINUS, MISTA OU EQUIVALENTE DA REGIAO - BRUTA (M3) | 0.00236 | AC069BR |
| `br_malla_alambre_7x7_cm_12_m2` Tela de Arame 7X7 Cm #12 (m2) | 10927 TELA DE ARAME GALVANIZADA QUADRANGULAR / LOSANGULAR, FIO 2,77 MM (12 B (M2) | 1 | OT032BR |
| `br_malla_alambre_galvanizado_7x7_cm_12_m2` Tela de Arame Galvanizado 7X7 Cm #12 (m2) | 10927 TELA DE ARAME GALVANIZADA QUADRANGULAR / LOSANGULAR, FIO 2,77 MM (12 B (M2) | 1 | CR018BR, OT033BR |
| `br_malla_flex_construpanel_m` Tela de Fibra de Vidro para Painel de EPS (m) | 36887 TELA DE FIBRA DE VIDRO, ACABAMENTO ANTI-ALCALINO, MALHA 10 X 10 MM (M2) | 0.25 | MP016BR, MP017BR, MP018BR, MP019BR |
| `br_marco_2_x_4_cedro_pza` Batente 2″ X 4″ de Cedro (Pza) | 183 BATENTE / PORTAL / ADUELA / MARCO EM MADEIRA MACICA COM REBAIXO, E = * (JG) | 1 | CR006BR |
| `br_marco_3_x_2_cedro_pza` Batente 3″ X 2″ de Cedro (Pza) | 183 BATENTE / PORTAL / ADUELA / MARCO EM MADEIRA MACICA COM REBAIXO, E = * (JG) | 1 | CR004BR |
| `br_marco_4_x_2_cedro_pza` Batente 4″ X 2″ de Cedro (Pza) | 183 BATENTE / PORTAL / ADUELA / MARCO EM MADEIRA MACICA COM REBAIXO, E = * (JG) | 1 | CR005BR, CR007BR |
| `br_marmol_travertino_nacional_m2` Mármore Travertino Nacional (m2) | 4818 PISO/ REVESTIMENTO EM MARMORE, POLIDO, BRANCO COMUM, FORMATO MENOR OU  (M2) | 1 | AC027BR, CR017BR |
| `br_masilla_etercoart_l` Massa Plástica de Poliéster (L) | 39433 MASSA DE REJUNTE PRONTA PARA TRATAMENTO DE JUNTAS DE CHAPA DE GESSO PA (KG) | 1.6 | MP020BR, MP021BR |
| `br_masilla_eterglass_l` Massa Plástica com Fibra de Vidro (L) | 39433 MASSA DE REJUNTE PRONTA PARA TRATAMENTO DE JUNTAS DE CHAPA DE GESSO PA (KG) | 1.6 | MP020BR, MP021BR |
| `br_medidor_de_agua_pza` Hidrômetro (Pza) | 12769 HIDROMETRO UNIJATO / MEDIDOR DE AGUA, DN 1/2", VAZAO MAXIMA DE 1,5 M3/ (UN) | 1 | IS014BR |
| `br_membrana_geotextil_aluminio_3_5_mm_m2` Manta Asfáltica Geotêxtil com Alumínio 3.5 Mm (m2) | 11621 MANTA ASFALTICA ELASTOMERICA EM POLIESTER ALUMINIZADA 3 MM, TIPO III,  (M2) | 1 | AC047BR |
| `br_membrana_liquida_impermeabilizante_l` Membrana Líquida Impermeabilizante (L) | 43147 MEMBRANA IMPERMEABILIZANTE ACRILICA MONOCOMPONENTE (KG) | 1.3 | CU025BR |
| `br_mezclador_y_transf_p_ducha_pza` Misturador e Desviador para Chuveiro (Pza) | 36800 MISTURADOR METALICO, BASE PARA CHUVEIRO/BANHEIRA, 1/2" OU 3/4", SOLDAV (UN) | 1 | IS087BR |
| `br_mezcladora_p_lavamanos_bras_pza` Misturador para Lavatório Bras. (Pza) | 11769 MISTURADOR DE METAL CROMADO, DE MESA/BANCADA, COM BICA BAIXA, PARA LAV (UN) | 1 | IS005BR |
| `br_mezcladora_p_lavaplatos_bras_pza` Misturador para Pia de Cozinha Bras. (Pza) | 11771 MISTURADOR DE PAREDE, DE METAL CROMADO, PARA COZINHA, BICA ALTA MOVEL, (UN) | 1 | IS006BR, IS007BR, IS008BR |
| `br_mosaico_marmolado_40x40_cm_m2` Ladrilho Marmorizado 40X40 Cm (m2) | 38138 LADRILHO HIDRAULICO, *30 X 30* CM, E= 2 CM, PADRAO MILANO, COR NATURAL (M2) | 1 | AC028BR |
| `br_niple_hexagonal_1_pza` Niple Hexagonal 1″ (Pza) | 4179 NIPLE DE FERRO GALVANIZADO, COM ROSCA BSP, DE 1" (UN) | 1 | IS017BR, IS036BR, IS037BR |
| `br_niple_hexagonal_3_4_pza` Niple Hexagonal 3/4″ (Pza) | 4178 NIPLE DE FERRO GALVANIZADO, COM ROSCA BSP, DE 3/4" (UN) | 1 | IS036BR, IS037BR |
| `br_nitrato_kg` Nitrato (Kg) | 37534 EMULSAO EXPLOSIVA EM CARTUCHOS DE 1" X 12", DENSIDADE 1.15 G/CM3, INIC (KG) | 1 | OT021BR |
| `br_parket_tajibo_m2` Parquete de Ipê (m2) | 6214 TACO DE MADEIRA PARA PISO, IPE (CERNE) OU EQUIVALENTE DA REGIAO, 7 X 4 (M2) | 1 | AC036BR |
| `br_parketek_para_parket_l` Selador para Parquete (L) | 10478 VERNIZ A BASE RESINA ALQUIDICA COM POLIURETANO PARA MADEIRA, COM FILTR (L) | 1 | AC036BR |
| `br_pavic_estandar_ceramico_20x10x6_5_cm_pza` Piso Cerâmico Intertravado (Paver) 20X10X6.5 Cm (Pza) | 36155 BLOQUETE/PISO INTERTRAVADO DE CONCRETO - MODELO ONDA/16 FACES/RETANGUL (M2) | 0.02 | OG053BR |
| `br_pegaladrillo_facil_kg` Argamassa para Assentamento de Tijolos (Kg) | 371 ARGAMASSA INDUSTRIALIZADA MULTIUSO, PARA REVESTIMENTO INTERNO E EXTERN (KG) | 1 | MP006BR |
| `br_pegamento_para_alfombras_l` Cola para Carpetes (L) | 4791 ADESIVO ACRILICO DE BASE AQUOSA / COLA DE CONTATO (KG) | 1 | AC063BR, AC064BR |
| `br_pegamento_para_ladrillo_valkure_kg_kg` Argamassa Colante para Tijolos (Kg) | 371 ARGAMASSA INDUSTRIALIZADA MULTIUSO, PARA REVESTIMENTO INTERNO E EXTERN (KG) | 1 | MP008BR |
| `br_pegamento_para_vinil_l` Cola para Piso Vinílico (L) | 4791 ADESIVO ACRILICO DE BASE AQUOSA / COLA DE CONTATO (KG) | 1 | AC031BR |
| `br_perfil_montante_de_0_70x2_40_m_m` Perfil Montante 0.70X2.40 M (m) | 39423 PERFIL MONTANTE, FORMATO C, EM ACO ZINCADO, PARA ESTRUTURA PAREDE DRYW (M) | 1 | MP020BR, MP021BR |
| `br_perfil_solera_de_0_70x3_00_m_m` Perfil Guia 0.70X3.00 M (m) | 39420 PERFIL GUIA, FORMATO U, EM ACO ZINCADO, PARA ESTRUTURA PAREDE DRYWALL, (M) | 1 | MP020BR, MP021BR |
| `br_perfil_tee_1_x_1_8_m` Perfil Tê 1″ X 1/8″ (m) | 567 CANTONEIRA (ABAS IGUAIS) EM ACO CARBONO, 25,4 MM X 3,17 MM (L X E), 1, (M) | 1 | CR015BR |
| `br_perfil_u_de_aluminio_m` Perfil U de Alumínio (m) | 11552 PERFIL EM ALUMINIO, FORMATO U, ABAS IGUAIS, LARGURA DE 12,70 MM (1/2 P (M) | 1 | AC057BR, CR010BR |
| `br_perno_3_8_x_4_con_arandela_pza` Parafuso 3/8″ x 4 com Arruela (Pza) | 13294 PARAFUSO DE ACO ZINCADO, SEXTAVADO, COM ROSCA SOBERBA, DIAMETRO 3/8",  (UN) | 1 | IE023BR |
| `br_perno_de_expansion_pza` Chumbador de Expansão (Pza) | 44179 CHUMBADOR TIPO BOLT FWA, PARABOLT PBA OU PARABOLT PBC, EM ACO ZINCADO, (UN) | 1 | CU008BR, CU010BR |
| `br_picaporte_15_cm_pza` Ferrolho 15 Cm (Pza) | 3120 FERROLHO COM FECHO / TRINCO REDONDO, EM ACO GALVANIZADO / ZINCADO, DE  (UN) | 1 | CR008BR, CR011BR, CR012BR |
| `br_piedra_pizarra_cortada_15x30_cm_m2` Pedra Ardósia Cortada 15X30 Cm (m2) | 4704 PEDRA ARDOSIA, CINZA, 20 X 40 CM, E= *1 CM (M2) | 1 | AC013BR |
| `br_piedra_tarija_m2` Pedra São Tomé (m2) | 4712 PEDRA QUARTZITO OU CALCARIO LAMINADO, CACO, TIPO CARIRI, ITACOLOMI, LA (M2) | 1 | AC037BR |
| `br_pintura_latex_exterior_l` Tinta Látex para Exterior (L) | 35692 TINTA LATEX ACRILICA STANDARD, COR BRANCA (L) | 1 | UA005BR |
| `br_pintura_latex_satinado_l` Tinta Látex Acetinada (L) | 35692 TINTA LATEX ACRILICA STANDARD, COR BRANCA (L) | 1 | AC052BR |
| `br_pintura_super_latex_gal` Tinta Super Látex (L) | 35692 TINTA LATEX ACRILICA STANDARD, COR BRANCA (L) | 1 | AC067BR |
| `br_pisopak_30x30cmx1_6_mm_m2` Piso Vinílico em Placas 30X30 Cm X 1.6 Mm (m2) | 4790 PLACA VINILICA SEMIFLEXIVEL PARA REVESTIMENTO DE PISOS E PAREDES, E =  (M2) | 1 | AC031BR |
| `br_placa_drywall_10_mm_1_2x2_4_m_pza` Placa de Drywall 10 Mm 1.2X2.4 M (Pza) | 39413 PLACA / CHAPA DE GESSO ACARTONADO, STANDARD (ST), COR BRANCA, E = 12,5 (M2) | 2.88 | CU020BR |
| `br_placa_ondulada_duralit_m2` Telha Ondulada de Fibrocimento (m2) | 7194 TELHA DE FIBROCIMENTO ONDULADA E = 6 MM, DE 2,44 X 1,10 M (SEM AMIANTO (M2) | 1 | CU009BR |
| `br_placas_cementicias_de_eter_board_8_mm_pza` Placa Cimentícia 8 Mm (Pza) | 11062 PLACA CIMENTICIA LISA E = 10 MM, DE 1,20 X *2,50* M (SEM AMIANTO) (M2) | 2.977 | MP020BR, MP021BR |
| `br_placas_durlock_12_50_mm_pza` Placa de Gesso Acartonado (Drywall) 12.50 Mm (Pza) | 39413 PLACA / CHAPA DE GESSO ACARTONADO, STANDARD (ST), COR BRANCA, E = 12,5 (M2) | 2.88 | MP014BR, MP015BR |
| `br_plancha_de_acero_5_16_8mm_hoja` Chapa de Aço 5/16″ (8mm) (Hoja) | 1332 CHAPA DE ACO GROSSA, ASTM A36, E = 3/8" (9,53 MM) 74,69 KG/M2 (KG) | 187 | IE023BR |
| `br_plancha_de_hierro_1_16_hoja` Chapa de Ferro 1/16″ (Hoja) | 1322 CHAPA DE ACO FINA A QUENTE BITOLA MSG 16, E = 1,50 MM (12,00 KG/M2) (KG) | 35.72 | CR011BR, CR012BR |
| `br_plancha_metalica_10mm_m2` Chapa Metálica 10mm (m2) | 1332 CHAPA DE ACO GROSSA, ASTM A36, E = 3/8" (9,53 MM) 74,69 KG/M2 (KG) | 74.69 | IE023BR |
| `br_plancha_metalica_1_4_2x1_m_pza` Chapa Metálica 1/4″ 2X1 M (Pza) | 1330 CHAPA DE ACO GROSSA, ASTM A36, E = 1/4" (6,35 MM) 49,79 KG/M2 (KG) | 99.58 | OT009BR |
| `br_plaqueta_tv_conector_spliter_pza` Placa com Tomada de TV e Splitter (Pza) | 38084 TOMADA PARA ANTENA DE TV, CABO COAXIAL DE 9 MM, CONJUNTO MONTADO PARA  (UN) | 1 | IE016BR |
| `br_plastoform_100x40x16_p_vigueta_pza` Bloco de EPS (Isopor) 100X40X16 para Vigota (Pza) | 39995 POLIESTIRENO EXPANDIDO/EPS (ISOPOR), TIPO 2F, BLOCO (M3) | 0.064 | OG021BR, OG022BR, OG023BR, OG024BR |
| `br_plastoformo_5mm_pza` Placa de EPS (Isopor) 5mm (Pza) | 11615 POLIESTIRENO EXPANDIDO/EPS (ISOPOR), TIPO 2F, PLACA, ISOLAMENTO TERMOA (M2) | 0.5 | OG076BR |
| `br_politubo_3_4_m` Mangueira de Polietileno 3/4″ (m) | 9813 TUBO DE POLIETILENO DE ALTA DENSIDADE (PEAD), PE-80, DE = 20 MM X 2,3  (M) | 1 | IE023BR, IE024BR |
| `br_poste_de_hormigon_pretensado_m` Poste de Concreto Protendido (m) | 4102 MOURAO DE CONCRETO RETO, SECAO QUADRADA, *10 X 10* CM, H= 3,00 M (UN) | 0.3333 | OT032BR |
| `br_puerta_moldeada_ext_hdf_pza` Porta Moldada Externa de HDF (Pza) | 4989 PORTA DE ABRIR / GIRO, DE MADEIRA FOLHA MEDIA (NBR 15930) DE 1000 X 21 (UN) | 1 | CR006BR |
| `br_puerta_moldeada_int_hdf_pza` Porta Moldada Interna de HDF (Pza) | 4987 PORTA DE ABRIR / GIRO, DE MADEIRA FOLHA MEDIA (NBR 15930) DE 900 X 210 (UN) | 1 | CR007BR |
| `br_puerta_tablero_cedro_0_80x2_10_m_pza` Porta Almofadada de Cedro 0.80X2.10 M (Pza) | 4992 PORTA DE ABRIR / GIRO, DE MADEIRA FOLHA MEDIA (NBR 15930) DE 800 X 210 (UN) | 1 | CR004BR |
| `br_puerta_tablero_exterior_pza` Porta Almofadada Externa (Pza) | 4989 PORTA DE ABRIR / GIRO, DE MADEIRA FOLHA MEDIA (NBR 15930) DE 1000 X 21 (UN) | 1 | CR005BR |
| `br_rejilla_de_piso_20x20_cm_bronce_pza` Grelha de Piso 20X20 Cm em Bronze (Pza) | 11234 RALO FOFO COM REQUADRO, QUADRADO 200 X 200 MM (UN) | 1 | AC038BR |
| `br_rejilla_de_piso_6_bronce_pza` Grelha de Piso 6″ em Bronze (Pza) | 11732 GRELHA FIXA, PVC CROMADA, REDONDA, 150 MM, PARA RALOS E CAIXAS (UN) | 1 | AC039BR |
| `br_revoque_fino_facil_kg` Argamassa para Reboco Fino (Kg) | 371 ARGAMASSA INDUSTRIALIZADA MULTIUSO, PARA REVESTIMENTO INTERNO E EXTERN (KG) | 1 | AC015BR |
| `br_sellador_para_madera_l` Selador para Madeira (L) | 10478 VERNIZ A BASE RESINA ALQUIDICA COM POLIURETANO PARA MADEIRA, COM FILTR (L) | 1 | AC055BR |
| `br_sifon_de_pvc_pza` Sifão de PVC (Pza) | 6149 SIFAO PLASTICO TIPO COPO PARA PIA OU LAVATORIO, 1 X 1.1/2" (UN) | 1 | IS004BR, IS005BR, IS009BR, IS010BR |
| `br_sika_1_impermeabilizante_kg` Sika 1 Impermeabilizante (Kg) | 123 ADITIVO IMPERMEABILIZANTE DE PEGA NORMAL PARA ARGAMASSAS E CONCRETOS S (L) | 0.952 | AC018BR |
| `br_sikadur_32_kg` Sikadur 32 (Kg) | 156 ADESIVO ESTRUTURAL A BASE DE RESINA EPOXI, BICOMPONENTE, FLUIDO (KG) | 1 | OG012BR |
| `br_socket_pza` Soquete (Pza) | 12295 SOQUETE DE BAQUELITE BASE E27, PARA LAMPADAS (UN) | 1 | IE013BR, IE014BR |
| `br_soldadura_para_calamina_kg` Solda para Telha (Kg) | 13388 SOLDA EM BARRA DE ESTANHO-CHUMBO 50/50 (KG) | 1 | CU021BR, CU022BR |
| `br_superlatex_acrilico_l` Tinta Super Látex Acrílica (L) | 7356 TINTA LATEX ACRILICA PREMIUM, COR BRANCO FOSCO (L) | 1 | AC050BR |
| `br_supertubo_hdpe_110_mm_4_m` Tubo de PEAD 110 Mm (4″) (m) | 44526 TUBO DE POLIETILENO DE ALTA DENSIDADE, PEAD, PE-80, DE = 110 MM X 10,0 (M) | 1 | IS066BR |
| `br_supertubo_hdpe_160_mm_6_pn6_m` Tubo de PEAD 160 Mm (6″) PN6 (m) | 44545 TUBO DE POLIETILENO DE ALTA DENSIDADE, PEAD, PE-80, DE = 160 MM X 14,6 (M) | 1 | IS068BR |
| `br_supertubo_hdpe_200_mm_8_pn6_m` Tubo de PEAD 200 Mm (8″) PN6 (m) | 44547 TUBO DE POLIETILENO DE ALTA DENSIDADE, PEAD, PE-80, DE= 200 MM X 18,2  (M) | 1 | IS069BR |
| `br_supertubo_hdpe_50_mm_1_1_2_m` Tubo de PEAD 50 Mm (1 1/2″) (m) | 44521 TUBO DE POLIETILENO DE ALTA DENSIDADE, PEAD, PE-80, DE= 50 MM X 4,6 MM (M) | 1 | IS062BR |
| `br_supertubo_hdpe_75_mm_2_1_2_m` Tubo de PEAD 75 Mm (2 1/2″) (m) | 44524 TUBO DE POLIETILENO DE ALTA DENSIDADE, PEAD, PE-80, DE= 75 MM X 6,9 MM (M) | 1 | IS064BR |
| `br_tacos_de_plastico_pza` Buchas Plásticas (Pza) | 4376 BUCHA DE NYLON SEM ABA S8 (UN) | 1 | AC001BR, AC014BR, AC042BR |
| `br_tanque_plastico_10_000_lt_con_acc_pza` Reservatório Plástico 10 000 L com Acessórios (Pza) | 37106 CAIXA D'AGUA / RESERVATORIO EM POLIESTER REFORCADO COM FIBRA DE VIDRO, (UN) | 1 | IS044BR |
| `br_tanque_plastico_1200_lt_con_acc_pza` Caixa d'Água Plástica 1200 L com Acessórios (Pza) | 34639 CAIXA D'AGUA / RESERVATORIO EM POLIETILENO, 1500 LITROS, COM TAMPA (UN) | 1 | IS041BR |
| `br_tanque_plastico_2300_lt_con_acc_pza` Caixa d'Água Plástica 2300 L com Acessórios (Pza) | 34640 CAIXA D'AGUA / RESERVATORIO EM POLIETILENO, 2000 LITROS, COM TAMPA (UN) | 1 | IS042BR |
| `br_tanque_plastico_5000_lt_con_acc_pza` Caixa d'Água Plástica 5000 L com Acessórios (Pza) | 37105 CAIXA D'AGUA / RESERVATORIO EM POLIESTER REFORCADO COM FIBRA DE VIDRO, (UN) | 1 | IS043BR |
| `br_tanque_plastico_600_lt_con_acc_pza` Caixa d'Água Plástica 600 L com Acessórios (Pza) | 34638 CAIXA D'AGUA / RESERVATORIO EM POLIETILENO, 750 LITROS, COM TAMPA (UN) | 1 | IS040BR |
| `br_teja_espanola_ceramica_pza` Telha Espanhola Cerâmica (Pza) | 7175 TELHA DE BARRO / CERAMICA, NAO ESMALTADA, TIPO ROMANA, AMERICANA, PORT (UN) | 1 | CU012BR |
| `br_teja_espanola_color_duralit_m2` Telha Espanhola Colorida de Fibrocimento (m2) | 7194 TELHA DE FIBROCIMENTO ONDULADA E = 6 MM, DE 2,44 X 1,10 M (SEM AMIANTO (M2) | 1 | CU013BR |
| `br_tepe_m2` Tepe (m2) | 3324 GRAMA BATATAIS EM PLACAS, SEM PLANTIO (M2) | 1 | OT028BR |
| `br_terminales_para_cable_utp_pza` Conectores para Cabo UTP (Pza) | 39602 CONECTOR MACHO RJ 45, CATEGORIA 5 E (CAT 5E) PARA CABOS (UN) | 1 | IE015BR |
| `br_tierra_cernida_m3` Terra Peneirada (m3) | 366 AREIA FINA - POSTO JAZIDA/FORNECEDOR (RETIRADO NA JAZIDA, SEM TRANSPOR (M3) | 1 | IS071BR |
| `br_tierra_comun_m3` Terra Comum (m3) | 368 AREIA PARA ATERRO - POSTO JAZIDA/FORNECEDOR (RETIRADO NA JAZIDA, SEM T (M3) | 1 | OT025BR |
| `br_timbre_pulsador_con_campanilla_pza` Campainha com Botão (Pza) | 38085 CAMPAINHA CIGARRA 127 V / 220 V, CONJUNTO MONTADO PARA EMBUTIR 4" X 2" (UN) | 1 | IE009BR |
| `br_tirafondos_de_4_1_2x1_4_pza` Parafuso Tirefond de 4 1/2X1/4″ (Pza) | 13294 PARAFUSO DE ACO ZINCADO, SEXTAVADO, COM ROSCA SOBERBA, DIAMETRO 3/8",  (UN) | 1 | CU004BR, CU005BR, CU014BR, CU015BR, CU016BR |
| `br_tirafondos_de_5_1_2x1_4_pza` Parafuso Tirefond de 5 1/2X1/4″ (Pza) | 13294 PARAFUSO DE ACO ZINCADO, SEXTAVADO, COM ROSCA SOBERBA, DIAMETRO 3/8",  (UN) | 1 | CU013BR |
| `br_tirafondos_pza` Parafusos Tirefond (Pza) | 13294 PARAFUSO DE ACO ZINCADO, SEXTAVADO, COM ROSCA SOBERBA, DIAMETRO 3/8",  (UN) | 1 | IS086BR |
| `br_tornillo_con_aleta_autoavellante_pza` Parafuso Autoatarraxante com Aleta (Pza) | 39443 PARAFUSO DRY WALL, EM ACO ZINCADO, CABECA LENTILHA E PONTA BROCA (LB), (UN) | 1 | MP020BR, MP021BR |
| `br_tornillo_hexagonal_pza` Parafuso Sextavado (Pza) | 13294 PARAFUSO DE ACO ZINCADO, SEXTAVADO, COM ROSCA SOBERBA, DIAMETRO 3/8",  (UN) | 1 | CU008BR, CU010BR |
| `br_tornillo_para_madera_pza` Parafuso para Madeira (Pza) | 11057 PARAFUSO ROSCA SOBERBA ZINCADO CABECA CHATA FENDA SIMPLES 4,8 X 40 MM  (UN) | 1 | AC001BR, AC014BR, AC042BR |
| `br_transformador_trifasico_150_kva_10_5_kv_380_220v_pza` Transformador Trifásico 150 KVA 10.5 KV 380/220V (Pza) | 7614 TRANSFORMADOR TRIFASICO DE DISTRIBUICAO, POTENCIA DE 150 KVA, TENSAO N (UN) | 1 | IE022BR |
| `br_tuberia_pvc_1_2_m` Tubo de PVC 1/2" (m) | 9856 TUBO PVC, ROSCAVEL, 1/2", AGUA FRIA PREDIAL (M) | 1 | IS001BR |
| `br_tuberia_pvc_4_m` Tubo de PVC 4" (m) | 9836 TUBO PVC SERIE NORMAL, DN 100 MM, PARA ESGOTO PREDIAL (NBR 5688) (M) | 1 | IS002BR |
| `br_tuberia_pvc_clase_9_3_con_junta_m` Tubo de PVC Classe 9 Ø 3″ com Junta (m) | 36373 TUBO PVC PBA JEI, CLASSE 12, DN 75 MM, PARA REDE DE AGUA (NBR 5647) (M) | 1 | IS053BR |
| `br_tuberia_pvc_clase_9_4_con_junta_m` Tubo de PVC Classe 9 Ø 4″ com Junta (m) | 36374 TUBO PVC PBA JEI, CLASSE 12, DN 100 MM, PARA REDE DE AGUA (NBR 5647) (M) | 1 | IS054BR |
| `br_tuberia_pvc_e_40_2_con_junta_m` Tubo de PVC E-40 Ø 2″ com Junta (m) | 36084 TUBO PVC PBA JEI, CLASSE 12, DN 50 MM, PARA REDE DE AGUA (NBR 5647) (M) | 1 | IS055BR |
| `br_tuberia_pvc_e_40_3_con_junta_m` Tubo de PVC E-40 Ø 3″ com Junta (m) | 36373 TUBO PVC PBA JEI, CLASSE 12, DN 75 MM, PARA REDE DE AGUA (NBR 5647) (M) | 1 | IS056BR |
| `br_tuberia_pvc_e_40_4_con_junta_m` Tubo de PVC E-40 Ø 4″ com Junta (m) | 36374 TUBO PVC PBA JEI, CLASSE 12, DN 100 MM, PARA REDE DE AGUA (NBR 5647) (M) | 1 | IS057BR |
| `br_tubo_de_hormigon_12_para_desague_m` Tubo de Concreto 12″ para Esgoto (m) | 37450 TUBO DE CONCRETO SIMPLES PARA AGUAS PLUVIAIS, CLASSE PS1, COM ENCAIXE  (M) | 1 | IS077BR |
| `br_tubo_de_hormigon_16_para_desague_m` Tubo de Concreto 16″ para Esgoto (m) | 37451 TUBO DE CONCRETO SIMPLES PARA AGUAS PLUVIAIS, CLASSE PS1, COM ENCAIXE  (M) | 1 | IS078BR |
| `br_tubo_de_hormigon_armado_40_m` Tubo de Concreto Armado 40″ (m) | 7753 TUBO DE CONCRETO ARMADO PARA AGUAS PLUVIAIS, CLASSE PA-1, COM ENCAIXE  (M) | 1 | OG039BR |
| `br_tubo_desague_pvc_4_sdr_m` Tubo de PVC para Esgoto Ø 4″ SDR (m) | 36365 TUBO COLETOR DE ESGOTO PVC, JEI, DN 100 MM (NBR 7362) (M) | 1 | IS081BR |
| `br_tubo_desague_pvc_6_sdr_35_m` Tubo de PVC para Esgoto Ø 6″ SDR 35 (m) | 41936 TUBO COLETOR DE ESGOTO, PVC, JEI, DN 150 MM (NBR 7362) (M) | 1 | IS082BR |
| `br_tubo_desague_pvc_clase_9_3_m` Tubo de PVC para Esgoto Classe 9 Ø 3″ (m) | 9837 TUBO PVC SERIE NORMAL, DN 75 MM, PARA ESGOTO PREDIAL (NBR 5688) (M) | 1 | IS079BR |
| `br_tubo_desague_pvc_clase_9_4_m` Tubo de PVC para Esgoto Classe 9 Ø 4″ (m) | 9836 TUBO PVC SERIE NORMAL, DN 100 MM, PARA ESGOTO PREDIAL (NBR 5688) (M) | 1 | IS080BR |
| `br_turba_m3` Turfa (m3) | 7253 TERRA VEGETAL (GRANEL) (M3) | 1 | OT028BR, OT029BR, OT045BR |
| `br_urinario_blanco_con_sifon_pza` Mictório Branco com Sifão (Pza) | 10432 MICTORIO INDIVIDUAL, SIFONADO, DE LOUCA BRANCA, SEM COMPLEMENTOS (UN) | 1 | IS013BR |
| `br_valvula_de_retencion_galvanizado_1_pza` Válvula de Retenção Galvanizada 1″ (Pza) | 10418 VALVULA DE RETENCAO VERTICAL, DE BRONZE (PN-16), 1", 200 PSI, EXTREMID (UN) | 1 | IS036BR, IS037BR, IS038BR, IS039BR |
| `br_ventana_mad_cedro_marco_2x3_m2` Janela de Madeira Cedro com Batente 2X3″ (m2) | 3437 JANELA BASCULANTE EM MADEIRA PINUS/ EUCALIPTO/ TAUARI/ VIROLA OU EQUIV (M2) | 1 | CR008BR |
| `br_vidrio_catedral_blanco_3_mm_m2` Vidro Catedral Branco 3 Mm (m2) | 10499 VIDRO MARTELADO OU CANELADO, 4 MM - SEM COLOCACAO (M2) | 1 | AC060BR |
| `br_vigueta_pretensada_h_20_m` Vigota Protendida H=20 (m) | 43348 LAJE PRE-MOLDADA COM VIGOTA PROTENDIDA (LAJOTAS + VIGOTAS) COM LAJOTA  (M2) | 0.5 | OG021BR, OG022BR, OG023BR, OG024BR |
| `br_zocalo_cedro_3_m` Rodapé de Cedro 3″ (m) | 6186 RODAPE DE MADEIRA MACICA CUMARU/IPE CHAMPANHE OU EQUIVALENTE DA REGIAO (M) | 1 | AC042BR |
| `br_zocalo_de_ceramica_m` Rodapé Cerâmico (m) | 536 REVESTIMENTO PARA PAREDE, EM CERAMICA ESMALTADA, FORMATO MENOR OU IGUA (M2) | 0.1 | AC041BR |
| `br_zocalo_granitico_de_25x10_cm_m` Rodapé de Granilite 25X10 Cm (m) | 34680 RODAPE PRE-MOLDADO DE GRANILITE, MARMORITE OU GRANITINA L = 10 CM (M) | 1 | AC043BR |

## Se quitan de recetas (insumos usados sin sustituto)

| insumo ArqOn | ítems | motivo |
|---|---|---|
| `br_accesorios_div_glb` Acessórios Diversos | AC057BR, AC059BR | Global. Global. |
| `br_accesorios_p_estruc_aluminio_glb` Acessórios para Estrutura de Alumínio | AC058BR | Global. Global; ítem NINGUNA (fachada). |
| `br_accesorios_pvc_codos_tees_glb` Conexões de PVC (joelhos, tês) | IS001BR, IS002BR | Global. Global de conexiones: la receta SINAPI del punto trae cada conexión. |
| `br_aceite_de_linaza_l` Óleo de Linhaça | AC056BR | Sin equivalente. Sin aceite de linaza; el lustrado SINAPI usa cera (41967). |
| `br_acople_superjunta_de_110_mm_pza` Luva de Compressão de 110 Mm | IS066BR | Cupla de compresión para PEAD: el SINAPI sólo tiene electrofusión o adaptadores. Idem. |
| `br_acople_superjunta_de_20_mm_pza` Luva de Compressão de 20 Mm | IS058BR | Idem. Coeficiente ~0,01/m, sin cupla de compresión en el SINAPI. |
| `br_acople_superjunta_de_25_mm_pza` Luva de Compressão de 25 Mm | IS059BR | Idem. Idem. |
| `br_acople_superjunta_de_32_mm_pza` Luva de Compressão de 32 Mm | IS060BR | Idem. Idem. |
| `br_acople_superjunta_de_40_mm_pza` Luva de Compressão de 40 Mm | IS061BR | Idem. Idem. |
| `br_acople_superjunta_de_50_mm_pza` Luva de Compressão de 50 Mm | IS062BR | Idem. Idem. |
| `br_acople_superjunta_de_63_mm_pza` Luva de Compressão de 63 Mm | IS063BR | Idem. Idem. |
| `br_acople_superjunta_de_75_mm_pza` Luva de Compressão de 75 Mm | IS064BR | Idem. Idem. |
| `br_acople_superjunta_de_90_mm_pza` Luva de Compressão de 90 Mm | IS065BR | Idem. Idem. |
| `br_agua_comun_l` Água Comum | OG075BR, OG082BR | Sin agua como insumo. Las composiciones SINAPI no cotizan el agua. |
| `br_alc_chapa_metalico_corrug_1_m_m` Bueiro de Chapa Metálica Corrugada Ø 1 M | OG038BR | Sin alcantarilla de chapa corrugada. Alcantarilla de chapa corrugada: ítem NINGUNA. |
| `br_alcohol_al_70_l` Álcool a 70% | OT040BR | Sin equivalente. Bioseguridad (ítem NINGUNA). |
| `br_alfombra_m2` Carpete | AC063BR | El SINAPI sólo tiene alfombra INSTALADA (servicio), no el material. El SINAPI trae la alfombra instalada (servicio): el  |
| `br_anclajes_12v1_2_pza` Chumbadores 12V1/2 | OG066BR, OG067BR, OG068BR, OG069BR | Sin equivalente (precio y nombre no concuerdan con un perno suelto). Postensado: ítems NINGUNA. |
| `br_anclajes_j_pza` Chumbadores Tipo J | CU023BR, CU024BR | Sin equivalente. Idem. |
| `br_armazon_de_aluminio_m` Estrutura de Alumínio | AC058BR | Sin equivalente. Fachada pele de vidro: ítem NINGUNA. |
| `br_barbijo_bioseguridad_kn95_5_filtros_pza` Máscara de Biossegurança KN95 5 Filtros | OT040BR | El SINAPI sólo tiene PFF1 descartable y semifacial con filtro. Idem. |
| `br_base_de_anclaje_u` Base de Ancoragem | OT009BR | Sin equivalente. Idem (placa de obra). |
| `br_base_de_ducha_0_80_x_0_80_m_pza` Base de Chuveiro 0.80 X 0.80 M | IS087BR | Sin equivalente. Sin receptáculo de ducha. |
| `br_basurero_para_desechos_infecciosos_pza` Lixeira para Resíduos Infectantes | OT040BR | Sin equivalente. Idem. |
| `br_bide_blanco_con_griferia_pza` Bidê Branco com Torneira | IS086BR | Sin bidé. Sin bidé en el SINAPI; ítem NINGUNA. |
| `br_cable_grado_270_kg` Cordoalha de Protensão Grau 270 | OG066BR, OG067BR, OG068BR, OG069BR | Sin cordoalha de protensión en el SINAPI como insumo. Idem. |
| `br_calamina_pvc_2_40x0_90_m_m2` Telha de PVC 2.40X0,90 M | CU005BR | Sin telha de PVC. Sin teja de PVC; ítem a revisar (NINGUNA). |
| `br_calefon_a_gas_11l_con_accesorios_pza` Aquecedor a Gás 11L com Acessórios | IS084BR | Sin calentador a gas en el SINAPI. Calefón: ítem NINGUNA. |
| `br_calefon_a_gas_14l_con_accesorios_pza` Aquecedor a Gás 14L com Acessórios | IS085BR | Idem. Idem. |
| `br_camara_septica_plastica_1200_lt_pza` Fossa Séptica Plástica 1200 L | IS045BR | Sin fosa séptica plástica (sólo anillos de concreto). Fosa plástica: el SINAPI arma la fosa con anillos de concreto (ADA |
| `br_camara_septica_plastica_2300_lt_pza` Fossa Séptica Plástica 2300 L | IS046BR | Idem. Idem. |
| `br_caucho_granulado_p_cesped_5_kg` Borracha Granulada para Grama Sintética 5 | OT034BR | Sin equivalente. Idem. |
| `br_cemento_asfaltico_kg` Cimento Asfáltico | OG041BR | El SINAPI sólo trae el CBUQ (mezcla) y asfalto oxidado de impermeabilizar. El ítem pasa a CBUQ (1518, t) en vez de CAP + |
| `br_cenefa_m` Faixa Decorativa | CR017BR | Sin equivalente. Decorativo. |
| `br_cesped_sint_bicolor_h_5_mm_m2` Grama Sintética Bicolor H=5 Mm | OT034BR | Sin césped sintético en el SINAPI. Idem. |
| `br_cesped_sint_monofilamento_h_6_mm_m2` Grama Sintética Monofilamento H=6 Mm | OT035BR | Idem. Idem. |
| `br_cinta_union_cesped_sintetico_m` Fita de União para Grama Sintética | OT034BR, OT035BR | Sin equivalente. Césped sintético: ítem NINGUNA. |
| `br_ducha_completa_mas_instalacion_glb` Chuveiro Completo com Instalação | OT040BR | Incluye instalación (global). Idem. |
| `br_eq_amoladora` Esmerilhadeira | OT046BR | El SINAPI no tiene amoladora como equipo por hora. Las demoliciones SINAPI usan martelete, no amoladora. |
| `br_eq_maquina_losetera_tipo_pulpo_manual` Máquina Manual para Fabricação de Ladrilhos (Tipo Polvo) | OG048BR | Sin equivalente. Fabricación de bloquetes en obra: ítem NINGUNA. |
| `br_escobas_y_cepillos_pza` Vassouras e Escovas | AC063BR, AC064BR | Sin equivalente. Sin rol. |
| `br_estructura_metalica_para_letrero_glb` Estrutura Metálica para Letreiro | OT041BR | Global; sin insumo SINAPI. Placa de obra de lona: pasa a la placa de obra SINAPI. |
| `br_fachada_flotante_vidrio_reflec_6_mm_m2` Fachada em Pele de Vidro Refletivo 6 Mm | AC058BR | Fachada armada; sin insumo. Idem. |
| `br_fosa_septica_de_polie_1100_sanear_pza` Fossa Séptica de Polietileno 1100 L | IS047BR | Idem. Idem. |
| `br_fosa_septica_de_polie_2500_sanear_pza` Fossa Séptica de Polietileno 2500 L | IS048BR | Idem. Idem. |
| `br_hipoclorito_de_sodio_l` Hipoclorito de Sódio | OT040BR | Sin hipoclorito en el SINAPI. Idem. |
| `br_juego_accesorios_de_bano_pza` Jogo de Acessórios para Banheiro | IS011BR | Juego; sin equivalente. El SINAPI los trae sueltos (papeleira 11703, saboneteira 11757…): rearmar el ítem. |
| `br_lama_m3` Silte Fino (Lama) | OT044BR | Sin equivalente. Relleno con lodo: ítem NINGUNA. |
| `br_letrero_lona_con_diseno_m2` Placa de Lona com Arte | OT009BR | Sin equivalente. El ítem pasa a la placa de obra SINAPI (chapa galvanizada). |
| `br_lona_de_pvc_con_impresion_digital_m2` Lona de PVC com Impressão Digital | OT041BR | Sin equivalente. Idem. |
| `br_madera_tejido_kg` Madeira Trançada | OG029BR | Sin equivalente. Sin rol en la práctica brasileña. |
| `br_masa_flex_construpanel_kg` Argamassa Flexível para Painel de EPS | MP016BR, MP017BR, MP018BR, MP019BR | Mortero propietario para paneles EPS. Idem. |
| `br_material_para_inyeccion_por_viga_m` Calda de Injeção (por Viga) | OG066BR, OG067BR, OG068BR, OG069BR | Sin equivalente. Idem. |
| `br_medidor_de_temperatura_infrarrojo_pza` Termômetro Infravermelho | OT040BR | Sin equivalente. Idem. |
| `br_mosaico_granitico_30x30_cm_m2` Ladrilho de Granilite 30X30 Cm | AC023BR | El SINAPI sólo trae piso de granilite EJECUTADO (4786), no la baldosa. El SINAPI sólo tiene el granilite ejecutado (serv |
| `br_muro_termoacustico_e_100_mm_m2` Painel de Parede Termoacústico E=100 Mm | MP018BR | Panel de muro termoacústico; el SINAPI sólo trae telhas termoacústicas. Idem. |
| `br_muro_termoacustico_e_120_mm_m2` Painel de Parede Termoacústico E=120 Mm | MP019BR | Idem. Idem. |
| `br_muro_termoacustico_e_60_mm_m2` Painel de Parede Termoacústico E=60 Mm | MP016BR | Idem. Panel EPS tipo Construpanel: sin insumo; ítem NINGUNA. |
| `br_muro_termoacustico_e_75_mm_m2` Painel de Parede Termoacústico E=75 Mm | MP017BR | Idem. Idem. |
| `br_neopreno_compuesto_grado_60_dm3` Neoprene Composto Grau 60 | OG070BR | Sin neopreno de apoyo en el SINAPI. Apoyo de neopreno: ítem NINGUNA. |
| `br_ocre_importado_kg` Pigmento Ocre Importado | AC032BR, AC044BR | Sin pigmentos en el SINAPI. Pigmento opcional; el SINAPI no lo lleva. |
| `br_paja_kg` Palha | AC003BR, CU019BR, OT029BR | Sin equivalente. Paja en morteros/revoques: sin rol en la práctica brasileña. |
| `br_panel_fix_construpanel_kg` Argamassa de Fixação para Painel de EPS | MP016BR, MP017BR, MP018BR, MP019BR | Mortero propietario para paneles EPS. Idem. |
| `br_pediluvio_pza` Pedilúvio | OT040BR | Sin equivalente. Idem. |
| `br_pegamento_para_cesped_sintetico_l` Cola para Grama Sintética | OT034BR, OT035BR | Sin equivalente. Idem. |
| `br_perfil_h_m` Perfil H | CU023BR, CU024BR | Perfil H sin especificar. Accesorio del policarbonato; ítem NINGUNA. |
| `br_perfil_p_cercha_pcg_40x6_mm_m` Perfil C Galvanizado (PCG) para Tesoura 40X6 Mm | CU010BR | Idem (steel framing para tesoura). Idem. |
| `br_perfil_p_cercha_pgg_40x6_mm_m` Perfil PGG para Tesoura 40X6 Mm | CU008BR | Steel framing; sin sección en el SINAPI. Idem. |
| `br_perfil_pcg_61x40x6_mm_m` Perfil C Galvanizado (PCG) 61X40X6 Mm | CU010BR | Perfil C galvanizado de steel framing: el SINAPI no tiene esta sección. Idem. |
| `br_perfil_pcg_90x40x6_mm_m` Perfil C Galvanizado (PCG) 90X40X6 Mm | CU008BR, CU010BR | Idem (steel framing 90×40). Steel frame: sin perfiles en el SINAPI; ítem NINGUNA. |
| `br_perfil_pcj_90x40_mm_m` Perfil PCJ 90X40 Mm | CU010BR | Steel framing; sin sección en el SINAPI. Idem. |
| `br_perfil_pgg_61x40x6_mm_m` Perfil PGG 61X40X6 Mm | CU008BR | Steel framing; sin sección en el SINAPI. Idem. |
| `br_perfil_pgj_90x40_mm_m` Perfil PGJ 90X40 Mm | CU008BR | Steel framing; sin sección en el SINAPI. Idem. |
| `br_perfil_terminal_u_m` Perfil Terminal U | CU023BR, CU024BR | Perfil terminal sin especificar. Idem. |
| `br_phono_spray_m2` Isolamento Acústico Aplicado a Spray | OG032BR | Sin equivalente. Aislamiento proyectado: sin insumo; ítem NINGUNA. |
| `br_piedra_cortada_20x20x20_cm_m3` Pedra Cortada 20X20X20 Cm | OG057BR | Sin equivalente. Mampostería de piedra labrada: ítem NINGUNA. |
| `br_piso_flotante_m2` Piso Laminado Flutuante | AC034BR | Sin piso laminado. Sin piso laminado; ítem NINGUNA (o sustituir por piso vinílico en regla 38180). |
| `br_policarbonato_con_bronce_6_mm_m2` Policarbonato Bronze 6 Mm | CU023BR | Sin policarbonato en el SINAPI. Sin policarbonato; ítem NINGUNA. |
| `br_policarbonato_con_bronce_8_mm_m2` Policarbonato Bronze 8 Mm | CU024BR | Idem. Idem. |
| `br_quincalleria_y_accesorios_p_puerta_glb` Ferragens e Acessórios para Porta | CR010BR | Global. Global. |
| `br_ray_grass_kg` Azevém (Ray-Grass) | OT029BR | Sin semillas en el SINAPI. El SINAPI usa grama en placas, no semilla. |
| `br_reja_metalica_tubo_rect_20x30_mm_m` Grade Metálica em Tubo Retangular 20X30 Mm | OT036BR | Reja armada; sin insumo. Reja armada; ítem NINGUNA/ADAPTADA a gradil SINAPI. |
| `br_senaletica_acrilica_con_adhesivo_40x30_cm_pza` Placa de Sinalização em Acrílico com Adesivo 40x30 Cm | OT040BR | Sin equivalente. Idem. |
| `br_sillar_tipo_a_60x40x30_cm_pza` Bloco de Cantaria Tipo A 60X40X30 Cm | OG059BR | Sin equivalente. Sillar: ítem NINGUNA. |
| `br_sillar_tipo_b_40x30x30_cm_pza` Bloco de Cantaria Tipo B 40X30X30 Cm | OG060BR | Sin equivalente. Idem. |
| `br_soporte_compresor_ai_split_pza` Suporte para Condensadora de Ar Condicionado Split | IE012BR | Sin equivalente. Sin soporte de condensadora. |
| `br_supertubo_hdpe_125_mm_5_pn8_m` Tubo de PEAD 125 Mm (5″) PN8 | IS067BR | Sin PEAD 125 mm. Idem. |
| `br_supertubo_hdpe_250_mm_10_pn6_m` Tubo de PEAD 250 Mm (10″) PN6 | IS070BR | Sin PEAD 250 mm. Idem. |
| `br_supertubo_hdpe_25_mm_3_4_m` Tubo de PEAD 25 Mm (3/4″) | IS059BR | Sin PEAD 25 mm. Sin PEAD de ese diámetro: el ítem queda NINGUNA (no inventar con otro diámetro). |
| `br_supertubo_hdpe_40_mm_1_1_4_m` Tubo de PEAD 40 Mm (1 1/4″) | IS061BR | Sin PEAD 40 mm. Idem. |
| `br_supertubo_hdpe_63_mm_2_m` Tubo de PEAD 63 Mm (2″) | IS063BR | Sin PEAD 63 mm. Idem. |
| `br_supertubo_hdpe_90_mm_3_m` Tubo de PEAD 90 Mm (3″) | IS065BR | Sin PEAD 90 mm. Idem. |
| `br_tapizon_m2` Carpete Agulhado | AC064BR | Idem. Idem. |
| `br_termo_spray_m2` Isolamento Térmico Aplicado a Spray | OG033BR, OG034BR, OG035BR | Sin equivalente. Idem. |
| `br_tina_blanca_con_griferia_pza` Banheira Branca com Torneira | IS012BR | Sin bañera en el SINAPI. Sin bañera; ítem NINGUNA. |
| `br_tubo_de_hormigon_10_para_desague_m` Tubo de Concreto 10″ para Esgoto | IS076BR | El SINAPI de concreto empieza en DN 200 (simple) / 300 (armado); 250 mm no está. Sin tubo de concreto de 250 mm; ítem NI |
| `br_tubular_cuadrado_20x20_mm_m` Tubo Quadrado 20X20 Mm | CR013BR | Metalon: sin insumo SINAPI. Metalon: sin insumo; el ítem de reja pasa a NINGUNA/ADAPTADA. |
| `br_tubular_rectangular_50x30x2_mm_m` Tubo Retangular 50X30X2 Mm | OT009BR | Metalon: sin insumo SINAPI. Idem (placa de obra). |
| `br_union_por_termofusion_10_pza` União por Termofusão 10″ | IS070BR | Sin equivalente. Idem. |
| `br_union_por_termofusion_5_pza` União por Termofusão 5″ | IS067BR | Sin equivalente. Sin unión por termofusión. |
| `br_union_por_termofusion_6_pza` União por Termofusão 6″ | IS068BR | Sin equivalente. Idem. |
| `br_union_por_termofusion_8_pza` União por Termofusão 8″ | IS069BR | Sin equivalente. Idem. |
| `br_vainas_m` Bainha Metálica para Protensão | OG066BR, OG067BR, OG068BR, OG069BR | Sin vaina de postensado. Idem. |
| `br_ventana_aluminio_3_hojas_m2` Janela de Alumínio 3 Folhas | CR014BR | Ventana entera por m²; el SINAPI da ventanas por unidad y medida. Ventana de aluminio 2,40 m de 3 hojas no está; ítem NI |

## Cómo aplicar (cuando Oscar apruebe)

```
# 1) ver qué cambiaría (no escribe nada)
python tools/aplicar-propuesta-sinapi-br.py --clase SEGURO --libro "%LOCALAPPDATA%\Temp\sinapi\SINAPI_Referencia_2026_08.xlsx"
# 2) aplicar: agrega las filas SEGURO a mapa_sinapi_BR.csv y corre tools/precios-sinapi-br.py con el mismo libro
python tools/aplicar-propuesta-sinapi-br.py --clase SEGURO --libro "%LOCALAPPDATA%\Temp\sinapi\SINAPI_Referencia_2026_08.xlsx" --aplicar
```

Las SUSTITUCIONES y los QUITAR tocan `items_BR.json` y son otra fase (ver `catalogo/fuentes/analisis_composicoes_BR_20260928.md`, «Plan para que todo Brasil siga SINAPI»).
