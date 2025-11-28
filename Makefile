.PHONY: help install api client dev clean kill

# Default target
help:
	@echo "NLP2SQL Development Commands"
	@echo ""
	@echo "Available targets:"
	@echo "  make install    - Install all dependencies (backend + frontend)"
	@echo "  make api        - Start the API server"
	@echo "  make client     - Start the frontend client"
	@echo "  make clean      - Clean all build artifacts and caches"
	@echo ""

# Install dependencies
install:
	@echo "Installing backend dependencies..."
	uv sync
	@echo ""
	@echo "Installing frontend dependencies..."
	cd client && pnpm install
	@echo ""
	@echo "All dependencies installed!"

# Start API server
api:
	uv run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Start client
client:
	cd client && pnpm run dev

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf api/__pycache__ api/**/__pycache__
	@rm -rf client/dist client/node_modules/.vite
	@echo "Clean complete"

