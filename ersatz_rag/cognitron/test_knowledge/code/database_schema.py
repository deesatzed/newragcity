"""
Medical database schema for patient management system
Implements HIPAA-compliant data models with audit trails
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional

Base = declarative_base()

class Patient(Base):
    """
    Patient record with HIPAA compliance
    Contains PHI (Protected Health Information)
    """
    __tablename__ = 'patients'
    
    id = Column(String, primary_key=True)
    medical_record_number = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    social_security_number = Column(String, nullable=True)  # Encrypted
    phone_number = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    
    # Medical information
    blood_type = Column(String, nullable=True)
    allergies = Column(Text, nullable=True)
    chronic_conditions = Column(Text, nullable=True)
    emergency_contact = Column(Text, nullable=True)
    
    # Compliance fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    consent_signed = Column(Boolean, default=False)
    hipaa_authorization = Column(DateTime, nullable=True)
    
    # Relationships
    appointments = relationship("Appointment", back_populates="patient")
    medical_records = relationship("MedicalRecord", back_populates="patient")

class MedicalProfessional(Base):
    """
    Medical professional with credentials and licensing
    """
    __tablename__ = 'medical_professionals'
    
    id = Column(String, primary_key=True)
    license_number = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    specialty = Column(String, nullable=False)
    credentials = Column(String, nullable=False)  # MD, DO, NP, PA, etc.
    
    # Contact information
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    department = Column(String, nullable=True)
    
    # License and certification
    license_expiry = Column(DateTime, nullable=False)
    board_certification = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Compliance
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    appointments = relationship("Appointment", back_populates="provider")
    medical_records = relationship("MedicalRecord", back_populates="provider")

class Appointment(Base):
    """
    Medical appointment scheduling with conflict resolution
    """
    __tablename__ = 'appointments'
    
    id = Column(String, primary_key=True)
    patient_id = Column(String, ForeignKey('patients.id'), nullable=False)
    provider_id = Column(String, ForeignKey('medical_professionals.id'), nullable=False)
    
    # Scheduling
    appointment_date = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=30)
    appointment_type = Column(String, nullable=False)  # consultation, follow-up, procedure
    status = Column(String, default='scheduled')  # scheduled, completed, cancelled, no-show
    
    # Clinical information
    chief_complaint = Column(Text, nullable=True)
    appointment_notes = Column(Text, nullable=True)
    
    # Billing and insurance
    insurance_authorization = Column(String, nullable=True)
    copay_amount = Column(Integer, nullable=True)  # in cents
    
    # Compliance
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    provider = relationship("MedicalProfessional", back_populates="appointments")

class MedicalRecord(Base):
    """
    Electronic medical record with full audit trail
    Highest level of HIPAA compliance required
    """
    __tablename__ = 'medical_records'
    
    id = Column(String, primary_key=True)
    patient_id = Column(String, ForeignKey('patients.id'), nullable=False)
    provider_id = Column(String, ForeignKey('medical_professionals.id'), nullable=False)
    appointment_id = Column(String, ForeignKey('appointments.id'), nullable=True)
    
    # Clinical content
    record_type = Column(String, nullable=False)  # progress_note, discharge_summary, consultation
    subjective = Column(Text, nullable=True)  # Patient's description
    objective = Column(Text, nullable=True)  # Clinical findings
    assessment = Column(Text, nullable=True)  # Medical assessment
    plan = Column(Text, nullable=True)  # Treatment plan
    
    # Vital signs and measurements
    vital_signs = Column(Text, nullable=True)  # JSON format
    medications_prescribed = Column(Text, nullable=True)
    procedures_performed = Column(Text, nullable=True)
    
    # Diagnosis codes
    icd10_codes = Column(Text, nullable=True)  # Primary and secondary diagnoses
    cpt_codes = Column(Text, nullable=True)  # Procedure codes for billing
    
    # Quality and compliance
    record_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_signed = Column(Boolean, default=False)
    signed_at = Column(DateTime, nullable=True)
    
    # Audit trail for HIPAA compliance
    accessed_by = Column(Text, nullable=True)  # JSON of access log
    last_accessed = Column(DateTime, nullable=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="medical_records")
    provider = relationship("MedicalProfessional", back_populates="medical_records")

class AuditLog(Base):
    """
    HIPAA-compliant audit logging for all PHI access
    Critical for regulatory compliance
    """
    __tablename__ = 'audit_logs'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    user_type = Column(String, nullable=False)  # medical_professional, admin, patient
    
    # Access details
    action = Column(String, nullable=False)  # view, create, update, delete, export
    resource_type = Column(String, nullable=False)  # patient, medical_record, appointment
    resource_id = Column(String, nullable=False)
    
    # Technical details
    ip_address = Column(String, nullable=False)
    user_agent = Column(String, nullable=True)
    session_id = Column(String, nullable=True)
    
    # Result and context
    success = Column(Boolean, nullable=False)
    failure_reason = Column(String, nullable=True)
    additional_context = Column(Text, nullable=True)
    
    # Timing
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<AuditLog(user={self.user_id}, action={self.action}, resource={self.resource_type}:{self.resource_id})>"