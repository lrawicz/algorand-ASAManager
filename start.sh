#uvicorn main:app --host 0.0.0.0 --port 8000
docker build -t hash-nft .
docker run -p 8000:8000 hash-nft