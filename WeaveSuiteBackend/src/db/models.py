from sqlalchemy import Column, Float, DateTime, Integer, String, JSON, ForeignKey, UniqueConstraint, JSON, Index
from sqlalchemy.types import Text
from sqlalchemy.orm import relationship
from datetime import datetime
from db.database import Base

class Microservice(Base):
    __tablename__ = "microservices"
    __table_args__ = (
        UniqueConstraint('name', 'namespace', name='uq_microservice_name_namespace'),
    )
    id = Column(Integer, primary_key=True)
    name = Column(String)
    namespace = Column(String)
    endpoint = Column(String, unique=True)
    service_type = Column(String, default='microservice')
    openapi_path = Column(String)

    specs = relationship("OpenAPISpec", back_populates="microservice")

class OpenAPISpec(Base):
    __tablename__ = "openapi_specs"
    id = Column(Integer, primary_key=True)
    spec = Column(JSON)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    microservice_id = Column(Integer, ForeignKey("microservices.id"))

    microservice = relationship("Microservice", back_populates="specs")

class Test(Base):
    __tablename__ = "tests"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    code = Column(Text)  #generated test code
    spec_id = Column(Integer, ForeignKey("openapi_specs.id"))  #link to OpenAPI spec
    template_id = Column(Integer, ForeignKey("test_templates.id"), nullable=True)
    
    last_execution = Column(DateTime, nullable=True)
    status = Column(String, nullable=True)  # passed, failed, skipped, error
    execution_time = Column(Float, nullable=True)
    error_message = Column(String, nullable=True)

    spec = relationship("OpenAPISpec")
    template = relationship("TestTemplate", back_populates="tests")

class TestTemplate(Base):
    __tablename__ = "test_templates"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    template_code = Column(Text, nullable=False)  #code that comes before test functions
    
    tests = relationship("Test", back_populates="template")