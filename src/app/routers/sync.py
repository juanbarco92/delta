from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session
from src.app.core.db import get_session
from src.app.services.sync import sync_user_items
from src.app.models.user import User

router = APIRouter()

@router.post("/items")
def trigger_sync_items(
    user_id: int, 
    background_tasks: BackgroundTasks, 
    session: Session = Depends(get_session)
):
    """
    Triggers the synchronization of items for a specific user.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    background_tasks.add_task(sync_user_items, user_id, session)
    
    return {"status": "accepted", "message": "Sync started in background", "user_id": user_id}
