from flask import render_template, Markup, flash, request, redirect, url_for
from time import sleep
from app import app

app.secret_key = '4de2eacfb1fb2f93791c05884568805794874daef98bffaf'


def read_data(story_id=None):
    with open("app/data.csv") as f:
        data = []
        for line in f.read().split("\n"):
            data_line = []
            if not story_id:
                for field in line.split(';'):
                    if "\\n" in field:
                        field = Markup(field.replace("\\n", "<br>"))
                    data_line.append(field)
                data.append(data_line)
            else:
                for field in line.split(';'):
                    if line[0] == str(story_id):
                        field = Markup(field.replace("\\n", "&#13;&#10;"))
                        data_line.append(field)
                data = data_line
    return data


def write_data(new_data, story_id=None, delete=False):
    new_data = fix_newline(new_data)
    data = read_data()
    if not story_id:
        for line in data:
            max_id = line[0]
        if str(max_id) == "ID":
            new_id = 1
        else:
            new_id = int(max_id) + 1
        new_line = "\n{};{}".format(new_id, ";".join(new_data))
        with open("app/data.csv", mode='a') as f:
            f.write(new_line)
    else:
        data_updated = []
        for line in data:
            if delete and line[0] == str(story_id):
                continue
            if line[0] == str(story_id) and not delete:
                joined_line = "{};{}".format(story_id, ";".join(new_data))
            else:
                joined_line = ";".join(line)
            data_updated.append(joined_line)
        data = "\n".join(data_updated)
        data = fix_newline(data)
        with open("app/data.csv", mode='w') as f:
            f.write(data)


def fix_newline(data):
    fixed_data = []
    if isinstance(data, (list)):
        for line in data:
            if isinstance(line, (list)):
                for field in line:
                    field.replace("\r\n", "\\n").replace("<br>", "\\n")
            else:
                line = line.replace("\r\n", "\\n").replace("<br>", "\\n")
            fixed_data.append(line)
    else:
        fixed_data = data.replace("\r\n", "\\n").replace("<br>", "\\n")
    return fixed_data


@app.route('/')
@app.route('/list')
def list_page():
    data = read_data()
    return render_template('list.html', data=data, enumerate=enumerate)


@app.route('/story', methods=["GET", "POST"])
def story():
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

    status_list = ["Planning", "TODO", "In Progress", "Review", "Done"]
    data = [0, "", "", "", 0, "0h", ""]
    return render_template('form.html', status_list=status_list, data=data, int=int, float=float)


@app.route('/story/<story_id>', methods=["GET", "POST"])
def update_story(story_id):
    status_list = ["Planning", "TODO", "In Progress", "Review", "Done"]
    data_update = read_data(story_id)
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
            return redirect(url_for("story/<story_id>"))
        else:
            write_data(data, story_id)
            return redirect(url_for("list_page"))

    return render_template('form.html', story_id=story_id, status_list=status_list,
                           data=data_update, int=int, float=float)


@app.route('/story/<story_id>/delete')
def delete_story(story_id):
    data = read_data(story_id)
    write_data(data, story_id, delete=True)
    return redirect(url_for("list_page"))
