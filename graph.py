import heapq
import math


# кастомные исключения
class GraphError(Exception):
    pass


class VertexExistsError(GraphError):
    pass


class VertexNotFoundError(GraphError):
    pass


class EdgeExistsError(GraphError):
    pass


class EdgeNotFoundError(GraphError):
    pass


class InvalidWeightError(GraphError):
    pass


class NoPathError(GraphError):
    pass


# класс для работы с графом
class Graph:
    def __init__(self) -> None:
        self._edge: dict[str, dict[str, float]] = {}

    def check_vertex(self, vertex: str) -> None:
        """проверка на существование вершины"""
        if vertex not in self._edge:
            raise VertexNotFoundError(f"Такой вершины нет: {vertex}")

    def add_vertex(self, vertex: str) -> None:
        """добавление ветки"""
        if vertex in self._edge:
            raise VertexExistsError(f"Вершина уже есть: {vertex}")
        self._edge[vertex] = {}

    def remove_vertex(self, vertex: str) -> None:
        """удалить вершину и ветку"""
        self.check_vertex(vertex)

        for neighbour in list(self._edge[vertex]):
            del self._edge[neighbour][vertex]

        del self._edge[vertex]

    def add_edge(self, first: str, second: str, weight: float) -> None:
        """создание ребра графа"""
        self.check_vertex(first)
        self.check_vertex(second)

        if second in self._edge[first]:
            raise EdgeExistsError(f"Ребро уже есть: {first} -> {second}")

        if (
            not isinstance(weight, (int, float))
            or isinstance(weight, bool)
            or weight <= 0
            or not math.isfinite(weight)
        ):
            raise InvalidWeightError(
                "Вес ребра должен быть положительным и конечным числом"
            )

        self._edge[first][second] = float(weight)
        self._edge[second][first] = float(weight)

    def remove_edge(self, first: str, second: str) -> None:
        self.check_vertex(first)
        self.check_vertex(second)

        if second not in self._edge[first]:
            raise EdgeNotFoundError(f"Нет ребра: Из {first} в {second}")
        del self._edge[first][second]

        # через add_edge можно создать петлю поэтому нужна такая проверка(на всякий случай)
        if first != second:
            del self._edge[second][first]

    # алгоритм дейкстры
    def deikstra(self, start: str, finish: str) -> tuple[float, dict[str, str]]:
        self.check_vertex(start)
        self.check_vertex(finish)
        distance: dict[str, float] = {start: 0.0}
        previous: dict[str, str] = {}
        visited: set[str] = set()
        queue: list[tuple[float, str]] = [(0.0, start)]

        while queue:
            time, vertex = heapq.heappop(queue)
            if vertex in visited:
                continue
            visited.add(vertex)
            if vertex == finish:
                return time, previous

            for neighbour, weight in self._edge[vertex].items():
                if neighbour in visited:
                    continue
                new_time = time + weight
                if new_time < distance.get(neighbour, math.inf):
                    distance[neighbour] = new_time
                    previous[neighbour] = vertex
                    heapq.heappush(queue, (new_time, neighbour))

        raise NoPathError(f"Нет пути между {start} и {finish}")

    def shortest_time(self, start: str, finish: str) -> float:
        time, _ = self.deikstra(start, finish)
        return time

    def shortest_path(self, start: str, finish: str) -> list[str]:
        _, previous = self.deikstra(start, finish)
        put = [finish]
        while put[-1] != start:
            put.append(previous[put[-1]])
        put.reverse()
        return put
