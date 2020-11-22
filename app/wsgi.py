from app import app


if __name__ == "__main__":
    # Run the server
    app.run(host='0.0.0.0', threaded=True)
    