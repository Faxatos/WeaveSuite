from sqlalchemy import Column, Float, DateTime, Integer, String, JSON, ForeignKey, UniqueConstraint, JSON, Index
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
    x = Column(Float, default=0.0)
    y = Column(Float, default=0.0)
    service_type = Column(String, default='microservice')
    openapi_path = Column(String)
    specs = relationship("OpenAPISpec", back_populates="microservice")
    outgoing_links = relationship("Link", foreign_keys="Link.source_id", back_populates="source")
    incoming_links = relationship("Link", foreign_keys="Link.target_id", back_populates="target")

class Link(Base):
    __tablename__ = "links"
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("microservices.id"), nullable=False)
    target_id = Column(Integer, ForeignKey("microservices.id"), nullable=False)
    label = Column(String)
    
    source = relationship("Microservice", foreign_keys=[source_id], back_populates="outgoing_links")
    target = relationship("Microservice", foreign_keys=[target_id], back_populates="incoming_links")

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
    test_failures = relationship("TestProxyFailure", back_populates="proxy_modification")

class Test(Base):
    __tablename__ = "tests"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    code = Column(String)  #generated test code
    spec_id = Column(Integer, ForeignKey("openapi_specs.id"))  #link to OpenAPI spec
    spec = relationship("OpenAPISpec")
    last_execution = Column(DateTime, nullable=True)
    status = Column(String, nullable=True)  # passed, failed, skipped, error
    execution_time = Column(Float, nullable=True)
    error_message = Column(String, nullable=True)
    services_visited = Column(JSON, nullable=True)  # JSON array as string
    proxy_failures = relationship("TestProxyFailure", back_populates="test", cascade="all, delete-orphan", passive_deletes=True)
    template = relationship("TestTemplate", back_populates="tests")

class TestTemplate(Base):
    __tablename__ = "test_templates"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    template_code = Column(Text, nullable=False)  #code that comes before test functions
    
    tests = relationship("Test", back_populates="template")

class TestProxyFailure(Base):
    __tablename__ = "test_proxy_failures"
    __table_args__ = (
        Index('idx_test_proxy_failure', 'test_id', 'proxy_modification_id'),
    )
    #composite primary key ensures uniqueness
    test_id               = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"), primary_key=True)
    proxy_modification_id = Column(Integer, ForeignKey("proxy_modifications.id", ondelete="CASCADE"), primary_key=True)
    #back‑refs into Test and ProxyModification
    test               = relationship("Test", back_populates="proxy_failures")
    proxy_modification = relationship("ProxyModification", back_populates="test_failures")