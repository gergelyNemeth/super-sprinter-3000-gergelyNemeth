from flask import render_template, Markup, flash, request, redirect, url_for
from app import app

app.secret_key = '4de2eacfb1fb2f93791c05884568805794874daef98bffaf'


def read_data(story_id=None):
    """Read the data.csv file and convert it to list.

    If story_id is None, give back the whole list.
    Else read only the row with the given ID.
    """
    with open("app/data.csv") as f:
        data = []
        for line in f.read().split("\n"):
            if line != "":
                data_line = []
                # Data for listing the whole table
                if not story_id:
                    for field in line.split(';'):
                        if "\\n" in field:
                            field = Markup(field.replace("\\n", "<br>"))
                        data_line.append(field)
                    data.append(data_line)
                # Data for editing the given row in the table
                else:
                    if line[0] == str(story_id):
                        for field in line.split(';'):
                            if "\\n" in field:
                                field = Markup(field.replace("\\n", "\r\n"))
                            data_line.append(field)
                        data = data_line
    return data


def write_data(new_data, story_id=None, delete=False):
    """Store data into the data.csv file.

    If story_id is None, append the new_data to the end of the table.
    Else update only the row with the given ID.

    If delete is True, delete the row with the given ID.
    """
    new_data = fix_newline(new_data)
    data = read_data()
    # Append new data to the end of the table
    if not story_id:
        max_id = 0
        for line in data:
            if line != "":
                max_id = line[0]
        new_id = int(max_id) + 1
        new_line = "{};{}".format(new_id, ";".join(new_data))
        if new_id != 1:
            new_line = "\n" + new_line
        with open("app/data.csv", mode="a") as f:
            f.write(new_line)
    # Update only the row with the given ID
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
    """Convert newlines and line breaks to characters in the given string or list of strings."""
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
    table_header = ["ID", "Story Title", "User Story", "Acceptance Criteria", "Business Value", "Estimation", "Status"]
    return render_template('list.html', data=data, table_header=table_header, enumerate=enumerate)


@app.route('/story', methods=["GET", "POST"])
@app.route('/story/<story_id>', methods=["GET", "POST"])
def story(story_id=None):
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
            if story_id:
                return redirect(url_for("story/<story_id>"))
            else:
                return redirect(url_for("story"))
        else:
            write_data(data, story_id)
            return redirect(url_for("list_page"))

    status_list = ["Planning", "TODO", "In Progress", "Review", "Done"]
    if story_id:
        data = read_data(story_id)
    else:
        data = [0, "", "", "", 0, "0h", ""]
    return render_template('form.html', story_id=story_id, status_list=status_list,
                           data=data, int=int, float=float)


@app.route('/story/<story_id>/delete')
def delete_story(story_id):
    data = read_data(story_id)
    write_data(data, story_id, delete=True)
    return redirect(url_for("list_page"))
