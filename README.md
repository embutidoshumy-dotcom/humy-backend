# Humy Embutidos API

Backend API para la aplicación Humy Embutidos.

## Deploy en Render

1. Conecta este repo a Render
2. Configura las variables de entorno:
   - `MONGO_URL`: Tu connection string de MongoDB Atlas
   - `DB_NAME`: humy_embutidos
   - `ADMIN_USERNAME`: EmbutidosHumy
   - `ADMIN_PASSWORD`: Tu contraseña de admin

## Endpoints

- `GET /api/combos` - Lista de combos
- `GET /api/store-settings` - Estado de la tienda
- `POST /api/orders` - Crear pedido
- Y más...
