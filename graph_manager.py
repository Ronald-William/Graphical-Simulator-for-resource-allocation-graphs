import networkx as nx

class GraphManager:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.process_count = 0
        self.resource_count = 0
        self.resource_instances = {}  # Stores total and available instances
        self.allocations = {}  # {process: {resource: allocated_count}}

    def add_process(self):
        process_id = f"P{self.process_count}"
        self.graph.add_node(process_id)
        self.allocations[process_id] = {}
        self.process_count += 1
        return process_id

    def add_resource(self, instances):
        resource_id = f"R{self.resource_count}"
        self.graph.add_node(resource_id)
        self.resource_instances[resource_id] = {"total": instances, "available": instances}
        self.resource_count += 1
        return resource_id

    def allocate_resource(self, process, resource):
        if resource not in self.resource_instances or process not in self.allocations:
            return "does not exist"

        if self.resource_instances[resource]["available"] > 0:
            self.resource_instances[resource]["available"] -= 1
            self.allocations[process][resource] = self.allocations[process].get(resource, 0) + 1
            self.graph.add_edge(resource, process)  # Allocation edge
            return "allocated"
        return "not enough instances"

    def release_resource(self, resource, process):
        if resource in self.allocations.get(process, {}) and self.allocations[process][resource] > 0:
            self.resource_instances[resource]["available"] += 1
            self.allocations[process][resource] -= 1
            if self.allocations[process][resource] == 0:
                del self.allocations[process][resource]
                self.graph.remove_edge(resource, process)  # Remove edge when released
            return True
        return False

    def detect_deadlock(self):
        try:
            cycle = nx.find_cycle(self.graph, orientation="original")
            return [edge[0] for edge in cycle]
        except nx.NetworkXNoCycle:
            return None
