# SPwap — Plataforma WhatsApp Multi-agente y Multi-número

Plataforma de WhatsApp tipo WATI, construida con Django + Evolution API (sin verificación de Meta).
Soporta varios números de WhatsApp conectados al mismo tiempo, con agentes asignados a
números específicos.

## Stack

- **Backend:** Django 5.1 + Celery + Redis
- **DB:** PostgreSQL 15
- **WhatsApp:** Evolution API (Baileys)
- **Frontend:** Django Templates (sin frameworks JS)
- **Infra:** Docker + docker-compose

## Setup rápido

### 1. Clonar y configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus datos
```

### 2. Levantar servicios

```bash
docker-compose up --build
```

### 3. Crear superusuario (admin)

```bash
docker-compose exec web python manage.py createsuperuser
```

### 4. Acceder

- **App:** http://localhost:8000
- **Admin:** http://localhost:8000/admin

## Roles de usuario

| Rol | Permisos |
|---|---|
| `admin` | Todo, incluyendo gestión de usuarios y números de WhatsApp |
| `supervisor` | Ve todas las conversaciones de todos los números, puede reasignar agentes, conecta números de WhatsApp |
| `agente` | Solo sus conversaciones, en los números que tiene asignados |

## Módulos

| Módulo | URL | Descripción |
|---|---|---|
| Inbox | `/whatsapp/inbox/` | Bandeja principal multi-agente, con selector de número |
| Plantillas | `/whatsapp/plantillas/` | Plantillas de mensajes |
| Números de WhatsApp | `/whatsapp/numeros/` | Conectar/gestionar varios números (Evolution API + QR) |
| Usuarios | `/usuarios/` | ABM de usuarios, roles y números asignados |

## Conectar WhatsApp

1. Ir a `/whatsapp/numeros/` → **+ Conectar número**
2. Ponerle un nombre (ej. "Ventas") y guardar — usa la URL/API Key globales del
   `.env` salvo que se pisen para ese número en particular
3. Escanear el QR con WhatsApp → Dispositivos vinculados
4. Repetir para cada número adicional, y asignar agentes a cada uno desde `/usuarios/`

## API para n8n

```http
POST /whatsapp/api/enviar/
X-Api-Key: <CRM_API_KEY>
Content-Type: application/json

{"conversation_id": 42, "message": "Hola!"}
```

> Con un solo número activo alcanza con `{"phone": "...", "message": "..."}` (como en V1).
> Con más de un número activo hay que indicar `conversation_id` o `instance_name`.
> Detalle completo en [N8N_API.md](N8N_API.md).

## Variables de entorno

| Variable | Descripción |
|---|---|
| `SECRET_KEY` | Clave secreta Django |
| `POSTGRES_*` | Credenciales PostgreSQL |
| `REDIS_URL` | URL de Redis |
| `EVOLUTION_API_URL` | URL default de Evolution API (cada número puede pisarla) |
| `EVOLUTION_API_KEY` | API Key default de Evolution API (cada número puede pisarla) |
| `EVOLUTION_INSTANCE_NAME` | Nombre de instancia default al crear el primer número |
| `WHATSAPP_WEBHOOK_TOKEN` | Token default para verificar webhooks (cada número puede tener el suyo) |
| `N8N_WEBHOOK_URL` | URL de n8n (opcional) |
| `CRM_API_KEY` | API Key para envío externo desde n8n |
