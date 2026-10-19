"""PostgreSQL/PostGIS-ready SQLAlchemy 2 domain models for SHUFFL."""
from datetime import datetime
from typing import Any
from uuid import uuid4
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

def uid() -> str:
    return str(uuid4())

class User(Base):
    __tablename__ = 'users'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    email: Mapped[str | None] = mapped_column(String(320), unique=True)
    phone: Mapped[str | None] = mapped_column(String(32), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    profile: Mapped['Profile | None'] = relationship(back_populates='user', uselist=False)

class Profile(Base):
    __tablename__ = 'profiles'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), unique=True)
    display_name: Mapped[str] = mapped_column(String(120), default='')
    pronouns: Mapped[str | None] = mapped_column(String(40))
    age: Mapped[int | None] = mapped_column(Integer)
    city: Mapped[str] = mapped_column(String(100), default='New Delhi')
    bio: Mapped[str] = mapped_column(Text, default='')
    preferences: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    user: Mapped[User] = relationship(back_populates='profile')

class AssessmentSession(Base):
    __tablename__ = 'assessment_sessions'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    scores_raw: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    scores_rescaled: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    vibe_name: Mapped[str | None] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(24), default='active')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    exposures: Mapped[list['CardExposure']] = relationship(cascade='all, delete-orphan')

class CardExposure(Base):
    __tablename__ = 'card_exposures'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    assessment_id: Mapped[str] = mapped_column(ForeignKey('assessment_sessions.id'))
    card_id: Mapped[str] = mapped_column(String(80))
    factor: Mapped[str] = mapped_column(String(20))
    action: Mapped[str | None] = mapped_column(String(20))
    score: Mapped[int | None] = mapped_column(Integer)
    ended_by: Mapped[str | None] = mapped_column(String(20))
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    exposure_index: Mapped[int] = mapped_column(Integer, default=0)

class Plan(Base):
    __tablename__ = 'plans'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    room_id: Mapped[str | None] = mapped_column(ForeignKey('rooms.id'))
    style: Mapped[str] = mapped_column(String(80), default='Open Night')
    chemistry: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(24), default='draft')
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    stops: Mapped[list['PlanStop']] = relationship(cascade='all, delete-orphan')

class PlanStop(Base):
    __tablename__ = 'plan_stops'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    plan_id: Mapped[str] = mapped_column(ForeignKey('plans.id'))
    stop_index: Mapped[int] = mapped_column(Integer)
    venue_id: Mapped[str | None] = mapped_column(ForeignKey('venues.id'))
    venue_type: Mapped[str] = mapped_column(String(80))
    duration_share: Mapped[float] = mapped_column(Float, default=0)
    arrival_window: Mapped[str | None] = mapped_column(String(80))

class Venue(Base):
    __tablename__ = 'venues'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String(160))
    city: Mapped[str] = mapped_column(String(100), default='New Delhi')
    area: Mapped[str] = mapped_column(String(120), default='')
    venue_type: Mapped[str] = mapped_column(String(80))
    vibe_scores: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    preference_scores: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    pol_sense: Mapped[str] = mapped_column(String(16), default='both')
    active: Mapped[bool] = mapped_column(Boolean, default=True)

class Room(Base):
    __tablename__ = 'rooms'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    host_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    title: Mapped[str] = mapped_column(String(160))
    visibility: Mapped[str] = mapped_column(String(24), default='friends')
    status: Mapped[str] = mapped_column(String(24), default='draft')

class JoinRequest(Base):
    __tablename__ = 'join_requests'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    room_id: Mapped[str] = mapped_column(ForeignKey('rooms.id'))
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    status: Mapped[str] = mapped_column(String(24), default='pending')
    note: Mapped[str] = mapped_column(Text, default='')

class Capsule(Base):
    __tablename__ = 'capsules'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    room_id: Mapped[str] = mapped_column(ForeignKey('rooms.id'))
    status: Mapped[str] = mapped_column(String(32), default='awaiting_approval')
    members: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

class Conversation(Base):
    __tablename__ = 'conversations'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    room_id: Mapped[str | None] = mapped_column(ForeignKey('rooms.id'))
    kind: Mapped[str] = mapped_column(String(20), default='group')
    title: Mapped[str] = mapped_column(String(160), default='')
    messages: Mapped[list['Message']] = relationship(cascade='all, delete-orphan')

class Message(Base):
    __tablename__ = 'messages'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    conversation_id: Mapped[str] = mapped_column(ForeignKey('conversations.id'))
    sender_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class Notification(Base):
    __tablename__ = 'notifications'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    kind: Mapped[str] = mapped_column(String(40))
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    read: Mapped[bool] = mapped_column(Boolean, default=False)

class Report(Base):
    __tablename__ = 'reports'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    reporter_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    target_id: Mapped[str] = mapped_column(String(36))
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(24), default='received')

class PrivacySettings(Base):
    __tablename__ = 'privacy_settings'
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), primary_key=True)
    location_sharing: Mapped[bool] = mapped_column(Boolean, default=False)
    approximate_presence: Mapped[bool] = mapped_column(Boolean, default=True)
    discoverability: Mapped[bool] = mapped_column(Boolean, default=True)

class FeatureFlag(Base):
    __tablename__ = 'feature_flags'
    name: Mapped[str] = mapped_column(String(80), primary_key=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)


# Canonical MVP collaboration domain. These tables replace the old JSON-only
# room/capsule metadata as the source of truth for the gathering flow.
class Friendship(Base):
    __tablename__ = 'friendships'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    requester_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    addressee_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    status: Mapped[str] = mapped_column(String(24), default='pending')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class Gathering(Base):
    __tablename__ = 'gatherings'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    owner_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    name: Mapped[str] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(32), default='gathering')
    wheel_owner_id: Mapped[str | None] = mapped_column(ForeignKey('users.id'))
    conversation_id: Mapped[str | None] = mapped_column(ForeignKey('conversations.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class GatheringMember(Base):
    __tablename__ = 'gathering_members'
    gathering_id: Mapped[str] = mapped_column(ForeignKey('gatherings.id'), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), primary_key=True)
    role: Mapped[str] = mapped_column(String(24), default='member')
    invite_status: Mapped[str] = mapped_column(String(24), default='pending')
    skeleton: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    joined_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

class WheelRequest(Base):
    __tablename__ = 'wheel_requests'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    gathering_id: Mapped[str] = mapped_column(ForeignKey('gatherings.id'))
    requester_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    status: Mapped[str] = mapped_column(String(24), default='pending')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class GatheringProposal(Base):
    __tablename__ = 'gathering_proposals'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    gathering_id: Mapped[str] = mapped_column(ForeignKey('gatherings.id'))
    kind: Mapped[str] = mapped_column(String(32))
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(24), default='pending')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
