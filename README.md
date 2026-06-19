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
