import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, Request, HTTPException
from psycopg_pool import ConnectionPool

from config import DATABASE_URL
from models import CreatePptRequest, CreatePptResponse
from db import create_pool, save_ppt_template, PptSaveError
from ppt_service import build_presentation, convert_ppt_to_bytes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting DB connection pool (max_size=3)...")
    app.state.db_pool = create_pool()
    yield
    logger.info("Closing DB connection pool...")
    app.state.db_pool.close()


app = FastAPI(lifespan=lifespan)


def get_db_pool(request: Request) -> ConnectionPool:
    return request.app.state.db_pool


@app.post("/generate_pb_ppt", response_model=CreatePptResponse)
def generate_pb_ppt(
    request: CreatePptRequest,
    pool: ConnectionPool = Depends(get_db_pool),
):
    presentation = build_presentation(request)
    ppt_bytes = convert_ppt_to_bytes(presentation)
    file_name = f"{request.pts_id}_Build.pptx"

    # created_by would typically come from an auth/session layer, not the request body
    created_by = request.architecture[0].soeid if request.architecture else "unknown"

    try:
        result = save_ppt_template(
            pool=pool,
            pts_id=request.pts_id,
            permit_type="Build",
            ppt_bytes=ppt_bytes,
            file_name=file_name,
            created_by=created_by,
        )
    except PptSaveError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return CreatePptResponse(
        id=result["id"],
        pts_id=request.pts_id,
        permit_type="Build",
        version=result["version"],
        status=result["status"],
        file_name=file_name,
        created_at=result["created_at"],
    )


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
