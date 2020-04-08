OWNER=nielsbohr
IMAGE=projects-site
TAG=edge
ARGS=

all: clean build push

init:
	mkdir -m775 -p persistence
	chgrp 33 persistence

build:
	docker build -t ${OWNER}/${IMAGE}:${TAG} ${ARGS} .

clean:
	rm -fr persistence
	docker rmi -f ${OWNER}/${IMAGE}:${TAG}

push:
	docker push ${OWNER}/${IMAGE}:${TAG}
