from flask import render_template, Markup
from app import app


@app.route('/')
@app.route('/list')
def list_page():
    with open("app/data.csv") as f:
        data = []
        for line in f.read().split("\n"):
            data_line = []
            for field in line.split(';'):
                field = Markup(field.replace("\\n", "<br />"))
                data_line.append(field)
            data.append(data_line)
    return render_template('list.html', data=data, enumerate=enumerate)
