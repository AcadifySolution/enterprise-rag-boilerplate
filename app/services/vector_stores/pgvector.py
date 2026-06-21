import asyncio
from typing import List, Dict, Any, Optional
from sqlalchemy import Column, String, Text, JSON, select, text, delete
from sqlalchemy.ext.asyncio import AsyncSession
from pgvector.sqlalchemy import Vector
from app.db.database import Base, engine, async_session_maker
from app.services.vector_stores.base import BaseVectorStore
from app.core.logging import logger

class DocumentEmbedding(Base):
    """
    SQLAlchemy database model for pgvector document chunk storage.
    """
    __tablename__ = "document_embeddings"
    
    id = Column(String, primary_key=True, index=True)
    vector = Column(Vector(1536), nullable=False)
    text = Column(Text, nullable=False)
    metadata_ = Column(JSON, nullable=False, default=dict)

class PgVectorStore(BaseVectorStore):
    """
    PgVector client wrapper implementing BaseVectorStore.
    """
    def __init__(self):
        self._db_initialized = False

    async def _init_db(self):
        """
        Registers pgvector extension and constructs database schema.
        """
        if self._db_initialized:
            return
        try:
            async with engine.begin() as conn:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                await conn.run_sync(Base.metadata.create_all)
            self._db_initialized = True
            logger.info("Successfully initialized PostgreSQL database with pgvector support.")
        except Exception as e:
            logger.error(f"Error initializing pgvector database tables: {str(e)}")

    async def upsert(
        self,
        ids: List[str],
        vectors: List[List[float]],
        metadatas: List[Dict[str, Any]],
        texts: List[str]
    ) -> bool:
        await self._init_db()
        try:
            async with async_session_maker() as session:
                async with session.begin():
                    for idx, vec, meta, txt in zip(ids, vectors, metadatas, texts):
                        # Construct or update the DocumentEmbedding
                        doc = await session.get(DocumentEmbedding, idx)
                        if doc:
                            doc.vector = vec
                            doc.text = txt
                            doc.metadata_ = meta
                        else:
                            doc = DocumentEmbedding(
                                id=idx,
                                vector=vec,
                                text=txt,
                                metadata_=meta
                            )
                            session.add(doc)
                await session.commit()
            return True
        except Exception as e:
            logger.error(f"pgvector upsert failed: {str(e)}")
            return False

    async def query(
        self,
        vector: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        await self._init_db()
        try:
            async with async_session_maker() as session:
                # Cosine distance ordering
                stmt = select(DocumentEmbedding).order_by(
                    DocumentEmbedding.vector.cosine_distance(vector)
                )
                
                # Apply metadata JSON filters
                if filter_dict:
                    for key, val in filter_dict.items():
                        stmt = stmt.where(
                            DocumentEmbedding.metadata_[key].astext == str(val)
                        )
                        
                stmt = stmt.limit(top_k)
                result = await session.execute(stmt)
                rows = result.scalars().all()
                
                results = []
                for row in rows:
                    # Score estimation: pgvector returns cosine distance (0 to 2)
                    # We map distance to similarity: 1 - distance
                    # Retrieve original vector/distance calculation if possible, else standard similarity scoring
                    distance_stmt = select(DocumentEmbedding.vector.cosine_distance(vector)).where(DocumentEmbedding.id == row.id)
                    dist_res = await session.execute(distance_stmt)
                    distance = dist_res.scalar() or 0.0
                    score = 1.0 - distance
                    
                    results.append({
                        "id": row.id,
                        "score": score,
                        "text": row.text,
                        "metadata": row.metadata_
                    })
                return results
        except Exception as e:
            logger.error(f"pgvector query failed: {str(e)}")
            return []

    async def delete(self, ids: List[str]) -> bool:
        await self._init_db()
        try:
            async with async_session_maker() as session:
                async with session.begin():
                    stmt = delete(DocumentEmbedding).where(DocumentEmbedding.id.in_(ids))
                    await session.execute(stmt)
                await session.commit()
            return True
        except Exception as e:
            logger.error(f"pgvector delete failed: {str(e)}")
            return False

    async def clear(self) -> bool:
        await self._init_db()
        try:
            async with async_session_maker() as session:
                async with session.begin():
                    stmt = delete(DocumentEmbedding)
                    await session.execute(stmt)
                await session.commit()
            return True
        except Exception as e:
            logger.error(f"pgvector clear failed: {str(e)}")
            return False

    async def verify_connectivity(self) -> bool:
        try:
            async with async_session_maker() as session:
                await session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"pgvector connection verification failed: {str(e)}")
            return False
