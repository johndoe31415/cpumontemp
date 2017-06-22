# cpumontemp
Small script that uses lm-sensors input to monitor CPU temperature while
simultaneously increasing CPU load by spawning processes which read from
/dev/urandom into /dev/null. After the number of processes is equal to the
number of CPUs in the system, all worker processes are killed and temperature
monitored for some more time. It is meant to make it easy to gnuplot the
load/temperature graph in order to determine if you have an issue with cooling
(or an improvement after renewing your CPU cooler or such).

# Usage and output
Really easy: Just give it the command line parameter you'd give sensors. I.e.

```
./cpumontemp.py coretemp-*
```

will do. The file format will have the format

```
time_seconds worker_cnt max_temp avg_temp [sensors_data]
```

so you can easily gnuplot it:

```
plot 'logfile.txt' using 1:2 with steps title 'Worker threads' axis x1y2, 
	'logfile.txt' using 1:3 with lines title 'Max temp', 
	'logfile.txt' using 1:4 with lines title 'Avg temp'
```

# License
MIT. Have fun.
