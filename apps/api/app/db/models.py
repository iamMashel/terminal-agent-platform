from datetime import UTC, datetime

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SessionModel(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

    messages: Mapped[list["MessageModel"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )
    commands: Mapped[list["CommandModel"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )


class MessageModel(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), index=True)
    role: Mapped[str] = mapped_column(String(32))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

    session: Mapped[SessionModel] = relationship(back_populates="messages")


class CommandModel(Base):
    __tablename__ = "commands"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), index=True)
    cmd: Mapped[str] = mapped_column(Text)
    risk: Mapped[str] = mapped_column(String(32))
    explanation: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="proposed")
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

    session: Mapped[SessionModel] = relationship(back_populates="commands")
    execution_logs: Mapped[list["ExecutionLogModel"]] = relationship(
        back_populates="command",
        cascade="all, delete-orphan",
    )


class ExecutionLogModel(Base):
    __tablename__ = "execution_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    command_id: Mapped[str] = mapped_column(ForeignKey("commands.id"), index=True)
    status: Mapped[str] = mapped_column(String(32))
    exit_code: Mapped[int] = mapped_column(Integer)
    output: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

    command: Mapped[CommandModel] = relationship(back_populates="execution_logs")
