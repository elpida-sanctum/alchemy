from flask import Flask, render_template


appweb = Flask(__name__)


@appweb.route('/')
def index():
    return render_template("base.html")


if __name__ == '__main__':
    appweb.run()