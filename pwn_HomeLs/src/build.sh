#!/bin/bash
docker rm -f homels-instance 2>/dev/null
docker build -t homels .
docker run -d -p 5295:5295 --rm --name homels-instance homels
