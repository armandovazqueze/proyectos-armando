.PHONY: setup run clean help

DB = tracker.db
SCHEMA = database/schema.sql
SEED = database/seed.sql

## Configuración inicial: crea la base de datos y carga el catálogo
setup:
	@echo "⚙️  Creando base de datos..."
	sqlite3 $(DB) < $(SCHEMA)
	@echo "🌱 Cargando datos de ejemplo..."
	sqlite3 $(DB) < $(SEED)
	@echo "✅ Listo. Ahora corre: make run"

## Inicia el tracker diario
run:
	@python app/main.py

## Inicia el tracker (primera vez: setup + run)
start: setup run

## Borra la base de datos para empezar de cero
clean:
	@rm -f $(DB)
	@echo "🗑️  Base de datos eliminada."

## Muestra esta ayuda
help:
	@grep -E '^##' Makefile | sed 's/## /  /'
