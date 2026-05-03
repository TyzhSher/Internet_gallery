from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/gallery", response_model=schemas.GalleryStats)
def gallery_stats(db: Session = Depends(get_db)):
    return schemas.GalleryStats(
        total_paintings=db.query(func.count(models.Painting.id)).scalar(),
        total_artists=db.query(func.count(models.FavoriteArtist.id)).scalar(),
        total_genres=db.query(func.count(models.FavoriteGenre.id)).scalar(),
        paintings_by_type=dict(db.query(models.Painting.painting_type, func.count()).group_by(models.Painting.painting_type).all()),
        paintings_by_decade=dict(db.query((models.Painting.year//10)*10, func.count()).group_by((models.Painting.year//10)*10).all())
    )