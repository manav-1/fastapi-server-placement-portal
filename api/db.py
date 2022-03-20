from enum import Enum
from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    Text,
    ForeignKey,
    MetaData,
    BigInteger,
    DECIMAL, Boolean,
    ARRAY
)
from sqlalchemy.types import Enum as SqlalchemyEnum, DateTime, Date
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import func, expression
from datetime import datetime, date

global_metadata = MetaData(schema="global")


class utcnow(expression.FunctionElement):
    type = DateTime()


class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"


class ContactPosition(Enum):
    CORE = 'core'
    SECRETARY = 'secretary'


@compiles(utcnow, "postgresql")
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


User: Table = Table(
    'user',
    global_metadata,
    Column("user_id", Integer, primary_key=True),
    Column("user_name", Text, nullable=False),
    Column("user_email", Text, unique=True, nullable=False),
    Column("user_password", Text, nullable=False),
    Column('user_mobile', BigInteger, nullable=False),
    Column("user_role", SqlalchemyEnum(UserRole), nullable=False),
    Column("user_created_at", DateTime, server_default=utcnow()),
    Column("user_updated_at", DateTime,
           server_default=utcnow(), server_onupdate=utcnow()),
)

UserProfile: Table = Table(
    'user_profile',
    global_metadata,
    Column("user_profile_id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("user.user_id"), nullable=False),
    Column('stream_id', Integer, ForeignKey(
        'stream.stream_id'), nullable=False),
    Column('marks_10', DECIMAL(), nullable=False),
    Column('marks_12', DECIMAL(), nullable=False),
    Column('marks_ug', DECIMAL(), nullable=False),
    Column('additional_info', Text, nullable=False),
    Column('resume_name', Text, nullable=False),
    Column('resume_path', Text, nullable=False),
    Column('user_profile_created_at', DateTime, server_default=utcnow()),
    Column('user_profile_updated_at', DateTime,
           server_default=utcnow(), server_onupdate=utcnow()),
)


Projects: Table = Table(
    'project',
    global_metadata,
    Column("project_id", Integer, primary_key=True),
    Column("project_name", Text, nullable=False),
    Column("project_url", Text, nullable=False),
    Column("created_by", Integer, ForeignKey("user.user_id"), nullable=False),
    Column("project_created_at", DateTime, server_default=utcnow()),
    Column("project_updated_at", DateTime,
           server_default=utcnow(), server_onupdate=utcnow()),

)

Streams: Table = Table(
    'stream',
    global_metadata,
    Column("stream_id", Integer, primary_key=True),
    Column("stream_name", Text, nullable=False),
    Column("stream_created_at", DateTime, server_default=utcnow()),
    Column("stream_updated_at", DateTime,
           server_default=utcnow(), server_onupdate=utcnow()),
)

Placements: Table = Table(
    'placement',
    global_metadata,
    Column("placement_id", Integer, primary_key=True),
    Column('placement_company_name', Text, nullable=False),
    Column('placement_profile', Text, nullable=False),
    Column('company_url', Text, nullable=False),
    Column('image_url', Text, nullable=False),
    Column('linkedin_url', Text, nullable=False),
    Column('jd_url', Text, nullable=False),
    Column('deadline', DateTime, nullable=False),
    Column('is_active', Boolean, nullable=False),
    Column('created_at', DateTime, server_default=utcnow()),
    Column('updated_at', DateTime,
           server_default=utcnow(), server_onupdate=utcnow()),
    Column('stream_ids', ARRAY(Integer), nullable=False),
)


PlacementUserLinking: Table = Table(
    'placement_user_linking',
    global_metadata,
    Column("placement_user_linking_id", Integer, primary_key=True),
    Column("placement_id", Integer, ForeignKey("placement.placement_id"),
           nullable=False),
    Column("user_id", Integer, ForeignKey("user.user_id"), nullable=False),
    Column("placement_user_linking_created_at", DateTime,
           server_default=utcnow()),
    Column("placement_user_linking_updated_at", DateTime,
           server_default=utcnow(), server_onupdate=utcnow()),
)

EmailData: Table = Table(
    'email_data',
    global_metadata,
    Column("email_data_id", Integer, primary_key=True),
    Column("hr_email", Text, nullable=False),
    Column("hr_name", Text, nullable=False),
    Column('email_sent_at', DateTime, nullable=False,
           server_default=utcnow(), server_onupdate=utcnow()),
    Column('email_sent_by_user_id', Integer, ForeignKey(User.c.user_id),
           nullable=False),
    Column('email_type', Boolean, nullable=False),
    Column('email_data_created_at', DateTime, server_default=utcnow()),
    Column('email_data_updated_at', DateTime,
           server_default=utcnow(), server_onupdate=utcnow()),
)

Contact: Table = Table(
    'contact',
    global_metadata,
    Column("contact_id", Integer, primary_key=True),
    Column("contact_name", Text, nullable=False),
    Column("contact_email", Text, nullable=False),
    Column("contact_mobile", BigInteger, nullable=False),
    Column("contact_position", SqlalchemyEnum(
        ContactPosition), nullable=False),
    Column("contact_created_at", DateTime, server_default=utcnow()),
    Column("contact_updated_at", DateTime,
           server_default=utcnow(), server_onupdate=utcnow()),
)
