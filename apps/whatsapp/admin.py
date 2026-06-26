from django.contrib import admin
from .models import Conversacion, Mensaje, PlantillaHSM, NumeroWhatsApp, LogAPIWhatsApp

@admin.register(NumeroWhatsApp)
class NumeroWhatsAppAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'instance_name', 'telefono', 'estado_conexion', 'activo', 'orden')
    list_filter = ('activo', 'estado_conexion')

@admin.register(Conversacion)
class ConversacionAdmin(admin.ModelAdmin):
    list_display = ('telefono', 'numero', 'nombre_contacto', 'agente', 'mensajes_no_leidos', 'ventana_activa', 'ultimo_mensaje_at')
    list_filter = ('numero', 'ventana_activa', 'archivada')
    search_fields = ('telefono', 'nombre_contacto')

@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ('conversacion', 'direccion', 'tipo', 'status', 'timestamp')
    list_filter = ('direccion', 'tipo', 'status')

@admin.register(PlantillaHSM)
class PlantillaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activa', 'created_at')

@admin.register(LogAPIWhatsApp)
class LogAdmin(admin.ModelAdmin):
    list_display = ('endpoint', 'method', 'response_status', 'exitoso', 'duracion_ms', 'created_at')
    list_filter = ('exitoso',)
