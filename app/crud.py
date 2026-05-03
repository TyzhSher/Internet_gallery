from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException
from typing import Optional, List
from app import models, schemas
from app.auth import get_password_hash, verify_password

# === Users ===
def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    if get_user_by_username(db, user.username): raise HTTPException(400, detail="Username taken")
    if get_user_by_email(db, user.email): raise HTTPException(400, detail="Email taken")
    db_user = models.User(username=user.username, email=user.email, hashed_password=get_password_hash(user.password))
    db.add(db_user); db.commit(); db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()
def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()
def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password): return None
    return user

# === Artists/Genres ===
def get_or_create_artist(db: Session, name: str) -> models.FavoriteArtist:
    artist = db.query(models.FavoriteArtist).filter(models.FavoriteArtist.name.ilike(name.strip())).first()
    if not artist:
        artist = models.FavoriteArtist(name=name.strip().title()); db.add(artist); db.commit(); db.refresh(artist)
    return artist
def get_artist_by_name(db: Session, name: str) -> Optional[models.FavoriteArtist]:
    return db.query(models.FavoriteArtist).filter(models.FavoriteArtist.name.ilike(name.strip())).first()
def get_all_artists(db: Session) -> List[models.FavoriteArtist]:
    return db.query(models.FavoriteArtist).order_by(models.FavoriteArtist.name).all()

def get_or_create_genre(db: Session, name: str) -> models.FavoriteGenre:
    genre = db.query(models.FavoriteGenre).filter(models.FavoriteGenre.name.ilike(name.strip())).first()
    if not genre:
        genre = models.FavoriteGenre(name=name.strip().title()); db.add(genre); db.commit(); db.refresh(genre)
    return genre
def get_genre_by_name(db: Session, name: str) -> Optional[models.FavoriteGenre]:
    return db.query(models.FavoriteGenre).filter(models.FavoriteGenre.name.ilike(name.strip())).first()
def get_all_genres(db: Session) -> List[models.FavoriteGenre]:
    return db.query(models.FavoriteGenre).order_by(models.FavoriteGenre.name).all()

# === Paintings ===
def create_painting(db: Session, p: schemas.PaintingCreate) -> models.Painting:
    art = get_or_create_artist(db, p.artist_name)
    gen = get_or_create_genre(db, p.genre_name)
    db_p = models.Painting(title=p.title, artist_id=art.id, genre_id=gen.id, image_url=str(p.image_url), 
                           year=p.year, painting_type=p.painting_type, description=p.description)
    db.add(db_p); db.commit(); db.refresh(db_p); return db_p

def get_painting(db: Session, pid: int) -> Optional[models.Painting]:
    return db.query(models.Painting).filter(models.Painting.id == pid).first()

def update_painting(db: Session, pid: int, update: schemas.PaintingUpdate) -> models.Painting:
    p = get_painting(db, pid)
    if not p: raise HTTPException(404, detail="Painting not found")
    data = update.model_dump(exclude_unset=True)
    for k, v in data.items():
        if k == "artist_name": p.artist_id = get_or_create_artist(db, v).id
        elif k == "genre_name": p.genre_id = get_or_create_genre(db, v).id
        else: setattr(p, k, v)
    db.commit(); db.refresh(p); return p

def delete_painting(db: Session, pid: int) -> bool:
    p = get_painting(db, pid)
    if not p: raise HTTPException(404, detail="Painting not found")
    db.delete(p); db.commit(); return True

def get_paintings_by_artist(db: Session, name: str) -> List[models.Painting]:
    art = get_artist_by_name(db, name)
    return db.query(models.Painting).filter(models.Painting.artist_id == art.id).all() if art else []

def get_paintings_by_genre(db: Session, name: str) -> List[models.Painting]:
    gen = get_genre_by_name(db, name)
    return db.query(models.Painting).filter(models.Painting.genre_id == gen.id).all() if gen else []

def search_paintings(db: Session, q: str, artist: str=None, genre: str=None, 
                     y_from: int=None, y_to: int=None, ptype: models.PaintingType=None, 
                     skip: int=0, limit: int=20) -> List[models.Painting]:
    qry = db.query(models.Painting)
    if q: qry = qry.filter(or_(models.Painting.title.ilike(f"%{q}%"), models.Painting.description.ilike(f"%{q}%")))
    if artist: a = get_artist_by_name(db, artist); qry = qry.filter(models.Painting.artist_id == a.id) if a else qry
    if genre: g = get_genre_by_name(db, genre); qry = qry.filter(models.Painting.genre_id == g.id) if g else qry
    if y_from: qry = qry.filter(models.Painting.year >= y_from)
    if y_to: qry = qry.filter(models.Painting.year <= y_to)
    if ptype: qry = qry.filter(models.Painting.painting_type == ptype)
    return qry.offset(skip).limit(limit).all()

# === Favorites ===
def add_favorite_artist(db: Session, uid: int, name: str) -> models.UserFavoriteArtist:
    art = get_or_create_artist(db, name)
    ex = db.query(models.UserFavoriteArtist).filter(and_(models.UserFavoriteArtist.user_id==uid, models.UserFavoriteArtist.artist_id==art.id)).first()
    if ex: raise HTTPException(400, detail=f"Artist '{art.name}' already in favorites")
    fav = models.UserFavoriteArtist(user_id=uid, artist_id=art.id); db.add(fav); db.commit(); db.refresh(fav); return fav

def add_favorite_genre(db: Session, uid: int, name: str) -> models.UserFavoriteGenre:
    gen = get_or_create_genre(db, name)
    ex = db.query(models.UserFavoriteGenre).filter(and_(models.UserFavoriteGenre.user_id==uid, models.UserFavoriteGenre.genre_id==gen.id)).first()
    if ex: raise HTTPException(400, detail=f"Genre '{gen.name}' already in favorites")
    fav = models.UserFavoriteGenre(user_id=uid, genre_id=gen.id); db.add(fav); db.commit(); db.refresh(fav); return fav

def remove_favorite_artist(db: Session, uid: int, name: str) -> bool:
    art = get_artist_by_name(db, name)
    if not art: raise HTTPException(404, detail="Artist not found")
    fav = db.query(models.UserFavoriteArtist).filter(and_(models.UserFavoriteArtist.user_id==uid, models.UserFavoriteArtist.artist_id==art.id)).first()
    if not fav: raise HTTPException(404, detail="Artist not in favorites")
    db.delete(fav); db.commit(); return True

def remove_favorite_genre(db: Session, uid: int, name: str) -> bool:
    gen = get_genre_by_name(db, name)
    if not gen: raise HTTPException(404, detail="Genre not found")
    fav = db.query(models.UserFavoriteGenre).filter(and_(models.UserFavoriteGenre.user_id==uid, models.UserFavoriteGenre.genre_id==gen.id)).first()
    if not fav: raise HTTPException(404, detail="Genre not in favorites")
    db.delete(fav); db.commit(); return True

def get_user_fav_artists(db: Session, uid: int) -> List[models.FavoriteArtist]:
    return [f.artist for f in db.query(models.UserFavoriteArtist).filter(models.UserFavoriteArtist.user_id==uid).all()]
def get_user_fav_genres(db: Session, uid: int) -> List[models.FavoriteGenre]:
    return [f.genre for f in db.query(models.UserFavoriteGenre).filter(models.UserFavoriteGenre.user_id==uid).all()]