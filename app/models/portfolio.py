from pydantic import BaseModel
from typing import List
from .basic_info import BasicInfo
from .skill import Skill
from .project import Project
from .experience import Experience
from .education import Education
from .publication import Publication
from .award import Award
from .volunteer import Volunteer

class Portfolio(BaseModel):
    basics: BasicInfo
    skills: List[Skill]
    projects: List[Project]
    experiences: List[Experience]
    schools: List[Education]
    languages: List[str] = []
    interests: List[str] = []
    references: List[str] = []
    certifications: List[str] = []
    publications: List[Publication] = []
    volunteers: List[Volunteer] = []
    awards: List[Award] = []
    social: List[str] = []
