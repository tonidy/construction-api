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


class Company(Base):
    __tablename__ = "companies"

    company_id = Column(String, primary_key=True)
    company_name = Column(String, nullable=False)

    projects = relationship("Project", back_populates="company")


class Project(Base):
    __tablename__ = "projects"

    project_id = Column(String, primary_key=True)
    project_name = Column(String, nullable=False)
    project_start = Column(String, nullable=False)
    project_end = Column(String, nullable=False)
    company_id = Column(String, ForeignKey("companies.company_id"), nullable=False)
    description = Column(String, nullable=True)
    project_value = Column(Integer, nullable=False)

    company = relationship("Company", back_populates="projects")

    @property
    def areas(self) -> list[str]:
        """Get list of areas for this project (lazy-loaded via query)."""
        # This requires a session - better to use explicit method in repository
        return []

    def __repr__(self):
        return f"<Project(id={self.project_id}, name={self.project_name})>"
