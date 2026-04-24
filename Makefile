# Developer shortcuts. The canonical entrypoint for end users is ./start.sh.

SHELL := /usr/bin/env bash
PY := backend/.venv/bin/python
PIP := backend/.venv/bin/pip

.PHONY: help install backend frontend dev build test lint typecheck clean

help:
	@echo "Targets:"
	@echo "  install     backend venv + deps + frontend node_modules"
	@echo "  backend     run FastAPI at localhost:7860"
	@echo "  frontend    run Vite dev server at localhost:5173"
	@echo "  dev         run both in parallel with hot reload"
	@echo "  build       build frontend for production"
	@echo "  test        backend pytest"
	@echo "  lint        ruff + eslint"
	@echo "  typecheck   mypy + tsc"

install:
	python3 -m venv backend/.venv
	$(PIP) install -e "backend[dev]"
	cd frontend && npm install

backend:
	cd backend && ../$(PY) -m vidify.main

frontend:
	cd frontend && npm run dev

dev:
	VIDIFY_DEV=1 ./start.sh --dev

build:
	cd frontend && npm run build

test:
	cd backend && ../$(PY) -m pytest -q

lint:
	cd backend && ../$(PY) -m ruff check .
	cd frontend && npm run lint

typecheck:
	cd frontend && npm run typecheck

clean:
	rm -rf backend/.venv frontend/node_modules frontend/dist
	find . -name __pycache__ -type d -exec rm -rf {} +
