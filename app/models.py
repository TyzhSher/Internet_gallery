"""SQLAlchemy модели базы данных для Internet Gallery."""
import enum
from sqlalchemy import (
    Column, Integer, String, ForeignKey,
    DateTime, Enum, Boolean, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class UserRole(str, enum.Enum):
    """Роли пользователей в системе."""
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


class PaintingType(str, enum.Enum):
    """Типы художественных работ."""
    OIL = "oil"
    WATERCOLOR = "watercolor"
    ACRYLIC = "acrylic"
    DIGITAL = "digital"
    SCULPTURE = "sculpture"
    OTHER = "other"


class User(Base):
    """Модель пользователя."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    favorite_artists = relationship(
        "UserFavoriteArtist", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    favorite_genres = relationship(
        "UserFavoriteGenre", 
        back_populates="user",
        cascade="all, delete-orphan"
    )


class FavoriteArtist(Base):
    """Справочник художников."""
    __tablename__ = "artists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    paintings = relationship("Painting", back_populates="artist")
    user_favorites = relationship(
        "UserFavoriteArtist", 
        back_populates="artist",
        cascade="all, delete-orphan"
    )


class FavoriteGenre(Base):
    """Справочник жанров."""
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    paintings = relationship("Painting", back_populates="genre")
    user_favorites = relationship(
        "UserFavoriteGenre", 
        back_populates="genre",
        cascade="all, delete-orphan"
    )


class UserFavoriteArtist(Base):
    """Связь пользователь-художник (избранное)."""
    __tablename__ = "user_favorite_artists"
    __table_args__ = (
        UniqueConstraint("user_id", "artist_id", name="uq_user_artist"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False)
    added_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    user = relationship("User", back_populates="favorite_artists")
    artist = relationship("FavoriteArtist", back_populates="user_favorites")


class UserFavoriteGenre(Base):
    """Связь пользователь-жанр (избранное)."""
    __tablename__ = "user_favorite_genres"
    __table_args__ = (
        UniqueConstraint("user_id", "genre_id", name="uq_user_genre"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    genre_id = Column(Integer, ForeignKey("genres.id"), nullable=False)
    added_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    user = relationship("User", back_populates="favorite_genres")
    genre = relationship("FavoriteGenre", back_populates="user_favorites")


class Painting(Base):
    """Модель картины в галерее."""
    __tablename__ = "paintings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False)
    genre_id = Column(Integer, ForeignKey("genres.id"), nullable=False)
    image_url = Column(String(500), nullable=False)
    year = Column(Integer, nullable=False)
    painting_type = Column(Enum(PaintingType), nullable=False)
    description = Column(String(1000), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    artist = relationship("FavoriteArtist", back_populates="paintings")
    genre = relationship("FavoriteGenre", back_populates="paintings")
