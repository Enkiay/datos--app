# Auditoría de defaults (estado del branch fix/formulas-defaults)

## items.json (genérico) — 376 ítems

### ⚠ Cantidad inicial ≠ 1 (1) — el ítem "llega" con cómputo raro
| Código | Ítem | Und | Fórmula | Cantidad inicial | Default culpable |
|---|---|---|---|---|---|
| UH021 | Escalera de Hormigón Armado | m3 | `Ancho * (Peldaños * sqrt(Huella^2 + Contrahuella^2) * Espesor + Peldaños * Huella * Contrahuella / 2) + Descansos * DescansoLargo * DescansoAncho * Espesor` | **1.1845** | Huella=0.28, Contrahuella=0.175, Peldaños=16, Espesor=0.15, Descansos=0, DescansoLargo=0, DescansoAncho=0 |

### ℹ Defaults ≠ 1 solo informativos (0) — no multiplican, OK

## items_BO.json (Bolivia) — 376 ítems

### ⚠ Cantidad inicial ≠ 1 (1) — el ítem "llega" con cómputo raro
| Código | Ítem | Und | Fórmula | Cantidad inicial | Default culpable |
|---|---|---|---|---|---|
| UH021 | Escalera de Hormigón Armado | m3 | `Ancho * (Peldaños * sqrt(Huella^2 + Contrahuella^2) * Espesor + Peldaños * Huella * Contrahuella / 2) + Descansos * DescansoLargo * DescansoAncho * Espesor` | **1.1845** | Huella=0.28, Contrahuella=0.175, Peldaños=16, Espesor=0.15, Descansos=0, DescansoLargo=0, DescansoAncho=0 |

### ℹ Defaults ≠ 1 solo informativos (0) — no multiplican, OK