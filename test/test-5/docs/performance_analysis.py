import os
# Code to Measure time taken by program to execute.
import time

# store starting time
begin = time.time()

# program body starts
cmd = 'gnome-terminal -x sh -c "python3 database.py postgres password postgres; bash" '

os.system(cmd)
cmd = 'gnome-terminal -x sh -c "python3 superserver.py; bash" '
for i in range(5):
        j = 8000 + i
        k = str(j)
        cmd = 'gnome-terminal -x sh -c "python3 server.py" ; bash" '



	# print("GeeksForGeeks")
# program body ends

time.sleep(1)
# store end time
end = time.time()

# total time taken
print(f"Total runtime of the program is {end - begin}")
