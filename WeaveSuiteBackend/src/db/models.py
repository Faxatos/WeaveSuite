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
    endpoints = relationship("Endpoint", back_populates="spec", cascade="all, delete-orphan")

class Endpoint(Base):
    __tablename__ = "endpoints"
    __table_args__ = (
        UniqueConstraint('spec_id', 'path', 'method', name='uq_endpoint_spec_path_method'),
        Index('idx_endpoint_spec', 'spec_id'),
    )
    
    id = Column(Integer, primary_key=True)
    spec_id = Column(Integer, ForeignKey("openapi_specs.id", ondelete="CASCADE"), nullable=False)
    path = Column(String, nullable=False)  # e.g., "/users/{id}"
    method = Column(String, nullable=False)  # e.g., "GET", "POST"
    operation_id = Column(String, nullable=True)
    summary = Column(String, nullable=True)
    tags = Column(JSON, nullable=True)
    
    spec = relationship("OpenAPISpec", back_populates="endpoints")
    test_coverages = relationship("TestEndpointCoverage", back_populates="endpoint", cascade="all, delete-orphan")

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
    endpoint_coverages = relationship("TestEndpointCoverage", back_populates="test", cascade="all, delete-orphan")

class TestTemplate(Base):
    __tablename__ = "test_templates"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    template_code = Column(Text, nullable=False)  #code that comes before test functions
    
    tests = relationship("Test", back_populates="template")

class TestEndpointCoverage(Base):
    __tablename__ = "test_endpoint_coverages"
    __table_args__ = (
        Index('idx_coverage_test', 'test_id'),
        Index('idx_coverage_endpoint', 'endpoint_id'),
    )
    
    test_id = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"), primary_key=True)
    endpoint_id = Column(Integer, ForeignKey("endpoints.id", ondelete="CASCADE"), primary_key=True)
    
    test = relationship("Test", back_populates="endpoint_coverages")
    endpoint = relationship("Endpoint", back_populates="test_coverages")