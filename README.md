# Shadow Investigation Agent

An AI-powered investigation engine that analyzes multiple articles, extracts entities and relationships, and builds an interactive investigation graph.

## What It Does

This project turns raw articles into an investigation graph.

It can:

- Read multiple article files
- Extract important entities
- Extract relationships between entities
- Build a graph JSON file
- Show the graph in an interactive D3.js viewer

## Workflow

Articles  
↓  
Entity Extraction  
↓  
Connection Extraction  
↓  
Graph Builder  
↓  
D3.js Visualization  

## Example Case

FTX Collapse

Extracted entities:

- FTX
- Alameda Research
- Binance
- Sam Bankman-Fried

Example connections:

- Alameda Research → connected to → FTX
- Binance → considered acquiring → FTX
- Sam Bankman-Fried → resigned as CEO of → FTX

## Tech Stack

- Python
- Ollama
- Llama 3.2
- Pydantic
- D3.js

## How to Run

Install requirements:

```bash
pip install -r requirements.txt
```

Run Ollama:
```bash
ollama run llama3.2
```
Run the agent:
```bash
python src/main.py
```
Start the frontend server:
```bash
python -m http.server 8080
```
Open:
```bash
http://localhost:8080/frontend/index.html
```
Outputs

The project generates:

outputs/entities.json
outputs/connections.json
outputs/graph.json
outputs/investigation_graph_*.md

Roadmap
Better entity extraction
Better relationship direction
Timeline reconstruction
Automatic news collection
More polished graph visualization
Real investigation case studies
