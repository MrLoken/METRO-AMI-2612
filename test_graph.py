import math

import pytest

from graph import (
    EdgeExistsError,
    EdgeNotFoundError,
    Graph,
    InvalidWeightError,
    NoPathError,
    VertexExistsError,
    VertexNotFoundError,
)
from metro import LINES, build_metro


@pytest.fixture
def graph() -> Graph:
    """создать граф с четырьмя вершинами"""
    result = Graph()
    for vertex in ("A", "B", "C", "D"):
        result.add_vertex(vertex)
    return result


@pytest.fixture
def route_graph(graph: Graph) -> Graph:
    """создать граф с несколькими маршрутами"""
    graph.add_edge("A", "B", 10)
    graph.add_edge("A", "C", 1)
    graph.add_edge("C", "B", 1)
    graph.add_edge("B", "D", 1)
    graph.add_edge("C", "D", 10)
    return graph


def test_add_vertex() -> None:
    """добавление новой вершины"""
    graph = Graph()

    graph.add_vertex("A")

    graph.check_vertex("A")
    assert graph.shortest_path("A", "A") == ["A"]


def test_add_existing_vertex(graph: Graph) -> None:
    """Повторное добавление вершины"""
    with pytest.raises(VertexExistsError, match="A"):
        graph.add_vertex("A")


@pytest.mark.parametrize("vertex", ["X", "Y"])
def test_missing_vertex(graph: Graph, vertex: str) -> None:
    """Обращение к отсутствующей вершине"""
    with pytest.raises(VertexNotFoundError, match=vertex):
        graph.check_vertex(vertex)


def test_remove_vertex(graph: Graph) -> None:
    """Удаление вершины"""

    graph.add_edge("A", "B", 1)
    graph.add_edge("B", "C", 1)

    graph.remove_vertex("B")

    with pytest.raises(VertexNotFoundError, match="B"):
        graph.check_vertex("B")
    with pytest.raises(NoPathError, match="Нет пути"):
        graph.shortest_time("A", "C")


@pytest.mark.parametrize("weight", [1, 2.5])
def test_add_edge(graph: Graph, weight: float) -> None:
    """добавление ребра"""

    graph.add_edge("A", "B", weight)

    assert graph.shortest_time("A", "B") == weight
    assert graph.shortest_time("B", "A") == weight


@pytest.mark.parametrize("weight", [0, -1, math.inf])
def test_invalid_weight(graph: Graph, weight: float) -> None:
    """Неположительный или бесконечный вес"""

    with pytest.raises(InvalidWeightError, match="Вес ребра"):
        graph.add_edge("A", "B", weight)


def test_add_existing_edge(graph: Graph) -> None:
    """Повторное добавление ребра"""

    graph.add_edge("A", "B", 1)

    with pytest.raises(EdgeExistsError, match="Ребро уже есть"):
        graph.add_edge("B", "A", 2)


def test_remove_edge(graph: Graph) -> None:
    """Удаление ребра"""

    graph.add_edge("A", "B", 1)

    graph.remove_edge("A", "B")

    with pytest.raises(NoPathError, match="Нет пути"):
        graph.shortest_time("A", "B")
    with pytest.raises(NoPathError, match="Нет пути"):
        graph.shortest_time("B", "A")


def test_remove_missing_edge(graph: Graph) -> None:
    """Удаление отсутствующего ребра"""

    with pytest.raises(EdgeNotFoundError, match="Нет ребра"):
        graph.remove_edge("A", "B")


def test_remove_loop(graph: Graph) -> None:
    """удалпение петли"""

    graph.add_edge("A", "A", 1)

    graph.remove_edge("A", "A")

    assert graph.shortest_time("A", "A") == 0
    with pytest.raises(EdgeNotFoundError, match="Нет ребра"):
        graph.remove_edge("A", "A")


@pytest.mark.parametrize(
    ("start", "finish", "expected_time", "expected_path"),
    [
        ("A", "D", 3.0, ["A", "C", "B", "D"]),
        ("D", "A", 3.0, ["D", "B", "C", "A"]),
    ],
)
def test_shortest_route(
    route_graph: Graph,
    start: str,
    finish: str,
    expected_time: float,
    expected_path: list[str],
) -> None:
    """Дейкстра"""

    time = route_graph.shortest_time(start, finish)
    path = route_graph.shortest_path(start, finish)

    assert time == expected_time
    assert path == expected_path


def test_no_path(graph: Graph) -> None:
    """Недостижимая вершина"""

    with pytest.raises(NoPathError, match="Нет пути"):
        graph.shortest_time("A", "D")
    with pytest.raises(NoPathError, match="Нет пути"):
        graph.shortest_path("A", "D")


def test_same_start_and_finish(graph: Graph) -> None:
    """нулевой вес из вершины"""

    time = graph.shortest_time("A", "A")
    path = graph.shortest_path("A", "A")

    assert time == 0
    assert path == ["A"]


def test_metro_has_31_unique_stations() -> None:
    """31 станция"""

    stations = [station for line, _ in LINES for station in line]
    expected_count = 31

    graph = build_metro()

    assert len(stations) == expected_count
    assert len(set(stations)) == expected_count
    for station in stations:
        graph.check_vertex(station)


def test_metro_route() -> None:
    """Маршрут метро"""
    graph = build_metro()
    start = "Арбатская (Арбатско-Покровская)"
    finish = "Таганская (Кольцевая)"
    expected_time = 10.5

    time = graph.shortest_time(start, finish)
    path = graph.shortest_path(start, finish)

    assert time == expected_time
    assert path == [
        "Арбатская (Арбатско-Покровская)",
        "Площадь Революции",
        "Курская (Арбатско-Покровская)",
        "Курская (Кольцевая)",
        "Таганская (Кольцевая)",
    ]
