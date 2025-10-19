Clone the repository
-
```
git clone https://github.com/RoGWilson/RAG_Backend.git
```
Set parameters
-
On macOS/Linux
```
export DATA_DIR="your Data dir under RAG_Docs"
export OPENAI_API_KEY="your api key"
```
On Windows
```
$env:DATA_DIR = "your Data dir under RAG_Docs"
$env:OPENAI_API_KEY = "your api key"
```
Create a docker container
-
build and activate container at background 
```
docker compose up -d --build
```
or check if there are errors
```
docker compose logs backend
```

Populate the data
-
download the pre-generated embedding data and import them to db
```
#download the sql file "vector_backup.sql"
#copy the file under RAG_Backend
#execute
docker exec -i pgvector-db psql -U postgres -d vector_db < vector_backup.sql
```
Generate the embedding data yourself
```
docker exec -it rag_backend-backend-1 python manage.py populate_vector_db
```
check if the data is sucessfully embedded
```
docker exec -it pgvector-db psql -U postgres -d vector_db -c "
SELECT COUNT(*) FROM langchain_pg_embedding 
WHERE collection_id = (SELECT uuid FROM langchain_pg_collection WHERE name = 'rag_vector_embeddings_table');
"
#if it shows there are 189,270 count, then the data is sucessfully embedded
```
testing
-
run testing files
```
docker compose exec backend bash -lc "pip install -q pytest pytest-django && pytest -q"
# if it shows 6 passed, then the testing is sucessful
```




