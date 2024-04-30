# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 20:52:19 2024

@author: mduby
"""

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
)

from board.database import get_db

bp = Blueprint("entries", __name__)

def getTotalStudents():
    db = get_db()
    result = db.execute("SELECT Count(*) FROM student").fetchall()
    return result  

@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        name = request.form["name"]
        id = request.form["id"]
        email = request.form["email"]
        year = request.form["year"]
        password = request.form["password"]
        office = request.form["office"]
        
        if (name and id and email and year):
            db = get_db()
            if (year == 'Professor'):
                print("prof")
                db.execute(
                    "INSERT INTO employee (employee_name, employee_id, email, office, password) VALUES (?, ?, ?, ?, ?)",
                    (name, id, email, office, password),
                )
                db.commit()
            else:   
                db.execute(
                    "INSERT INTO student (student_name, student_id, email, student_year, password) VALUES (?, ?, ?, ?, ?)",
                    (name, id, email, year, password),
                )
                db.commit()
            return redirect(url_for("entries.create"))
        return render_template("entries/register.html")
    return render_template("entries/register.html")

@bp.route("/create_class", methods=("GET", "POST"))
def create_class():
    if request.method == "POST":
        name = request.form["class_name"]
        id = request.form["class_id"]
        email = request.form["email"]
        
        db = get_db()
        class_exists = db.execute("SELECT COUNT(*) FROM teaches WHERE class_fid = ?", (id, )).fetchone()
        if (class_exists[0] > 0):
            return redirect(url_for("pages.logging"))
        
        if (name and id and email):
            employee = db.execute("SELECT employee_id FROM employee WHERE email = ?", (email, )).fetchone()
            db.execute(
                    "INSERT INTO teaches (class_fid, employee_fid) VALUES (?, ?)",
                    (id, str(employee[0])),
                )
            db.commit()
            db.execute(
                "INSERT INTO class (class_id, class_name) VALUES (?, ?)", (name, id))
            db.commit()
        return render_template("entries/create_class.html")
    return render_template("entries/create_class.html")

@bp.route("/create", methods=("GET", "POST"))
def create(): 
    db = get_db()
    classes = db.execute("SELECT DISTINCT class_name FROM class").fetchall()

    if request.method == "POST":
        student_id = request.form["student_id"]
        task = request.form["task"]
        time_spent = request.form["time_spent"]
        class_name = request.form["class_name"]
        group_num = request.form["group_num"]
        password = request.form["password"]
       
        student_exists = db.execute(f"SELECT student_name FROM student WHERE student_id = {student_id}").fetchone()
        
        if (not student_exists or len(student_exists) == 0):
            return redirect(url_for("entries.register"))
        
        found_passwords = db.execute(f"SELECT password FROM student WHERE student_id = {student_id}").fetchone()
        
        if (found_passwords[0] == password):
            db = get_db()
            
            db.execute(
                "INSERT INTO post (student_id, task, time_spent, class_name, group_num) VALUES (?, ?, ?, ?, ?)",
                (student_id, task, time_spent, class_name, group_num),
            )
            db.commit()
            
            return redirect(url_for("entries.entries"))
        else:
            return render_template("entries/wrong_password.html")
    return render_template("entries/create.html", classes=classes)

@bp.route("/entries")
def entries():
    db = get_db()
    entries = db.execute(
        "SELECT S.id, (SELECT student_name FROM student WHERE student_id = S.student_id) as author, S.task, S.time_spent, S.class_name, S.group_num FROM post as S ORDER BY S.created DESC"
    ).fetchall()
    return render_template("entries/entries.html", entries=entries)

@bp.route("/classes")
def classes():
    db = get_db()
    classes = db.execute(
        "SELECT DISTINCT class_fid, employee_name, email, office FROM teaches JOIN employee ON employee_id = employee_fid ORDER BY class_fid"
    ).fetchall()
    
    return render_template("entries/classes.html", classes=classes)

@bp.route("/members")
def members():
    db = get_db()
    students = db.execute(
        "SELECT student_id, student_name, email, student_year FROM student ORDER BY student_id"
    ).fetchall()
    employees = db.execute(
        "SELECT employee_name, email, office FROM employee ORDER BY employee_id"
    ).fetchall()
    
    total = getTotalStudents()[0]
    return render_template("entries/members.html", students=students, total=total[0], employees=employees)

@bp.route("/statistics")
def statistics():
    db = get_db()
    entries = db.execute(
        "SELECT DISTINCT (SELECT student_name FROM student WHERE student_id = S.student_id) as author, ROUND(AVG(S.time_spent), 2) as average, COUNT(S.student_id) as visits, S.class_name FROM post as S GROUP BY S.student_id, S.class_name ORDER BY S.created DESC"
    ).fetchall()
    return render_template("entries/statistics.html", entries=entries)

@bp.route("/individual", methods=("GET", "POST"))
def individual():
    db = get_db()
    authors = db.execute("SELECT DISTINCT (SELECT student_name FROM student WHERE S.student_id = student_id) as author FROM post as S").fetchall()
    classes = db.execute("SELECT DISTINCT class_name FROM class").fetchall()
    groups = db.execute("SELECT DISTINCT group_num FROM post").fetchall()
    
    if request.method == "POST":
        name = request.form["name"]
        group_num = request.form["group_num"]
        class_name = request.form["class_name"]
        
        db = get_db()
        entries = ""
        statistics = ""
        student_id = db.execute("SELECT student_id FROM student WHERE student_name = ?", (name,)).fetchone()
        
        if (name != "blank"):
            statistics = db.execute("SELECT ? as author, ROUND(AVG(time_spent), 2) as average, class_name FROM post WHERE student_id = ? GROUP BY author, class_name ORDER BY created DESC", (name, str(student_id[0]))).fetchall()
            if (class_name != "blank" and group_num != "blank"):
                entries = db.execute("SELECT id, ? as author, id, task, time_spent, class_name, group_num FROM post WHERE student_id = " + str(student_id[0]) + " AND class_name = ? AND group_num = " + group_num, (name, class_name, )).fetchall() 
            elif (class_name != "blank"):
                entries = db.execute("SELECT id, ? as author, id, task, time_spent, class_name, group_num FROM post WHERE student_id = " + str(student_id[0]) + " AND class_name = ?", (name, class_name, )).fetchall()
            else:
                entries = db.execute("SELECT ? as author, id, task, time_spent, class_name, group_num FROM post WHERE student_id = ?", (name, str(student_id[0]))).fetchall()

        elif (class_name != "blank"):
            statistics = db.execute("SELECT class_name, ROUND(AVG(time_spent), 2) as average, 'All Students' as author FROM post WHERE class_name = ? GROUP BY class_name ORDER BY created DESC", (class_name, )).fetchall()
            if (group_num != "blank"):
                entries = db.execute("SELECT (SELECT S.student_name FROM student as S WHERE student_id = S.student_id) as author, id, task, time_spent, class_name, group_num FROM post WHERE class_name = ? AND group_num = " + group_num, (class_name, )).fetchall() 
            else:
                entries = db.execute("SELECT (SELECT S.student_name FROM student as S WHERE student_id = S.student_id) as author, id, task, time_spent, class_name, group_num FROM post WHERE class_name = ?", (class_name, )).fetchall() 
                
        elif (group_num != "blank"):
            statistics = db.execute("SELECT 'Entire Group' as author, ROUND(AVG(time_spent), 2) as average, class_name FROM post WHERE group_num = " + group_num + " GROUP BY group_num").fetchall()
            entries = db.execute("SELECT (SELECT S.student_name FROM student as S WHERE student_id = S.student_id) as author, id, task, time_spent, class_name, group_num FROM post WHERE group_num = " + group_num).fetchall() 

        else:
            return render_template("entries/individual.html")
        
        if (len(entries) == 0):
            return render_template("entries/no_results.html")
        else:
            return render_template("entries/search_results.html", entries=entries, statistics=statistics)
    return render_template("entries/individual.html", authors=authors, classes=classes, groups=groups)

@bp.route("/edit", methods=("GET", "POST", "DELETE"))
def edit():
    if request.method == "POST":
        id = request.form["id"]
        password = request.form["password"]
        type = request.form["type"]
        edit_value = request.form["edit_value"]
        new_value = request.form["new_value"]
        
        db = get_db()
        check = db.execute(f"SELECT password FROM student S JOIN post P ON P.student_id = S.student_id WHERE P.id = {id}").fetchone()
        
        if (check[0] == password):
            if (type == 'delete'):
                db.execute(f"DELETE FROM post WHERE id = {id}")
                db.commit()
            else:
                if (edit_value == "task"):
                    db.execute(f"UPDATE post SET task = ? WHERE id = {id}", (new_value, ))
                    db.commit()
                elif (edit_value == "time_spent"):
                    new_val = float(new_value)
                    db.execute(f"UPDATE post SET time_spent = {new_val} WHERE id = {id}")
                    db.commit()
                elif (edit_value == "class_name"):
                    db.execute(f"UPDATE post SET class_name = ? WHERE id = {id}", (new_value, ))
                    db.commit()
                elif (edit_value == "group_num"):
                    new_val = int(new_value)
                    db.execute(f"UPDATE post SET task = {new_val} WHERE id = {id}")
                    db.commit()
            return redirect(url_for("entries.entries"))
        else:
            return render_template("entries/wrong_password.html")
    return render_template("entries/edit.html")