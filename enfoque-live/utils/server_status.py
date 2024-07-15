import psutil

def get_cpu_usage():
	print(psutil.cpu_percent())
	return float(psutil.cpu_percent())