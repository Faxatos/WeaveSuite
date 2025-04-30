from sqlalchemy import Column, Boolean, DateTime, Integer, String, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from src.db.database import Base

class Microservice(Base):
    __tablename__ = "microservices"
    __table_args__ = (
        UniqueConstraint('name', 'namespace', name='uq_microservice_name_namespace'),
    )
    id = Column(Integer, primary_key=True)
    name = Column(String)
    namespace = Column(String)
    endpoint = Column(String, unique=True)
    specs = relationship("OpenAPISpec", back_populates="microservice")

class OpenAPISpec(Base):
    __tablename__ = "openapi_specs"
    id = Column(Integer, primary_key=True)
    spec = Column(JSON)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    microservice_id = Column(Integer, ForeignKey("microservices.id"))
    microservice = relationship("Microservice", back_populates="specs")
    proxy_modifications = relationship("ProxyModification", back_populates="spec")

class ProxyModification(Base):
    __tablename__ = "proxy_modifications"
    id = Column(Integer, primary_key=True)
    config = Column(JSON)  
    spec_id = Column(Integer, ForeignKey("openapi_specs.id"))  # 1:N link
    spec = relationship("OpenAPISpec", back_populates="proxy_modifications")

class Test(Base):
    __tablename__ = "tests"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    code = Column(String)  #generated test code
    spec_id = Column(Integer, ForeignKey("openapi_specs.id"))  #link to OpenAPI spec
    spec = relationship("OpenAPISpec")
    result = Column(Boolean, nullable=True)
    executed_at = Column(DateTime, nullable=True)

class TestProxyFailure(Base):
    __tablename__ = "test_proxy_failures"
    #composite primary key ensures uniqueness
    test_id               = Column(Integer, ForeignKey("tests.id"), primary_key=True)
    proxy_modification_id = Column(Integer, ForeignKey("proxy_modifications.id"), primary_key=True)
    #back‑refs into Test and ProxyModification
    test               = relationship("Test", back_populates="proxy_failures")
    proxy_modification = relationship("ProxyModification", back_populates="test_failures")