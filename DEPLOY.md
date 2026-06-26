# Guía de despliegue — SPwap V2 (multi-número)

**Dominio:** `spwap.supregsolutions.com`

> Proyecto separado del viejo `ras.supregsolutions.com` (otro código, otro dominio).
> Convive en el mismo servidor físico, en su propio directorio y con sus propios
> puertos — no toca nada de lo que ya está corriendo.

## Tabla de contenidos

- [Stack y puertos](#stack-y-puertos)
- [Parte 1 — Local (desarrollo)](#parte-1--local-desarrollo)
- [Parte 2 — Producción en servidor](#parte-2--producción-en-servidor)
- [Variables de entorno](#variables-de-entorno--referencia-completa)
- [Comandos útiles](#comandos-útiles)
- [Solución de problemas](#solución-de-problemas)

---

## Stack y puertos

| Servicio | Puerto interno (Docker) | Puerto host (producción) | Expuesto al host |
|---|---|---|---|
| web (Django + Gunicorn) | 8000 | **8006** | Solo `127.0.0.1` → Nginx |
| evolution-api | 8080 | **8086** | Solo `127.0.0.1` → Nginx |
| db (PostgreSQL 15) | 5432 | — | ❌ No expuesto |
| redis (Redis 7) | 6379 | — | ❌ No expuesto |
| celery / celery-beat | — | — | ❌ No aplica |

> DB y Redis no se exponen al host — solo se comunican dentro de la red Docker interna.  
> Nginx en el host actúa de único punto de entrada por el dominio.

---

## Parte 1 — Local (desarrollo)

### Requisitos previos

- Docker Desktop (Mac/Windows) o Docker Engine + Docker Compose v2 (Linux)
- Git

```bash
docker --version        # Docker version 24+
docker compose version  # Docker Compose version v2+
```

### 1. Clonar el repositorio

```bash
git clone <url-del-repo> spwap
cd spwap
```

### 2. Crear el archivo `.env`

```bash
cp .env.example .env
```

Para desarrollo local, editá estas líneas en `.env`:

```env
DEBUG=True
ALLOWED_HOSTS=*
```

El resto puede quedar igual que el ejemplo.

### 3. Levantar los servicios

```bash
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d
```

Primera vez tarda 2-3 minutos mientras baja imágenes y construye la app.

```bash
docker compose ps   # verificar que todo esté Up
```

### 4. Migraciones y superusuario

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

### 5. Abrir la app

- **App:** http://localhost:8000
- **Admin:** http://localhost:8000/admin
- **Evolution API:** http://localhost:8080

### 6. Conectar WhatsApp (QR)

SPwap V2 soporta varios números de WhatsApp — cada uno se da de alta por separado en
**Números de WhatsApp** (ícono de engranaje en la barra lateral):

1. Ir a `/whatsapp/numeros/` → **+ Conectar número**
2. Completar un nombre (ej. "Principal") y guardar
   - `URL Evolution API` / `API Key` pueden quedar vacíos para usar los valores
     globales del `.env` (`EVOLUTION_API_URL` / `EVOLUTION_API_KEY`)
   - Al guardar se registra automáticamente el webhook de ese número
3. Click **Ver QR** → escanear con WhatsApp
4. Repetir para cada número adicional que quieras conectar

> Para recibir mensajes reales en local, exponé el puerto con  
> `ngrok http 8000` y volvé a guardar el número (re-registra el webhook con la URL pública).

### 7. Detener / reiniciar

```bash
docker compose down                                                   # detiene (preserva datos)
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d   # levanta
docker compose logs -f web                                            # logs en vivo
```

---

## Parte 2 — Producción en servidor

### Requisitos del servidor

- **OS:** Ubuntu 22.04 LTS o Debian 12
- **RAM:** mínimo 2 GB libres además de lo que ya usa el proyecto existente
- **Disco:** 20 GB libres mínimo
- **Red:** dominio `spwap.supregsolutions.com` apuntando a la misma IP del servidor

> Si el servidor ya tiene `ras.supregsolutions.com` corriendo, los pasos 1-3
> (firewall, Docker, Nginx/Certbot) probablemente ya están hechos — verificá con
> `docker --version` y `nginx -v` antes de repetirlos.

### 1. Preparar el servidor

```bash
apt update && apt upgrade -y
apt install -y git curl ufw

# Firewall
ufw allow OpenSSH
ufw allow 80
ufw allow 443
ufw --force enable
```

### 2. Instalar Docker

```bash
curl -fsSL https://get.docker.com | sh
usermod -aG docker $USER
# Cerrar y volver a abrir la sesión SSH, luego:
docker --version
docker compose version
```

### 3. Instalar Nginx y Certbot

```bash
apt install -y nginx certbot python3-certbot-nginx
systemctl enable nginx
systemctl start nginx
```

### 4. Clonar el proyecto

Directorio propio, distinto del proyecto viejo (`/opt/conectorwpp`):

```bash
cd /opt
git clone <url-del-repo> spwap
cd spwap
```

### 5. Configurar el `.env` de producción

```bash
cp .env.example .env
chmod 600 .env
nano .env
```

Completar con valores reales:

```env
# Generá la clave con: python3 -c "import secrets; print(secrets.token_urlsafe(50))"
SECRET_KEY=<clave-larga-aleatoria>

DEBUG=False
ALLOWED_HOSTS=spwap.supregsolutions.com

POSTGRES_DB=spwap
POSTGRES_USER=spwap
POSTGRES_PASSWORD=<contraseña-segura>
POSTGRES_HOST=db
POSTGRES_PORT=5432

REDIS_URL=redis://redis:6379/0

EVOLUTION_API_URL=http://evolution-api:8080
EVOLUTION_API_KEY=<api-key-largo>
EVOLUTION_INSTANCE_NAME=principal

WHATSAPP_WEBHOOK_TOKEN=<token-secreto>
PUBLIC_URL=https://spwap.supregsolutions.com
```

> `POSTGRES_DB`/`POSTGRES_USER` viven en el contenedor `db` de **este** proyecto
> (red Docker propia) — no hay conflicto con la base del proyecto viejo aunque
> ambos usen nombres parecidos. Usar `spwap` en vez de `waply` es solo para
> que sea más claro a qué proyecto pertenece cada cosa al mirar los logs.

### 6. Levantar servicios con el override de producción

El archivo `docker-compose.prod.yml` ya está incluido en el repositorio con los puertos
de **este** proyecto (`8006` y `8086` — distintos de los `8004`/`8084` que ya usa
`ras.supregsolutions.com` en el mismo servidor).

```bash
cd /opt/spwap

docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Verificar
docker compose ps
```

### 7. Migraciones y superusuario

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

### 8. Configurar Nginx

Archivo nuevo y separado del que ya existe para `ras.supregsolutions.com` —
no se toca ese.

```bash
nano /etc/nginx/sites-available/spwap
```

Pegá esta configuración:

```nginx
server {
    listen 80;
    server_name spwap.supregsolutions.com;

    # Para que Certbot pueda validar el dominio
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # Redirigir todo lo demás a HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name spwap.supregsolutions.com;

    # Certbot agrega las líneas ssl_certificate aquí automáticamente

    client_max_body_size 20M;

    location /static/ {
        alias /opt/spwap/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /opt/spwap/media/;
        expires 7d;
    }

    location / {
        proxy_pass         http://127.0.0.1:8006;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
        proxy_connect_timeout 10s;
    }

    # SSE — sin buffering para que los eventos lleguen instantáneamente
    location /whatsapp/api/inbox/sse/ {
        proxy_pass         http://127.0.0.1:8006;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
        proxy_buffering    off;
        proxy_cache        off;
        proxy_set_header   Connection        '';
        proxy_http_version 1.1;
        chunked_transfer_encoding on;
    }
}
```

Activar y verificar:

```bash
ln -s /etc/nginx/sites-available/spwap /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### 9. Obtener certificado SSL

```bash
certbot --nginx -d spwap.supregsolutions.com
```

Certbot modifica Nginx automáticamente para agregar los certificados y la redirección HTTP→HTTPS.
No afecta el certificado de `ras.supregsolutions.com`.

Verificar renovación automática:

```bash
certbot renew --dry-run
```

### 10. Conectar el primer número de WhatsApp

SPwap V2 soporta varios números — cada uno se conecta por separado desde la
pantalla **Números de WhatsApp**, no hay un singleton de "Configuración" global:

1. Entrar a `https://spwap.supregsolutions.com` con el superusuario
2. Ir a `/whatsapp/numeros/` → **+ Conectar número**
3. Completar un nombre (ej. "Principal") y guardar
   - Dejá `URL Evolution API` / `API Key` vacíos para que use los valores
     globales del `.env` (`EVOLUTION_API_URL=http://evolution-api:8080` interno,
     `EVOLUTION_API_KEY`) — solo hace falta llenarlos si ese número en particular
     usa otro servidor Evolution
   - Al guardar se registra automáticamente el webhook en
     `https://spwap.supregsolutions.com/whatsapp/webhook/<instance_name>/`
4. Click **Ver QR** → escanear con WhatsApp
5. Repetir el paso para cada número adicional, y asignar agentes a cada uno
   desde `/usuarios/` (editar usuario → tildar los números que atiende)

> **Importante:** la URL de Evolution API es `http://evolution-api:8080`
> (nombre del servicio Docker, puerto interno). El puerto `8086` es solo para
> acceso externo desde el host — la app accede por la red interna Docker directamente.

### 11. Verificar que todo funciona

```bash
# Estado de servicios
docker compose ps

# Logs en vivo
docker compose logs -f web celery

# Probar la app
curl -sI https://spwap.supregsolutions.com/
# Debe devolver: HTTP/2 302 (redirige a login)

# Probar que el webhook de un número responde (404 si el instance_name no existe,
# 403 si existe pero falta el header apikey — ambos confirman que la ruta está viva)
curl -s -o /dev/null -w "%{http_code}\n" https://spwap.supregsolutions.com/whatsapp/webhook/principal/
```

---

## Resumen de puertos — convivencia con otros proyectos en el servidor

```
Internet
    │
    ▼
Nginx :80 / :443
    │
    ├── crm.supregsolutions.com    → 127.0.0.1:8000   (CRM existente)
    ├── ras.supregsolutions.com    → 127.0.0.1:8004    (proyecto viejo, V1)
    └── spwap.supregsolutions.com  → 127.0.0.1:8006    (este proyecto, V2)

Red Docker "crm_default"        Red Docker "conectorwpp_default"   Red Docker "spwap_default"
┌─────────────────────┐        ┌─────────────────────────────┐    ┌─────────────────────────────┐
│ web    :8000 interno │        │ web    :8000 interno        │    │ web    :8000 interno        │
│ db     :5432 interno │        │ db     :5432 interno        │    │ db     :5432 interno        │
│ redis  :6379 interno │        │ redis  :6379 interno        │    │ redis  :6379 interno        │
│ ...                  │        │ evolution-api:8080 interno  │    │ evolution-api:8080 interno  │
└─────────────────────┘        └─────────────────────────────┘    └─────────────────────────────┘
  Host: :8000                    Host: :8004 (web) / :8084 (evo)    Host: :8006 (web) / :8086 (evo)
```

Los números internos no importan — cada proyecto vive en su propia red Docker,
con su propia base de datos y su propio Redis, completamente aislados entre sí.

---

## Variables de entorno — referencia completa

| Variable | Descripción | Valor en producción |
|---|---|---|
| `SECRET_KEY` | Clave secreta Django | Cadena aleatoria 50+ chars |
| `DEBUG` | Modo debug | `False` |
| `ALLOWED_HOSTS` | Dominios permitidos | `spwap.supregsolutions.com` |
| `POSTGRES_DB` | Nombre de la DB | `spwap` |
| `POSTGRES_USER` | Usuario PostgreSQL | `spwap` |
| `POSTGRES_PASSWORD` | Contraseña PostgreSQL | Contraseña segura |
| `POSTGRES_HOST` | Host DB (servicio Docker) | `db` |
| `POSTGRES_PORT` | Puerto PostgreSQL | `5432` |
| `REDIS_URL` | URL Redis | `redis://redis:6379/0` |
| `EVOLUTION_API_URL` | URL interna Evolution API (default si un número no la pisa) | `http://evolution-api:8080` |
| `EVOLUTION_API_KEY` | API key Evolution (default si un número no la pisa) | Cadena aleatoria larga |
| `EVOLUTION_INSTANCE_NAME` | Nombre de instancia default al crear el primer número | `principal` |
| `WHATSAPP_WEBHOOK_TOKEN` | Token validación webhook (default si un número no tiene el suyo) | Cadena aleatoria |
| `PUBLIC_URL` | URL pública del servidor | `https://spwap.supregsolutions.com` |
| `N8N_WEBHOOK_URL` | URL n8n (opcional) | `https://...` |
| `CRM_API_KEY` | API key para n8n (opcional) | Cadena aleatoria |

> Desde la V2, `EVOLUTION_API_URL`/`EVOLUTION_API_KEY`/`WHATSAPP_WEBHOOK_TOKEN`
> son solo **valores default**: cada número conectado en `/whatsapp/numeros/`
> puede pisarlos con los suyos propios si hace falta.

---

## Comandos útiles

```bash
# ── Servicios ──────────────────────────────────────────────────────────────
docker compose ps
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
docker compose down
docker compose restart web
docker compose logs -f web celery

# ── Migraciones ────────────────────────────────────────────────────────────
docker compose exec web python manage.py migrate
docker compose exec web python manage.py showmigrations

# ── Usuarios ───────────────────────────────────────────────────────────────
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py changepassword <username>

# ── Shell / debug ──────────────────────────────────────────────────────────
docker compose exec web python manage.py shell
docker compose exec db  psql -U spwap spwap

# ── Backup de base de datos ────────────────────────────────────────────────
docker compose exec db pg_dump -U spwap spwap > backup_$(date +%Y%m%d_%H%M).sql

# Restaurar
docker compose exec -T db psql -U spwap spwap < backup_20240601_1200.sql

# ── Actualizar el código ───────────────────────────────────────────────────
git pull
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build web celery celery-beat
docker compose exec web python manage.py migrate
docker compose logs --tail=30 web
```

---

## Solución de problemas

### Error 502 Bad Gateway desde Nginx

```bash
# 1. Verificar que el contenedor web corre
docker compose ps

# 2. Ver el error exacto
docker compose logs --tail=50 web

# 3. Verificar que Gunicorn escucha en el puerto 8006 del host
ss -tlnp | grep 8006
```

### Webhook de un número no recibe mensajes

```bash
# Verificar que el webhook de ese instance_name responde
# (403 = ruta viva, falta el header apikey; 404 = el número no existe o está inactivo)
curl -X POST https://spwap.supregsolutions.com/whatsapp/webhook/<instance_name>/ \
  -H "apikey: TU_WEBHOOK_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"event":"test"}'

# Ver logs del webhook
docker compose logs web | grep -i webhook
```

Si la app está bien pero Evolution API no pega al webhook, entrar a
`/whatsapp/numeros/`, editar ese número y volver a guardar — eso re-registra
la URL del webhook en Evolution API.

### La app corre pero ALLOWED_HOSTS da error 400

```bash
# Verificar el .env
grep ALLOWED_HOSTS /opt/spwap/.env
# Debe tener: ALLOWED_HOSTS=spwap.supregsolutions.com

# Reiniciar la app para que tome el cambio
docker compose restart web
```

### Celery no procesa tareas

```bash
docker compose logs --tail=50 celery
docker compose restart celery
```

### Importar archivo grande falla (413 Request Entity Too Large)

```bash
# Editar Nginx
nano /etc/nginx/sites-available/spwap
# Cambiar: client_max_body_size 20M;  →  client_max_body_size 50M;

nginx -t && systemctl reload nginx
```
