import sys
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
import networkx as nx
import matplotlib.pyplot as plt

from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QGridLayout, 
                             QWidget, QMessageBox, QInputDialog, QLabel, 
                             QGraphicsView, QGraphicsScene)
from graph_manager import GraphManager
from styles import BUTTON_STYLE, VIEW_STYLE

class ResourceAllocationSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Resource Allocation Graph")
        self.setGeometry(100, 100, 800, 500)
        self.graph_manager = GraphManager()
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        layout = QGridLayout()

        title = QLabel("Resource Allocation Graph Simulator")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setStyleSheet(VIEW_STYLE)
        self.view.setMinimumSize(500, 300)

        buttons = [
            ("Add Process", self.add_process),
            ("Add Resource", self.add_resource),
            ("Allocate/Request", self.manage_allocation),
            ("Release Resource", self.release_resource),
            ("Check Deadlock", self.detect_deadlock),
            ("Show Graph", self.show_graph)
        ]

        row, col = 1, 0
        for text, handler in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(handler)
            btn.setStyleSheet(BUTTON_STYLE)
            layout.addWidget(btn, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

        layout.addWidget(title, 0, 0, 1, 3)
        layout.addWidget(self.view, row + 1, 0, 1, 3)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def add_process(self):
        process_id = self.graph_manager.add_process()
        QMessageBox.information(self, "Process Added", f"Added {process_id}")

    def add_resource(self):
        quantity, ok = QInputDialog.getInt(self, "Resource Instances", "Enter number of instances:", 1, 1, 10, 1)
        if ok:
            resource_id = self.graph_manager.add_resource(quantity)
            QMessageBox.information(self, "Resource Added", f"Added {resource_id} with {quantity} instances")

    def manage_allocation(self):
        processes = [n for n in self.graph_manager.graph.nodes if n.startswith("P")]
        resources = [n for n in self.graph_manager.graph.nodes if n.startswith("R")]
        if not processes or not resources:
            QMessageBox.warning(self, "Error", "Create at least one process and one resource")
            return
    
        process, ok = QInputDialog.getItem(self, "Select Process", "Process:", processes, 0, False)
        if not ok: return
        resource, ok = QInputDialog.getItem(self, "Select Resource", "Resource:", resources, 0, False)
        if not ok: return

        status = self.graph_manager.allocate_resource(process, resource)
        if status == "not enough instances":
            QMessageBox.information(self, "Request", f"{process} waiting for {resource}")
        else:
            QMessageBox.information(self, "Allocation", f"{resource} {status} to {process}")
    
        self.show_graph()  # Refresh the graph immediately


    def release_resource(self):
        allocations = [(u, v) for u, v in self.graph_manager.graph.edges if u.startswith("R") and v.startswith("P")]
        if not allocations:
            QMessageBox.warning(self, "Error", "No resources allocated")
            return

        allocation_strs = [f"{u} → {v}" for u, v in allocations]
        selection, ok = QInputDialog.getItem(self, "Release Resource", "Select allocation:", allocation_strs, 0, False)
        if not ok: return

        resource, process = selection.split(" → ")
        success = self.graph_manager.release_resource(resource, process)
        if success:
            QMessageBox.information(self, "Released", f"Released {resource} from {process}")

    def detect_deadlock(self):
        try:
            cycles = list(nx.simple_cycles(self.graph_manager.graph))  # Find all cycles
            if cycles:
                QMessageBox.critical(self, "Deadlock Detected!", f"Deadlock cycles: {cycles}")
            else:
                QMessageBox.information(self, "No Deadlock", "System is safe")
        except nx.NetworkXNoCycle:
            if any(e for e in self.graph_manager.graph.edges if e[0].startswith("P")):
                QMessageBox.warning(self, "Warning", "Potential deadlock (requests exist but no cycle)")
            else:
                QMessageBox.information(self, "No Deadlock", "System is safe")



    def show_graph(self):
        plt.clf()
        color_map = []
        labels = {}
        node_shapes = {}

        for node in self.graph_manager.graph.nodes:
            if node.startswith("R"):  # Resource node as rectangle
                labels[node] = node
                color_map.append("red")
                node_shapes[node] = "s"
            else:  # Process node as circle
                labels[node] = node
                color_map.append("blue")
                node_shapes[node] = "o"

        pos = nx.spring_layout(self.graph_manager.graph)

        # Draw nodes with different shapes
        for shape in set(node_shapes.values()):
            nx.draw_networkx_nodes(self.graph_manager.graph, pos, nodelist=[n for n in self.graph_manager.graph.nodes if node_shapes[n] == shape],
                                   node_shape=shape, node_color=[color_map[i] for i, n in enumerate(self.graph_manager.graph.nodes) if node_shapes[n] == shape],
                                   node_size=2000)

        # Draw normal edges (allocations)
        nx.draw_networkx_edges(self.graph_manager.graph, pos, edgelist=[(u, v) for u, v in self.graph_manager.graph.edges if self.graph_manager.graph.edges[u, v].get('style') != 'dashed'],
                               edge_color="gray", arrowsize=20)

        # Draw request edges in orange dashed style
        nx.draw_networkx_edges(self.graph_manager.graph, pos, edgelist=[(u, v) for u, v in self.graph_manager.graph.edges if self.graph_manager.graph.edges[u, v].get('style') == 'dashed'],
                               edge_color="orange", style='dashed', arrowsize=20)

        nx.draw_networkx_labels(self.graph_manager.graph, pos, labels, font_size=10)
        plt.show()

