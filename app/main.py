import os

from app.infrastructure import http


def main(host="127.0.0.1", port=8080):

    # Initialize the HTTP server.
    http.run(os.getenv("SERVER_HOST", host), os.getenv("SERVER_PORT", port))
