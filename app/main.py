import os
from flask import Flask, jsonify, redirect, render_template, request, url_for

app = Flask(__name__)

tasks = ["Learn Jenkins CI", "Learn Argo CD"]


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        task = request.form.get("task", "").strip()

        if task:
            tasks.append(task)

        return redirect(url_for("home"))

    return render_template(
        "index.html",
        tasks=tasks,
        version=os.getenv("APP_VERSION", "1.0.0")
    )


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/version")
def version():
    return jsonify(
        version=os.getenv("APP_VERSION", "1.0.0")
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
