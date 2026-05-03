from pydantic import BaseModel, EmailStr, Field, field_validator, HttpUrl, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum
import re

class PaintingType(str, Enum):
    oil = "oil"
    watercolor = "watercolor"
    acrylic = "acrylic"
    digital = "digital"
    sculpture = "sculpture"
    other = "other"

class UserRole(str, Enum):
    user = "user"
    moderator = "moderator"
    admin = "admin"

# === Auth ===
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username can only contain letters, numbers, underscores and hyphens")
        return v.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        errs = []
        if len(v) < 8: errs.append("at least 8 chars")
        if not any(c.isupper() for c in v): errs.append("uppercase")
        if not any(c.islower() for c in v): errs.append("lowercase")
        if not any(c.isdigit() for c in v): errs.append("digit")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v): errs.append("special char")
        if errs: raise ValueError(f"Password must contain: {', '.join(errs)}")
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: EmailStr
    role: UserRole
    created_at: datetime

# === Catalog ===
class ArtistBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
class ArtistResponse(ArtistBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

class GenreBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
class GenreResponse(GenreBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

# === Paintings: REQUEST schemas (input) ===
class PaintingCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, strip_whitespace=True)
    artist_name: str = Field(..., min_length=2, max_length=100, strip_whitespace=True)  # ← для ввода
    genre_name: str = Field(..., min_length=2, max_length=50, strip_whitespace=True)    # ← для ввода
    image_url: HttpUrl
    year: int = Field(..., ge=1000, le=2100)
    painting_type: PaintingType
    description: Optional[str] = Field(None, max_length=1000, strip_whitespace=True)

    @field_validator("title", "artist_name", "genre_name")
    @classmethod
    def sanitize_text(cls, v: str) -> str:
        if re.search(r"[;'\"]|--|/\*|\*/", v, re.I):
            raise ValueError("Invalid characters detected")
        return v.strip()

class PaintingUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    artist_name: Optional[str] = Field(None, min_length=2, max_length=100)
    genre_name: Optional[str] = Field(None, min_length=2, max_length=50)
    image_url: Optional[HttpUrl] = None
    year: Optional[int] = Field(None, ge=1000, le=2100)
    painting_type: Optional[PaintingType] = None
    description: Optional[str] = Field(None, max_length=1000)

# === Paintings: RESPONSE schema (output) ===
class PaintingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    # ← НЕТ artist_name/genre_name на верхнем уровне!
    image_url: str  # HttpUrl можно упростить до str для ответа
    year: int
    painting_type: PaintingType
    description: Optional[str]
    created_at: datetime
    # ← Вложенные объекты художника и жанра
    artist: ArtistResponse
    genre: GenreResponse

# === Favorites ===
class FavoriteArtistAdd(BaseModel): artist_name: str = Field(..., min_length=2, max_length=100)
class FavoriteGenreAdd(BaseModel): genre_name: str = Field(..., min_length=2, max_length=50)
class FavoriteArtistResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; artist: ArtistResponse; added_at: datetime
class FavoriteGenreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; genre: GenreResponse; added_at: datetime

# === Recommendations & Analytics ===
class RecommendationCriteria(str, Enum):
    by_genre = "by_genre"
    by_artist = "by_artist"
    by_both = "by_both"

class RecommendationRequest(BaseModel): criteria: RecommendationCriteria
class RecommendationResponse(BaseModel):
    paintings: List[PaintingResponse]
    criteria_used: str
    total_count: int

class ExplainResponse(BaseModel):
    painting_id: int
    painting_title: str
    total_score: float
    factors: List[dict]
    algorithm_version: str

class GalleryStats(BaseModel):
    total_paintings: int
    total_artists: int
    total_genres: int
    paintings_by_type: dict
    paintings_by_decade: dict
