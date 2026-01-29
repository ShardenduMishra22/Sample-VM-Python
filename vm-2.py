# Install required packages inside the environment
import sys
import os
import simpy
import matplotlib.pyplot as plt

# -----------------------------
# Resource Configuration
# -----------------------------

hosts_config = [
    {"id": "Host1", "cores": 4, "ram": 8192, "storage": 100000},
    {"id": "Host2", "cores": 4, "ram": 8192, "storage": 100000}
]

vms_config = [
    {"name": "VM1", "type": "small", "cores": 1, "runtime": 5},
    {"name": "VM2", "type": "medium", "cores": 2, "runtime": 6},
    {"name": "VM3", "type": "large", "cores": 3, "runtime": 7}
]

# Save resource configuration file
os.makedirs("data", exist_ok=True)
with open("data/resource_config.txt", "w") as f:
    f.write("HOSTS\n")
    for h in hosts_config:
        f.write(str(h) + "\n")
    f.write("\nVMS\n")
    for v in vms_config:
        f.write(str(v) + "\n")

# -----------------------------
# Simulation
# -----------------------------

class Host:
    def __init__(self, env, host_id, cores):
        self.env = env
        self.id = host_id
        self.cpu = simpy.Resource(env, capacity=cores)
        self.total_cores = cores
        self.used_cores = 0

class VM:
    def __init__(self, env, name, cores, runtime, host):
        self.env = env
        self.name = name
        self.cores = cores
        self.runtime = runtime
        self.host = host
        env.process(self.run())

    def run(self):
        with self.host.cpu.request() as req:
            yield req
            self.host.used_cores += self.cores
            print(f"{self.name} mapped to {self.host.id} at time {self.env.now}")
            yield self.env.timeout(self.runtime)
            self.host.used_cores -= self.cores

env = simpy.Environment()
hosts = [Host(env, h["id"], h["cores"]) for h in hosts_config]

util_time = []
util_percent = []

def monitor(env):
    while True:
        used = sum(h.used_cores for h in hosts)
        total = sum(h.total_cores for h in hosts)
        util_time.append(env.now)
        util_percent.append((used / total) * 100)
        yield env.timeout(1)

env.process(monitor(env))

VM(env, "VM1", 1, 5, hosts[0])
VM(env, "VM2", 2, 6, hosts[0])
VM(env, "VM3", 3, 7, hosts[1])

env.run(until=15)

plt.figure()
plt.plot(util_time, util_percent)
plt.xlabel("Time")
plt.ylabel("CPU Utilization (%)")
plt.title("Datacenter CPU Utilization Over Time")
plt.savefig("data/utilization.png")
plt.close()

print("FILES CREATED:")
print("data/resource_config.txt")
print("data/utilization.png")
