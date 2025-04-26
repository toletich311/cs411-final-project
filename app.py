from flask import Flask

app = Flask(__name__)

@app.route("/healthcheck")
def healthcheck():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run(debug=True)
