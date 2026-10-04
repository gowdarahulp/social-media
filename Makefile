.PHONY: install test run docker-build docker-up clean

install:
	pip install -r requirements.txt

test:
	pytest backend/tests -v

run:
	uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

docker-build:
	docker compose build

docker-up:
	docker compose up -d

clean:
	rm -rf __pycache__ .pytest_cache *.db
