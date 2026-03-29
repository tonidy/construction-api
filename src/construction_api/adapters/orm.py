"""ORM adapters - SQLAlchemy classes for database persistence."""

from sqlalchemy import Column, String, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship

from construction_api.database import Base


# Many-to-many mapping between projects and areas
project_area_map = Table(
    "project_area_map",
    Base.metadata,
    Column("project_id", String, ForeignKey("projects.project_id"), primary_key=True),
    Column("area", String, primary_key=True),
)


class CompanyORM(Base):
    """Company ORM class for database operations."""

    __tablename__ = "companies"

    company_id = Column(String, primary_key=True)
    company_name = Column(String, nullable=False)

    projects = relationship("ProjectORM", back_populates="company")


class ProjectORM(Base):
    """Project ORM class for database operations."""

    __tablename__ = "projects"

    project_id = Column(String, primary_key=True)
    project_name = Column(String, nullable=False)
    project_start = Column(String, nullable=False)
    project_end = Column(String, nullable=False)
    company_id = Column(String, ForeignKey("companies.company_id"), nullable=False)
    description = Column(String, nullable=True)
    project_value = Column(Integer, nullable=False)

    company = relationship("CompanyORM", back_populates="projects")

    def __repr__(self):
        return f"<ProjectORM(id={self.project_id}, name={self.project_name})>"
