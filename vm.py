import simpy

class Host:
    def __init__(self, env, cores):
        self.env = env
        self.cpu = simpy.Resource(env, capacity=cores)

class VM:
    def __init__(self, env, name, host, runtime):
        self.env = env
        self.name = name
        self.host = host
        self.runtime = runtime
        env.process(self.run())

    def run(self):
        with self.host.cpu.request() as req:
            yield req
            print(f"{self.name} START at {self.env.now}")
            yield self.env.timeout(self.runtime)
            print(f"{self.name} END at {self.env.now}")

env = simpy.Environment()
host = Host(env, cores=3)

VM(env, "VM1", host, 5)
VM(env, "VM2", host, 5)
VM(env, "VM3", host, 5)

env.run()
