from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import crud, schemas, models
from app.auth import get_current_user

router = APIRouter(prefix="/api/paintings", tags=["paintings"])

@router.post("", response_model=schemas.PaintingResponse, status_code=status.HTTP_201_CREATED)
def create(p: schemas.PaintingCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return crud.create_painting(db, p)

@router.get("", response_model=List[schemas.PaintingResponse])
def list_all(skip: int=0, limit: int=20, db: Session = Depends(get_db)):
    return db.query(models.Painting).offset(skip).limit(limit).all()

@router.get("/artist/{name}", response_model=List[schemas.PaintingResponse])
def by_artist(name: str, db: Session = Depends(get_db)): return crud.get_paintings_by_artist(db, name)

@router.get("/genre/{name}", response_model=List[schemas.PaintingResponse])
def by_genre(name: str, db: Session = Depends(get_db)): return crud.get_paintings_by_genre(db, name)

@router.get("/type/{ptype}", response_model=List[schemas.PaintingResponse])
def by_type(ptype: models.PaintingType, db: Session = Depends(get_db)):
    return db.query(models.Painting).filter(models.Painting.painting_type==ptype).all()

@router.get("/search", response_model=List[schemas.PaintingResponse])
def search(q: str, artist: str=None, genre: str=None, y_from: int=None, y_to: int=None, 
           ptype: models.PaintingType=None, skip: int=0, limit: int=20, db: Session = Depends(get_db)):
    return crud.search_paintings(db, q, artist, genre, y_from, y_to, ptype, skip, limit)

@router.get("/{pid}", response_model=schemas.PaintingResponse)
def get_one(pid: int, db: Session = Depends(get_db)):
    p = crud.get_painting(db, pid)
    if not p: raise Exception("404: Painting not found")
    return p

@router.put("/{pid}", response_model=schemas.PaintingResponse)
def update(pid: int, upd: schemas.PaintingUpdate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return crud.update_painting(db, pid, upd)

@router.delete("/{pid}", status_code=status.HTTP_204_NO_CONTENT)
def delete(pid: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    crud.delete_painting(db, pid)
