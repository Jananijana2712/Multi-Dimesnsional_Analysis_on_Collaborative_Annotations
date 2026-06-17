# Multi-Dimensional Analysis on Collaborative Annotations

## Overview

This project was developed as part of my M.Tech Final Year Phase - II Project.

The project presents an AI-powered Cricket Chatbot that integrates multiple cricket-related data sources to provide context-aware responses, match summaries, predictive analytics, voice interaction, and visual insights.

The chatbot supports both English and Tamil languages and allows users to interact through text and voice interfaces.

## Objectives

- Context-aware cricket query answering
- Match insights and auto-summarization
- Predictive analytics for match outcomes
- Voice-based interaction
- Multilingual support (English and Tamil)
- Interactive data visualization
- Integration of multiple cricket knowledge sources

## Data Sources

### Cricsheet Dataset
Historical cricket match data including:

- Ball-by-ball records
- Player statistics
- Match outcomes
- ODI
- T20
- Test matches

### External APIs

- Wikipedia API
- CricketData API
- Google News API

## System Architecture

The system consists of four major modules:

### UI/UX Module

- Text Input
- Voice Input
- Light Mode
- Dark Mode
- Multilingual Support

### Processing Module

- Context-Based Retrieval
- Match Summary Generation
- Predictive Analytics
- Voice Processing
- Visualization Generation

### Database Module

- MongoDB
- Cricsheet Dataset
- Wikipedia Data
- CricketData API
- Google News API

### Output Module

- Text Response
- Voice Response
- Interactive Charts

## Features

### Context-Based Retrieval

The chatbot extracts:

- Team Names
- Match Dates
- Player Information

using:

- Regular Expressions (Regex)
- Named Entity Recognition (NER)
- FAISS Vector Search

### Match Insights

Provides:

- Match Summaries
- Team Statistics
- Top Batters
- Top Bowlers
- Match Results

### Predictive Analytics

Implemented using:

- Logistic Regression

Predicts:

- Match Outcomes
- Team Performance

### Voice Modeling

Speech-to-Text:

- Google Speech Recognition API

Text-to-Speech:

- pyttsx3

Supported Languages:

- English
- Tamil

### Visualization

Interactive charts created using:

- Chart.js

Visualizations include:

- Win/Loss Analysis
- Player Performance
- Team Statistics
- Wicket Analysis

## Technology Stack

### Backend

- Python
- FastAPI

### Database

- MongoDB

### Frontend

- HTML
- CSS
- JavaScript

### Libraries

- Pandas
- Requests
- pyttsx3
- SpeechRecognition
- Chart.js

## Results

The chatbot successfully performs:

- Context-aware cricket query answering
- Match summarization
- Predictive analytics
- Voice interaction
- Interactive visualization

while supporting multilingual communication in English and Tamil.
