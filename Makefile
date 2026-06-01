build:
	docker-compse --build

up:
	docker-compose up -d

down:
	docker-compose down

run-notification-event:
	docker exec -it event_backend bash -c "cd /app && python3.11 cli.py 7"

logs:
	docker-compose logs -f backend

backend:
	docker-compose exec backend bash

test:
	docker-compose exec backend pytest tests -vv --color=yes --tb=short --durations=10

test-auth:
	docker-compose exec backend pytest tests/services/test_auth_service.py -v

test-cov:
	docker-compose exec backend pytest tests --cov=app --cov-report=term-missing   --cov-report=html