#!/bin/sh

# python3 superserver.py && python3 server.py 8000
running = $ ( python3 superserver.py && python3 server.py 8000 )
for i in {0..3}
do
    running = $( running && python3 client.py )
done
