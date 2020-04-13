OWNER=nielsbohr
IMAGE=${APP_NAME}-site
APP_NAME=projects
APP_DIR=/var/${APP_NAME}
SERVER_NAME=projects.escience.dk
TAG=edge

all: clean build push

init:
	mkdir -m 770 -p persistence
	chown 33:33 -R persistence

build:
	docker build -t ${OWNER}/${IMAGE}:${TAG} --build-arg SERVER_NAME=${SERVER_NAME} \
	                                         --build-arg APP_NAME=${APP_NAME} \
						 --build-arg APP_DIR=${APP_DIR} .

clean:
	rm -fr persistence
	docker rmi -f ${OWNER}/${IMAGE}:${TAG}

push:
	docker push ${OWNER}/${IMAGE}:${TAG}
