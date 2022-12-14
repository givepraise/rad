#!/bin/bash  

if ! [ -d "$1" ] ; then
  echo "β Could not find data folder";
  echo "Usage: bash start.sh [absoute path to root data folder]";
  exit 1;
fi

IMAGE=$( docker images | grep rad )
if [ -z "$IMAGE" ]
then
  echo "π Building image..."
  docker build --tag rad .
else
  echo "β Using built image."
fi

CONTAINER=$( docker ps | grep rad | cut -d' ' -f1 )
if [ -z "$CONTAINER" ]
then
  echo "π Starting container..."
else
  echo "β Restarting container..."
  docker stop $CONTAINER
fi

docker run --rm -d -it -v $(pwd):/app -v "$1:/data" rad

echo "β Opening RAD shellβ¦" 
echo "π‘ Type 'bash rad.sh' to run analysis/distribution."
echo "π‘ Type 'exit' to quit."
docker exec -ti $( docker ps | grep rad | cut -d' ' -f1 ) bash