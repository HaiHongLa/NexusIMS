stop:
	docker kill development
	docker rm development
	docker kill imsdb
	docker rm imsdb
	docker kill production
	docker rm production
build:
	docker build . --no-cache -f ims-base.Dockerfile -t ims-base
	docker build . --no-cache -f development.Dockerfile -t development
	docker build . --no-cache -f production.Dockerfile -t production
runserver:
	docker compose up -d
flaskContainer:
	docker exec -it development /bin/bash
dbContainer:
	docker exec -it imsdb mysql -u admin -p
format:
	black .
clean: stop
	docker rmi development:latest
	docker rmi ims-base:latest
	docker rmi production:latest
	docker system prune -f
run:
	docker exec -it development sh -c "python3 app.py"
runProdServer:
	docker compose -f prod-docker-compose.yml up -d
prodContainer:
	docker exec -it production /bin/bash