from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from neo4j import GraphDatabase
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import transformers
from contextlib import asynccontextmanager

# Initialize the FastAPI app with lifespan context
app = FastAPI()

# Neo4j Database Credentials
neo4j_uri = "neo4j://localhost:7687"
neo4j_user = "neo4j"
neo4j_password = "password"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup resources (e.g., Neo4j driver)
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    app.state.driver = driver
    
    # Run the app with resources
    yield
    
    # Clean up resources on shutdown
    driver.close()

app = FastAPI(lifespan=lifespan)

# Models for incoming requests
class Paper(BaseModel):
    title: str
    year: int
    topic: str
    abstract: Optional[str] = None
    authors: Optional[List[str]] = []

class PaperQueryRequest(BaseModel):
    topic: Optional[str] = None
    year: Optional[int] = None

# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

### Endpoint: Store Paper Metadata in Neo4j ###
@app.post("/store_paper/")
def store_paper(paper: Paper):
    with app.state.driver.session() as session:
        try:
            session.run(
                """
                MERGE (p:Paper {title: $title, year: $year, topic: $topic, abstract: $abstract})
                SET p.authors = $authors
                """,
                title=paper.title,
                year=paper.year,
                topic=paper.topic,
                abstract=paper.abstract,
                authors=paper.authors
            )
            return {"status": "Paper stored successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

### Endpoint: Query Papers by Topic and Year ###
@app.post("/query_papers/")
def query_papers(query: PaperQueryRequest):
    with app.state.driver.session() as session:
        try:
            query_str = "MATCH (p:Paper) WHERE 1=1 "
            params = {}

            # Add filtering by year if provided
            if query.year:
                query_str += "AND p.year = $year "
                params['year'] = query.year

            # Add filtering by topic if provided
            if query.topic:
                query_str += "AND p.topic = $topic "
                params['topic'] = query.topic

            query_str += "RETURN p.title AS title, p.year AS year, p.topic AS topic, p.abstract AS abstract, p.authors AS authors"

            result = session.run(query_str, **params)
            papers = [
                {
                    "title": record["title"],
                    "year": record["year"],
                    "topic": record["topic"],
                    "abstract": record["abstract"],
                    "authors": record["authors"]
                }
                for record in result
            ]

            return {"papers": papers}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
