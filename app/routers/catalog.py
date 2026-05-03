from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, models, schemas
from app.auth import require_roles

router = APIRouter(prefix="/api/catalog", tags=["catalog"])

@router.get("/artists", response_model=list[schemas.ArtistResponse])
def list_artists(db: Session = Depends(get_db)): return crud.get_all_artists(db)

@router.post("/artists", response_model=schemas.ArtistResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles("moderator", "admin"))])
def create_artist(a: schemas.ArtistBase, db: Session = Depends(get_db)):
    ex = crud.get_artist_by_name(db, a.name)
    if ex: raise Exception("400: Artist exists")
    art = models.FavoriteArtist(name=a.name); db.add(art); db.commit(); db.refresh(art); return art

@router.get("/genres", response_model=list[schemas.GenreResponse])
def list_genres(db: Session = Depends(get_db)): return crud.get_all_genres(db)

@router.post("/genres", response_model=schemas.GenreResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles("moderator", "admin"))])
def create_genre(g: schemas.GenreBase, db: Session = Depends(get_db)):
    ex = crud.get_genre_by_name(db, g.name)
    if ex: raise Exception("400: Genre exists")
    gen = models.FavoriteGenre(name=g.name); db.add(gen); db.commit(); db.refresh(gen); return gen