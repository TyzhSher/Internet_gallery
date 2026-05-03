from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas, models
from app.auth import get_current_user
from app.services.recommendation_engine import RecommendationEngine

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])

@router.post("", response_model=schemas.RecommendationResponse)
def recommend(req: schemas.RecommendationRequest, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    fav_art = crud.get_user_fav_artists(db, user.id)
    fav_gen = crud.get_user_fav_genres(db, user.id)
    if req.criteria == "by_artist" and not fav_art: raise HTTPException(400, detail="No favorite artists found")
    if req.criteria == "by_genre" and not fav_gen: raise HTTPException(400, detail="No favorite genres found")
    if req.criteria == "by_both" and (not fav_art or not fav_gen): raise HTTPException(400, detail="Need both artists and genres in favorites")
    
    engine = RecommendationEngine(db)
    pnts = engine.get_recommendations(user.id, req.criteria)
    return schemas.RecommendationResponse(paintings=pnts, criteria_used=req.criteria, total_count=len(pnts))

@router.post("/explain/{pid}", response_model=schemas.ExplainResponse)
def explain(pid: int, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    p = crud.get_painting(db, pid)
    if not p: raise HTTPException(404, detail="Painting not found")
    engine = RecommendationEngine(db)
    exp = engine.explain(p, user.id)
    return schemas.ExplainResponse(painting_id=pid, painting_title=p.title, total_score=exp["total_score"], 
                                   factors=exp["factors"], algorithm_version="hybrid_v2.0")