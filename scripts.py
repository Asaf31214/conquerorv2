import typer

app = typer.Typer()


@app.command()
def start_server():
    from server import server

    server()


@app.command()
def start_client():
    from client import client

    client()


if __name__ == "__main__":
    app()
