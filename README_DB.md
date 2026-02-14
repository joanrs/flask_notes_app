empty_notes.db

Esta base de datos SQLite creada para el repositorio contiene SOLO el esquema (tablas) y NO contiene datos de usuario, correos ni hashes de contraseñas.

Cómo fue creada:
- Ejecuta `python3 create_empty_db.py` para regenerar una `empty_notes.db` vacía con el esquema actual.

Notas de seguridad:
- No subir la base de datos real `notes.db` si contiene datos reales.
- `notes.db` está listado en `.gitignore`.

Si necesitas una versión con datos de ejemplo anonimizados en lugar de vacía, pídelo y la crearé.
