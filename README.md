# Hash NFT Software

Hash NFT Software is a web application built using FastAPI and Uvicorn. It provides a simple and efficient way to interact with Algorand blockchain by creating and managing hash-based NFTs. This README will guide you through setting up and running the software using Docker.

# Dependencies (Node and indexer)
This project requires an Algorand node and indexer. You can host them on your dedicated server or use a service like AlgoNode (algonode.io) for streamlined deployment.

## Prerequisites

- Docker: Install Docker on your system. You can download it from [Docker's official website](https://www.docker.com/get-started).

## Getting Started

Follow these steps to get Hash NFT Software up and running:

1. **Clone the Repository:**
   ```sh
   git clone https://github.com/your-username/hash-nft.git
   cd hash-nft

2. **Configure API Keys:**
    Open the config.json file in the config directory and edit the variables "mnemonic" and "x-token"
        "mnemonic": Replace this with your Algorand mnemonic.
        "x-token": You can change the value of this token to enhance security.
3. **Build the Docker Image and run the container:**

```sh
docker build -t hash-nft .
docker run -p 8000:8000 hash-nft
```
4. **Access the Application:**
Open your web browser and navigate to http://localhost:8000 to use the Hash NFT Software. The software's API will be available at http://localhost:8000/api.




