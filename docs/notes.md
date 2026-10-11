# Notes de projet

## 11 octobre 2026 — premières observations

- 458 stations reçues, dont environ 160 changent d'état chaque minute.
- Dimanche vers 16 h (heure de Lyon) : 71 stations vides sur 454 ouvertes, soit environ 16 %.
- Stations vides : Carmélites, Quai Lassagne, Place Sathonay (pentes de la Croix-Rousse). Hypothèse : les vélos descendent la colline mais remontent peu.
- « 0-555 - ATELIER VÉLO'V » est l'atelier de réparation : exclu dans `stg_station_status`.
- Les horodatages de l'API sont en UTC : convertis à l'heure de Paris dans dbt.
