from collections import deque


class DAG:
    def __init__(self, graph: dict[str, set[str]] = {}) -> None:
        self.graph = graph

    def add(self, node: str, *predecessors: str) -> None:
        # graph points backwards at dependencies
        if node not in self.graph:
            self.graph[node] = {*predecessors}

    # TODO: check for cycles
    def is_valid(self) -> bool:
        pass

    # Unused right now
    def pop_leaves(self, node: str) -> set[str]:
        queue = deque([node])
        leaves = set()

        while len(queue):
            next_node = queue.pop()

            if next_node not in self.graph:
                return leaves

            dependencies = self.graph[next_node]

            for dep in dependencies:
                if dep not in self.graph:
                    leaves.add(dep)
                else:
                    queue.appendleft(dep)

        return leaves
