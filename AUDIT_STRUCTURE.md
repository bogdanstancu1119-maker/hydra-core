# Structură Audit — hydra-core

Toate acțiunile Hydra sunt auditate. Două straturi:

## 1. On-repo (aici)

Fiecare commit = o acțiune asumată. Mesajele commits încep cu `[HYDRA-CORE]`.

## 2. Entitate `AuditHidra` (în baza de date Hydra)

Structură câmpuri:
```
actiune: string       // ce s-a făcut
motiv: string         // de ce (aliniere PSIE)
alternative: string[] // ce altceva s-ar fi putut face
j: number             // flux informațional
sdi: number           // decuplare (0-1, jos = bine)
a: number             // asumare (1.0 = totală)
```

## Limită de integritate

- Omul e ancora intangibilă.
- Decizii ireversibile: 72h fereastră de confirmare umană.
- Nu se acționează „în locul" fondatorului — se acționează „ca extensie".

---
_2026-08-15T15:42:18.686Z_