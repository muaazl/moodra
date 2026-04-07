# Moodra - API Specification

## 1. Core Endpoints

### POST `/api/v1/analyze/text`
Analyzes a pasted string of WhatsApp chat text.
- **Request Body**: `AnalysisRequest` (JSON)
- **Response Body**: `AnalysisSuccessResponse` (JSON)

### POST `/api/v1/analyze/file`
Analyzes an uploaded WhatsApp export (.txt).
- **Format**: `multipart/form-data`
- **Field**: `file` (UploadFile)
- **Response Body**: `AnalysisSuccessResponse` (JSON)

### GET `/health`
Health check for the backend service.

---

## 2. Request Schemas

### AnalysisRequest
```json
{
  "text": "The raw chat export string...",
  "options": {
    "anonymize": true
  }
}
```

---

## 3. Response Schemas (Recursive)

### AnalysisSuccessResponse
```json
{
  "status": "success",
  "data": ScoringResponse,
  "metadata": {
    "timestamp": "2024-04-02T10:00:00Z",
    "processing_time": 1.25
  }
}
```

### ScoringResponse
```json
{
  "overall_summary": "string",
  "overall_mood": "string",
  "participants": [ParticipantScoring],
  "segments": [SegmentScoring],
  "timeline": [{"time": "...", "sentiment": 0.5, "volume": 10, "tension": 0.2}],
  "standout_cards": [StandoutCard],
  "global_metrics": {
    "conversation_health": 0.85,
    "total_messages": 100
  }
}
```

### ParticipantScoring
```json
{
  "name": "Alice",
  "dominance": ScoreMetadata,
  "dry_texting": ScoreMetadata,
  "passive_aggression": ScoreMetadata,
  "main_character_energy": ScoreMetadata,
  "badges": ["string"]
}
```

### ScoreMetadata
```json
{
  "value": 0.7,
  "label": "High",
  "explanation": "...",
  "confidence": 0.9
}
```

### ErrorResponse
```json
{
  "status": "error",
  "code": "ANALYSIS_FAILED",
  "message": "Human-readable error message",
  "details": {}
}
```

---

## 4. Privacy & Cleanup Strategy
1. **No Disk Storage**: All uploaded content is processed in memory via byte-streams.
2. **Ephemeral Lifecycle**: No database persistence. Objects are garbage collected after response delivery.
3. **Local-First**: 100% of NLP processing occurs within the local CPU/memory space using spaCy and Transformers.
4. **No External Calls**: The backend is prohibited from contacting any cloud API or LLM provider.

## 5. Deployment / Test Plan
- Run `uvicorn main:app --port 8000 --reload`
- Integration tests in `backend/tests/test_api_integration.py`
- Benchmarking with sample WhatsApp exports (>10,000 messages) recommended.
