import os
from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapi import FastAPI, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

app = FastAPI()
load_dotenv()

API_KEY = os.getenv("API_KEY")
API_KEY = "my-secret-key-123"
DATABASE_URL = "sqlite:///./student.db"

engine = create_engine(

    DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
Base = declarative_base()



class StudentDB(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    age = Column(Integer)
    department = Column(String)
Base.metadata.create_all(bind=engine)
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )

    return x_api_key
class Student(BaseModel):
    name: str
    age: int
    department: str

@app.get("/")
def home():
    return {"message": "Hello FastAPI"}
@app.get("/about")
def about():
    return {
        "name": "My FastAPI",
        "course": "Agentic AI"
    }
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {
        "user_id": user_id
    }
@app.get("/greet")
def greet(name: str):
    return {
        "message": f"Hello {name}"
    }
@app.post("/students")
def create_student(
    student: Student,
    db: Session = Depends(get_db)
):
    new_student = StudentDB(
        name=student.name,
        age=student.age,
        department=student.department
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return {
        "message": "Student created",
        "student": new_student
    }
@app.put("/students/{student_id}")
def update_student(
    student_id: int,
    student: Student,
    db: Session = Depends(get_db)
):
    existing_student = db.query(StudentDB).filter(
        StudentDB.id == student_id
    ).first()

    if existing_student is None:
        return {
            "message": "Student not found"
        }

    existing_student.name = student.name
    existing_student.age = student.age
    existing_student.department = student.department

    db.commit()
    db.refresh(existing_student)

    return {
        "message": "Student updated",
        "student": existing_student
    }
@app.delete("/students/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    student = db.query(StudentDB).filter(
        StudentDB.id == student_id
    ).first()

    if student is None:
        return {
            "message": "Student not found"
        }

    db.delete(student)
    db.commit()

    return {
        "message": "Student deleted",
        "student_id": student_id
    }
@app.get("/students")
def get_students(
    db: Session = Depends(get_db),
    api_key: dict = Depends(verify_api_key)
):
    students = db.query(StudentDB).all()

    return students
