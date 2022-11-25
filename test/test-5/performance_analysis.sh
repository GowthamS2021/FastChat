#!/bin/sh

running = $( python3 superserver.py && python3 server.py )

for i in {0..3}
do
    running = $( running && python3 client.py )
done

