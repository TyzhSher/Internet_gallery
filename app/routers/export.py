from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
import csv, io
from app.database import get_db
from app import crud

router = APIRouter(prefix="/api/export", tags=["export"])

@router.get("/paintings/csv")
def export_csv(artist: str=None, genre: str=None, db: Session = Depends(get_db)):
    pnts = crud.search_paintings(db, q="", artist=artist, genre=genre, limit=10000)
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["ID","Title","Artist","Genre","Year","Type","URL"])
    for p in pnts: w.writerow([p.id, p.title, p.artist.name, p.genre.name, p.year, p.painting_type.value, p.image_url])
    return Response(out.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=paintings.csv"})