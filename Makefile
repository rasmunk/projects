OWNER=nielsbohr
APP_NAME=projects
IMAGE=${APP_NAME}-site
TAG=edge
SERVER_NAME=projects.escience.dk

all: clean build push

init:
	mkdir -m 770 -p persistence
	chown 33:33 -R persistence

build:
	docker build -t ${OWNER}/${IMAGE}:${TAG} --build-arg SERVER_NAME=${SERVER_NAME} \
	                                         --build-arg APP_NAME=${APP_NAME} \
											 .

clean:
	rm -fr persistence
	docker rmi -f ${OWNER}/${IMAGE}:${TAG}

push:
	docker push ${OWNER}/${IMAGE}:${TAG}
