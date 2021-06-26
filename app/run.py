from app import app

server = app.server

if __name__ == "__main__":
    server.run(debug=True, port=4401)
