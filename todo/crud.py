from sqlalchemy.orm import Session, session
from . import models, schemas


def create_todo(db: Session, todo: schemas.TodoCreate):
    db_todo = models.Todo(task_name=todo.task_name, is_completed=todo.is_completed)
    db.add(db_todo)	
    db.commit()
    db.refresh(db_todo)
    return db_todo

def get_todos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Todo).offset(skip).limit(limit).all()

def get_todo(db: Session, todo_id: int):
    return db.query(models.Todo).filter(models.Todo.id == todo_id).first()

def update_todo(db: Session, todo: schemas.TodoUpdate):
	updated_todo = db.query(models.Todo).filter(models.Todo.id == todo.id).first()
	updated_todo.task_name = todo.task_name
	updated_todo.is_completed = todo.is_completed
	db.add(updated_todo)	
	db.commit()
	db.refresh(updated_todo)
	return updated_todo

def delete_todo(db: Session, todo_id: int):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    db.delete(todo)
    db.commit()
    return todo




