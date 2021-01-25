import subprocess

ran = subprocess.run(['hcitool', 'rssi','"ef:12:e6:c2:b4:7f"', '/dev/null'], capture_output=True,shell=True)
print(ran.stdout)
