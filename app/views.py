from flask import render_template, Markup, flash, request, redirect, url_for
from time import sleep
from app import app

app.secret_key = '4de2eacfb1fb2f93791c05884568805794874daef98bffaf'


def read_data():
    with open("app/data.csv") as f:
        data = []
        for line in f.read().split("\n"):
            data_line = []
            for field in line.split(';'):
                field = Markup(field.replace("\\n", "<br />"))
                data_line.append(field)
            data.append(data_line)
    return data


def write_data(new_data, id=None):
    data = read_data()
    for line in data:
        max_id = line[0]
    if str(max_id) == "ID":
        new_id = 1
    else:
        new_id = int(max_id) + 1
    new_line = "\n{};{}".format(new_id, ";".join(new_data))
    with open("app/data.csv", mode='a') as f:
        f.write(new_line)


@app.route('/')
@app.route('/list')
def list_page():
    data = read_data()
    return render_template('list.html', data=data, enumerate=enumerate)


@app.route('/story')
def story():
    status_list = ["Planning", "TODO", "In Progress", "Review", "Done"]
    return render_template('form.html', status_list=status_list)


@app.route('/story/add', methods=["GET", "POST"])
def add_story():
    if request.method == "POST":
        story_title = request.form["story_title"]
        user_story = request.form["user_story"]
        acceptance_criteria = request.form["acceptance_criteria"]
        business_value = request.form["business_value"]
        estimation = request.form["estimation"]
        status = request.form["status"]
        data = [story_title, user_story, acceptance_criteria, business_value, estimation, status]
        if "" in data:
            flash("All fields required")
            return redirect(url_for("story"))
        else:
            write_data(data)
            return redirect(url_for("list_page"))
