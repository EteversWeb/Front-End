from app import app

if __name__ == "__main__":
    app.run(debug=True)


from flask import render_template
def error(message):
    return render_template("error.html", message=message)