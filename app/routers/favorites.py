from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas, models
from app.auth import get_current_user

router = APIRouter(prefix="/api/favorites", tags=["favorites"])

@router.post("/artists", response_model=schemas.FavoriteArtistResponse, status_code=status.HTTP_201_CREATED)
def add_artist(req: schemas.FavoriteArtistAdd, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return crud.add_favorite_artist(db, user.id, req.artist_name)

@router.delete("/artists/{name}", status_code=status.HTTP_204_NO_CONTENT)
def del_artist(name: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    crud.remove_favorite_artist(db, user.id, name)

@router.get("/artists", response_model=list[schemas.ArtistResponse])
def get_artists(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return crud.get_user_fav_artists(db, user.id)

@router.post("/genres", response_model=schemas.FavoriteGenreResponse, status_code=status.HTTP_201_CREATED)
def add_genre(req: schemas.FavoriteGenreAdd, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return crud.add_favorite_genre(db, user.id, req.genre_name)

@router.delete("/genres/{name}", status_code=status.HTTP_204_NO_CONTENT)
def del_genre(name: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    crud.remove_favorite_genre(db, user.id, name)

@router.get("/genres", response_model=list[schemas.GenreResponse])
def get_genres(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return crud.get_user_fav_genres(db, user.id)