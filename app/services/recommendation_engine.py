from sqlalchemy.orm import Session
from typing import Dict, List
from app import models, crud
import math

class RecommendationEngine:
    def __init__(self, db: Session): self.db = db

    def get_recommendations(self, user_id: int, criteria: str, limit: int = 20) -> List[models.Painting]:
        scores: Dict[int, float] = {}
        fav_art = set(a.id for a in crud.get_user_fav_artists(self.db, user_id))
        fav_gen = set(g.id for g in crud.get_user_fav_genres(self.db, user_id))

        for p in self.db.query(models.Painting).all():
            s = 0
            if criteria in ["by_artist", "by_both"] and p.artist_id in fav_art: s += 10.0
            if criteria in ["by_genre", "by_both"] and p.genre_id in fav_gen: s += 8.0
            if p.year >= 2016: s += 2.0
            if p.description: s += 1.5
            if p.artist_id in fav_art and p.genre_id in fav_gen: s += 5.0
            
            # Simplified collaborative boost
            similar = self.db.query(models.User).filter(models.User.id != user_id).limit(50).all()
            collab = sum(1 for u in similar if (fav_art & {a.id for a in crud.get_user_fav_artists(self.db, u.id)}) or 
                         (fav_gen & {g.id for g in crud.get_user_fav_genres(self.db, u.id)}))
            s += min(collab * 0.5, 5.0)
            
            if s > 0: scores[p.id] = s

        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:limit]
        if not sorted_ids: return []
        return self.db.query(models.Painting).filter(models.Painting.id.in_(sorted_ids)).all()

    def explain(self, painting: models.Painting, user_id: int) -> dict:
        fav_art = {a.id for a in crud.get_user_fav_artists(self.db, user_id)}
        fav_gen = {g.id for g in crud.get_user_fav_genres(self.db, user_id)}
        factors = []
        if painting.artist_id in fav_art:
            factors.append({"factor": "favorite_artist", "weight": 10.0, "desc": f"Artist '{painting.artist.name}' is in favorites"})
        if painting.genre_id in fav_gen:
            factors.append({"factor": "favorite_genre", "weight": 8.0, "desc": f"Genre '{painting.genre.name}' is in favorites"})
        if painting.year >= 2016: factors.append({"factor": "recency", "weight": 2.0, "desc": "Created in last 10 years"})
        if painting.description: factors.append({"factor": "content_rich", "weight": 1.5, "desc": "Has detailed description"})
        return {"total_score": sum(f["weight"] for f in factors), "factors": factors}