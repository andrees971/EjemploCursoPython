from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from todo.auth import login_required
from todo.db import get_db

bp = Blueprint('todo', __name__)

@bp.route('/')
@login_required
def index():
    db, c = get_db()
    c.execute(
        'select t.id, t.descripcion, u.username, t.completed, t.created_at from todo t JOIN user u on t.created_by = u.id'
        ' WHERE t.created_by = %s ORDER BY created_at DESC', 
        (g.user['id'],)
    )
    todos = c.fetchall()

    return render_template('todo/index.html', todos=todos)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        descripcion = request.form['descripcion']
        error = None

        if not descripcion:
            error = 'Descripcion requerida'

        if error is not None:
            flash(error)
        else:
            db, c = get_db()
            c.execute(
                'insert into todo (descripcion, completed, created_by) values (%s, %s, %s)', 
                (descripcion, False, g.user['id'])
            )
            db.commit()
            return redirect(url_for('todo.index'))

    return render_template('todo/create.html')


def get_todo(id):
    db, c = get_db()
    c.execute(
        'select t.id, t.descripcion, t.completed, t.created_by, t.created_at, u.username'
        ' from todo t join user u on t.created_by = u.id where t.id = %s',
        (id,)
    )
    todo = c.fetchone()

    if todo is None:
        abort(404, "El todo id {0} no existe".format(id))
    return todo

@bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    todo = get_todo(id)
    
    if request.method == 'POST':
        descripcion = request.form['descripcion']
        completed = True if request.form.get('completed') == 'on' else False
        error = None

        if not descripcion:
            error = "la descripcion es requerida."

        if error is not None:
            flash(error)
        else:
            db, c = get_db()
            c.execute(
                'update todo set descripcion = %s, completed = %s where id = %s and created_by = % s',
                (descripcion, completed, id, g.user['id'])
            )
            db.commit()
            return redirect(url_for('todo.index'))

    return render_template('todo/update.html', todo=todo)


@bp.route('/<int:id>/delate', methods=['GET', 'POST'])
@login_required
def delete(id):
    db, c = get_db()
    c.execute(
        'delete from todo where id = %s and created_by = %s', (id, g.user['id'])
    )
    db.commit()
    return redirect(url_for('todo.index'))