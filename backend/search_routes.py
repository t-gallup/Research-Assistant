from fastapi import APIRouter, HTTPException, Query, Request, Depends
from typing import List
from pydantic import BaseModel
import os
import aiohttp
from firebase_auth import verify_firebase_token
from rate_limiter import rate_limiter

router = APIRouter()


class SearchResult(BaseModel):
    title: str
    link: str
    snippet: str


class SearchResponse(BaseModel):
    results: List[SearchResult]


@router.get("/api/search", response_model=SearchResponse)
async def search(q: str = Query(..., min_length=1),
                request: Request = None,
                token: dict = Depends(verify_firebase_token),
                is_internal: bool = True):
    try:
        # Only check rate limit if this is an external request
        if not is_internal and request:
            await rate_limiter.check_rate_limit(request, token, is_internal=False)

        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
        
        if not GOOGLE_API_KEY or not SEARCH_ENGINE_ID:
            raise HTTPException(
                status_code=500,
                detail="Google Search API credentials not configured"
            )

        async with aiohttp.ClientSession() as session:
            params = {
                'key': GOOGLE_API_KEY,
                'cx': SEARCH_ENGINE_ID,
                'q': q,
                'num': 10
            }
            
            async with session.get(
                'https://www.googleapis.com/customsearch/v1',
                params=params
            ) as response:
                if response.status != 200:
                    error_detail = await response.text()
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Google Search API error: {error_detail}"
                    )
                
                data = await response.json()
                
                if 'items' not in data:
                    return SearchResponse(results=[])

                results = [
                    SearchResult(
                        title=item.get('title', ''),
                        link=item.get('link', ''),
                        snippet=item.get('snippet', '')
                    )
                    for item in data['items']
                ]
                
                return SearchResponse(results=results)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search error: {str(e)}"
        )