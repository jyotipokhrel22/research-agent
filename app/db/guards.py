from fastapi import HTTPException, status


def require_collection(collection, name: str):
    if collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database is not configured for {name}",
        )
    return collection
