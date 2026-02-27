from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Repo(Base):
    __tablename__ = "repos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    local_path: Mapped[str] = mapped_column(String(512))
    policy_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    runs: Mapped[list[Run]] = relationship(back_populates="repo")


class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    repo_id: Mapped[int] = mapped_column(ForeignKey("repos.id"), index=True)
    cron: Mapped[str] = mapped_column(String(128))
    job_name: Mapped[str] = mapped_column(String(64))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    repo_id: Mapped[int] = mapped_column(ForeignKey("repos.id"), index=True)
    job_name: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(64), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    branch: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pr_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    artifacts_path: Mapped[str] = mapped_column(String(512))
    summary_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    repo: Mapped[Repo] = relationship(back_populates="runs")


class Budget(Base):
    __tablename__ = "budgets"

    day: Mapped[str] = mapped_column(String(16), primary_key=True)
    repo_id: Mapped[int] = mapped_column(ForeignKey("repos.id"), primary_key=True)
    minutes_used: Mapped[float] = mapped_column(Float, default=0)
    prs_created: Mapped[int] = mapped_column(Integer, default=0)


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    repo_id: Mapped[int] = mapped_column(ForeignKey("repos.id"), index=True)
    job_name: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(64), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    config_json: Mapped[str] = mapped_column(Text)
