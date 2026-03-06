from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import MatchResult

router = APIRouter(prefix="/api/team", tags=["Team Formation"])

@router.post("/predict")
async def predict_team(results: List[MatchResult], team_size: int = 3):
    """
    Predict an ideal team formation from a pool of candidates.
    Heuristic: Select candidates who together cover the most unique skills 
    while maintaining highest individual scores in different categories.
    """
    if not results:
        raise HTTPException(status_code=400, detail="No candidates provided for team formation.")
        
    if len(results) <= team_size:
        # Just assign roles to everyone
        team = []
        roles = ["Team Lead", "Technical Specialist", "Communicator", "Project Lead", "Core Developer"]
        for i, res in enumerate(results):
            team.append({
                "role": roles[i % len(roles)],
                "candidate": res
            })
        return {
            "team": team,
            "message": "Pool size smaller than or equal to team size. Roles assigned to all."
        }

    # Algorithm:
    # 1. Start with the overall top scorer (The "All-Rounder / Team Lead")
    # 2. Pick the person with the highest technical skill score who isn't #1.
    # 3. Pick the person with the highest soft skill score who isn't already picked.
    # 4. If more needed, pick based on highest project score or experience.
    
    sorted_by_total = sorted(results, key=lambda x: x.final_score, reverse=True)
    team = []
    picked_filenames = set()

    # Lead: Highest overall
    lead = sorted_by_total[0]
    team.append({
        "role": "Team Lead / All-Rounder",
        "candidate": lead
    })
    picked_filenames.add(lead.filename)

    # Specialist: Highest skill_score (excluding lead)
    sorted_by_skill = sorted(results, key=lambda x: x.skill_score, reverse=True)
    for cand in sorted_by_skill:
        if cand.filename not in picked_filenames:
            team.append({
                "role": "Technical Specialist",
                "candidate": cand
            })
            picked_filenames.add(cand.filename)
            break

    # Communicator: Highest soft_skill_score
    if len(team) < team_size:
        sorted_by_soft = sorted(results, key=lambda x: x.soft_skill_score, reverse=True)
        for cand in sorted_by_soft:
            if cand.filename not in picked_filenames:
                team.append({
                    "role": "Soft Skills / Communicator",
                    "candidate": cand
                })
                picked_filenames.add(cand.filename)
                break

    # Executor: Highest project_score
    if len(team) < team_size:
        sorted_by_proj = sorted(results, key=lambda x: x.project_score, reverse=True)
        for cand in sorted_by_proj:
            if cand.filename not in picked_filenames:
                team.append({
                    "role": "Project Implementer",
                    "candidate": cand
                })
                picked_filenames.add(cand.filename)
                break
                
    # Fill remaining from top scorers
    if len(team) < team_size:
        for cand in sorted_by_total:
            if cand.filename not in picked_filenames:
                team.append({
                    "role": "Core Contributor",
                    "candidate": cand
                })
                picked_filenames.add(cand.filename)
                if len(team) >= team_size:
                    break

    return {
        "status": "success",
        "team": team,
        "team_size": len(team),
        "total_pool": len(results)
    }
