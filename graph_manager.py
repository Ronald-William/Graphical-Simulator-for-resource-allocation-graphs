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

        # If no available instances, add a request edge
        self.graph.add_edge(process, resource, style='dashed', color='orange')
        return "not enough instances"



    def release_resource(self, resource, process):
        if resource in self.allocations.get(process, {}) and self.allocations[process][resource] > 0:
            self.resource_instances[resource]["available"] += 1
            self.allocations[process][resource] -= 1
            if self.allocations[process][resource] == 0:
                del self.allocations[process][resource]
                self.graph.remove_edge(resource, process)  # Remove allocation edge

            # Check if any process is waiting for this resource
            waiting_processes = [p for p in self.graph.predecessors(resource) 
                             if self.graph.edges[p, resource].get('style') == 'dashed']
            if waiting_processes:
                next_process = waiting_processes[0]  # Pick the first waiting process
                self.graph.remove_edge(next_process, resource)  # Remove request edge
                self.allocate_resource(next_process, resource)  # Allocate resource

            return True
        return False
    
    def remove_resource(self, resource):
        if resource in self.resource_instances:
            del self.resource_instances[resource]  # Remove resource record
            self.graph.remove_node(resource)  # Remove from the graph
            return True
        return False
    
    def remove_process(self, process):
        if process in self.allocations:
            # Release all allocated resources
            allocated_resources = list(self.allocations[process].keys())  # Copy keys to avoid mutation issues
            for resource in allocated_resources:
                self.release_resource(resource, process)

            del self.allocations[process]  # Remove process record

        if process in self.graph.nodes:
            self.graph.remove_node(process)  # Remove process from graph
            return True

        return False
    
