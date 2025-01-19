import typer

from client import client
from server import server

app = typer.Typer()


@app.command()
def start_server():
    server()


@app.command()
def start_client():
    client()


if __name__ == "__main__":
    app()
