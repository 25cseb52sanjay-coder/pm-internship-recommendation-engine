from app.schemas.student import StudentProfileCreate
from app.db.models import Skill
import pydantic
print(StudentProfileCreate.model_fields["skills"])
try:
    obj = StudentProfileCreate(skills=["Python", "C++"])
    print("Parsed skills:", obj.skills)
    print("Type of skill item:", type(obj.skills[0]))
except Exception as e:
    print("Error:", e)
