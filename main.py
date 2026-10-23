import argparse

from graph import GraphError
from metro import build_metro


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Поиск маршрута в метро")

    commands = parser.add_subparsers(dest="command", required=True)

    path = commands.add_parser("path", help="Показать маршрут")
    time = commands.add_parser("time", help="Показать время")

    for command in (path, time):
        command.add_argument("--from", dest="start", required=True)
        command.add_argument("--to", dest="finish", required=True)

    args = parser.parse_args(argv)
    graph = build_metro()

    try:
        if args.command == "time":
            print(graph.shortest_time(args.start, args.finish))
        else:
            for station in graph.shortest_path(args.start, args.finish):
                print(station)
    except GraphError as error:
        parser.exit(1, f"Ошибка: {error}\n")


if __name__ == "__main__":
    main()
