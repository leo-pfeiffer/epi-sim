from app.server import app
from app.configuration import DEV_PORT

server = app.server

if __name__ == "__main__":
    server.run(debug=True, port=DEV_PORT)
