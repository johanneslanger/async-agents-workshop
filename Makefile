# Async Agents Workshop Makefile

.PHONY: install-infra deploy-infra install-backend install-frontend start-frontend build-frontend install-all deploy-all install-notebook clean clean-frontend clean-infra clean-all

# Infrastructure commands
install-infra:
	cd unitok/infrastructure && npm install

deploy-infra:
	cd unitok/infrastructure && npm run deploy

clean-infra:
	rm -rf unitok/infrastructure/cdk.out
	rm -rf unitok/infrastructure/node_modules

# Backend commands
install-backend:
	cd unitok/backend/functions/publish-post && pip install -r requirements.txt
	cd unitok/backend/functions/get-posts && pip install -r requirements.txt

# Frontend commands
install-frontend:
	cd unitok/frontend && npm install

start-frontend:
	cd unitok/frontend && npm start

build-frontend:
	cd unitok/frontend && npm run build

clean-frontend:
	rm -rf unitok/frontend/build
	rm -rf unitok/frontend/temp
	rm -rf unitok/frontend/node_modules

# Notebook commands
install-notebook:
	pip install -r notebooks/requirements.txt

# Combined commands
install-all: install-infra install-backend install-frontend install-notebook

deploy-all: build-frontend deploy-infra

# Clean commands
clean-all: clean-frontend clean-infra
	@echo "All build artifacts and temporary files have been removed."

clean: clean-all

# Local development
start-local:
	@echo "Starting local development environment..."
	@echo "1. Starting frontend..."
	cd unitok/frontend && npm start &
	@echo "Frontend started at http://localhost:3000"

# Help command
help:
	@echo "Async Agents Workshop Makefile"
	@echo ""
	@echo "Available commands:"
	@echo "  make install-infra         - Install infrastructure dependencies"
	@echo "  make deploy-infra          - Deploy infrastructure to AWS"
	@echo "  make clean-infra           - Clean infrastructure build artifacts"
	@echo "  make install-backend       - Install backend dependencies"
	@echo "  make install-frontend      - Install frontend dependencies"
	@echo "  make start-frontend        - Start frontend development server"
	@echo "  make build-frontend        - Build frontend for production"
	@echo "  make clean-frontend        - Clean frontend build artifacts"
	@echo "  make install-notebook      - Install Jupyter notebook dependencies"
	@echo "  make install-all           - Install all dependencies"
	@echo "  make deploy-all            - Build frontend and deploy all infrastructure"
	@echo "  make clean-all             - Clean all build artifacts and temporary files"
	@echo "  make clean                 - Alias for clean-all"
	@echo "  make start-local           - Start local development environment"
	@echo "  make help                  - Show this help message"
