#!/usr/bin/python3
import time
import datetime
import subprocess
import sys


class CPUMonitor(object):
	_CYCLE_DURATION_SECONDS = 60
	_FINAL_DURATION_SECONDS = 60

	def __init__(self, sensorname):
		self._sensorname = sensorname
		self._outfile = None
		self._t0 = None
		self._workers = [ ]

	def _spawn_worker(self):
		self._workers.append(subprocess.Popen([ "dd", "if=/dev/urandom", "of=/dev/null", "bs=1M" ], stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL))

	def _kill_workers(self):
		while len(self._workers) > 0:
			worker = self._workers.pop()
			worker.kill()

	def _get_cpu_count(self):
		with open("/proc/cpuinfo") as f:
			text = f.read()
		text = text.split("\n")
		cpu_cnt = 0
		for line in text:
			if line.startswith("processor"):
				cpu_cnt += 1
		return cpu_cnt

	def start(self):
		try:
			with open("logfile.txt", "a") as f:
				self._outfile = f
				self._print_info()
				self._t0 = time.time()
				for threadcount in range(self._get_cpu_count() + 1):
					self._monitor_seconds(self._CYCLE_DURATION_SECONDS)
					self._outfile.flush()
					self._spawn_worker()
				self._kill_workers()
				self._monitor_seconds(self._FINAL_DURATION_SECONDS)
		finally:
			self._kill_workers()
		self._outfile = None


	def _print_info(self):
		print("# %s UTC, %d CPUs" % (datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), self._get_cpu_count()), file = self._outfile)
		with open("/proc/cpuinfo") as f:
			text = f.read()
		text = text.split("\n")
		for line in text:
			if line == "":
				break
			print("# %s" % (line), file = self._outfile)
		print(file = self._outfile)

		temperatures = self._get_temperature()
		print("# %d sensor inputs:" % (len(temperatures)), file = self._outfile)
		for (sensor_id, (corename, temperature)) in enumerate(temperatures):
			print("#    Sensor %d: %s (initial %.2f)" % (sensor_id, corename, temperature), file = self._outfile)

	def _get_temperature(self):
		output = subprocess.check_output([ "sensors", "-u", self._sensorname ]).decode()
		corename = None
		temperatures = [ ]
		for line in output.split("\n"):
			if not line.startswith(" "):
				corename = line.split(":")[0]
			elif line.startswith("  ") and ("_input:" in line):
				temperature = float(line.split(": ")[1])
				temperatures.append((corename, temperature))
		return temperatures

	def _monitor_seconds(self, second_count):
		for seconds in range(second_count):
			t = time.time() - self._t0
			temperature = self._get_temperature()
			avg_temperature = sum(temp[1] for temp in temperature) / len(temperature)
			max_temperature = max(temp[1] for temp in temperature)
			temperature_str_display = " ".join("%5.1f" % (temp[1]) for temp in temperature)
			temperature_str_log = " ".join("%.3f" % (temp[1]) for temp in temperature)
			threadcount = len(self._workers)
			print("%3.0f %2d Max %5.1f Avg %5.1f : %s" % (t, threadcount, max_temperature, avg_temperature, temperature_str_display))
			print("%.0f %d %.3f %.3f    %s" % (t, threadcount, max_temperature, avg_temperature, temperature_str_log), file = self._outfile)
			time.sleep(1)

CPUMonitor(sys.argv[1]).start()
