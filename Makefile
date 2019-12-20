OWNER=nielsbohr
IMAGE=projects-site
TAG=edge

all: clean build push

init:
	mkdir -m775 -p persistence
	chgrp 33 persistence

build:
	docker build -t ${OWNER}/${IMAGE}:${TAG} .

build-no-cache:
	docker build --no-cache -t ${OWNER}/${IMAGE}:${TAG} .

clean:
	rm -fr persistence
	docker rmi -f ${OWNER}/${IMAGE}:${TAG}

push:
	docker push ${OWNER}/${IMAGE}:${TAG}
