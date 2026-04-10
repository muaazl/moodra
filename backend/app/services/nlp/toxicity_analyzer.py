import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from transformers import pipeline
import torch
from app.services.nlp.schemas import (
    MessageToxicity,
    ParticipantToxicity,
    ToxicityAnalysisResponse,
)
from app.services.parser.schemas import RawMessage
from app.core.config import settings
_BATCH_SIZE = 32
_MAX_CHARS = 512
class ToxicityAnalyzer:
    """
    Local toxicity analysis using a transformer model.
    Privacy-first: everything runs on CPU/local.
    Optimizations vs. original:
    - All messages processed in ONE batched pipeline call.
    - Duplicate texts inferred only once (dedup + re-expand).
    """
    def __init__(self, model_name: str = settings.TOXICITY_MODEL):
        self.model_name = model_name
        self._pipeline = None
        self.threshold = 0.5
    @property
    def pipeline(self):
        if self._pipeline is None:
            self._pipeline = pipeline(
                "text-classification",
                model=self.model_name,
                tokenizer=self.model_name,
                device=-1,
                top_k=None,
            )
        return self._pipeline
    def _score_from_raw(
        self,
        raw_results: List[Dict[str, Any]],
        text: str,
    ) -> MessageToxicity:
        """Convert raw pipeline output for one message into a MessageToxicity."""
        categories = {res["label"]: float(res["score"]) for res in raw_results}
        max_score = float(max(categories.values())) if categories else 0.0
        top_cat = (
            str(max(categories, key=categories.get)) if categories else None
        )
        confidence = max_score
        words = text.split()
        if len(words) < 3:
            confidence *= 0.7
        elif len(words) > 50:
            confidence *= 0.9
        words_lower = [w.lower().strip(".,!?\"'") for w in words]
        if max_score > 0.85:
            label = "high"
        elif max_score > 0.5:
            label = "medium"
        else:
            label = "low"
        return dict(
            score=round(max_score, 3),
            label=label,
            confidence=round(confidence, 3),
            top_category=top_cat,
            categories=categories,
            is_high_risk=(max_score > self.threshold),
        )
    def _make_safe(self) -> Dict:
        return dict(
            score=0.0, label="low", confidence=0.0,
            top_category=None, categories={}, is_high_risk=False,
        )
    def analyze_chat(self, messages: List[RawMessage]) -> ToxicityAnalysisResponse:
        if not messages:
            return ToxicityAnalysisResponse(
                messages=[], participants=[],
                global_intensity=0.0, summary_metrics={}
            )
        texts: List[str] = []
        msg_idx_map: List[int] = []
        for i, msg in enumerate(messages):
            if msg.is_media or not msg.content.strip():
                continue
            texts.append(msg.content[:_MAX_CHARS])
            msg_idx_map.append(i)
        unique_texts = list(dict.fromkeys(texts))
        text_to_unique_idx = {t: i for i, t in enumerate(unique_texts)}
        raw_batch: List[List[Dict]] = []
        if unique_texts:
            raw_batch = self.pipeline(
                unique_texts,
                batch_size=_BATCH_SIZE,
                truncation=True,
            )
        unique_scored = [
            self._score_from_raw(raw_batch[i], unique_texts[i])
            for i in range(len(unique_texts))
        ]
        msg_results: List[MessageToxicity] = []
        scored_map: Dict[int, Dict] = {}
        for text, orig_i in zip(texts, msg_idx_map):
            scored_map[orig_i] = unique_scored[text_to_unique_idx[text]]
        for i, msg in enumerate(messages):
            if i in scored_map:
                s = scored_map[i]
                msg_results.append(
                    MessageToxicity(
                        message_id=i,
                        sender=msg.sender,
                        **s,
                    )
                )
            else:
                msg_results.append(
                    MessageToxicity(
                        message_id=i,
                        sender=msg.sender,
                        **self._make_safe(),
                    )
                )
        return self._aggregate(msg_results)
    def _aggregate(
        self, msg_results: List[MessageToxicity]
    ) -> ToxicityAnalysisResponse:
        participant_map: Dict[str, Dict[str, Any]] = {}
        for res in msg_results:
            if not res.sender:
                continue
            if res.sender not in participant_map:
                participant_map[res.sender] = {
                    "scores": [], "outbursts": 0, "risky_ids": []
                }
            p = participant_map[res.sender]
            p["scores"].append(res.score)
            if res.is_high_risk:
                p["outbursts"] += 1
                p["risky_ids"].append(res.message_id)
        participants = []
        for name, data in participant_map.items():
            avg_intensity = np.mean(data["scores"]) if data["scores"] else 0.0
            max_heat = max(data["scores"]) if data["scores"] else 0.0
            participants.append(
                ParticipantToxicity(
                    name=name,
                    intensity_index=round(float(avg_intensity), 3),
                    outburst_count=data["outbursts"],
                    max_heat=round(float(max_heat), 3),
                    risky_message_ids=data["risky_ids"][:5],
                )
            )
        all_scores = [r.score for r in msg_results]
        global_intensity = float(np.mean(all_scores)) if all_scores else 0.0
        high_risk_total = sum(1 for r in msg_results if r.is_high_risk)
        most_intense_user = (
            max(participants, key=lambda p: p.intensity_index).name
            if participants
            else None
        )
        summary = {
            "most_intense_user": most_intense_user,
            "high_risk_ratio": round(high_risk_total / len(msg_results), 3)
            if msg_results
            else 0.0,
            "peak_tension_segment": self._identify_peak_tension(all_scores),
            "uncertainty_index": round(
                1.0 - float(np.mean([r.confidence for r in msg_results])), 3
            )
            if msg_results
            else 0.0,
        }
        return ToxicityAnalysisResponse(
            messages=msg_results,
            participants=participants,
            global_intensity=round(global_intensity, 3),
            summary_metrics=summary,
        )
    def _identify_peak_tension(
        self, scores: List[float], bin_size: int = 20
    ) -> Optional[str]:
        if not scores:
            return None
        chunks = np.array_split(scores, min(len(scores), bin_size))
        avg_scores = [np.mean(chunk) for chunk in chunks if len(chunk) > 0]
        if not avg_scores:
            return None
        peak_idx = int(np.argmax(avg_scores))
        return f"Segment {peak_idx + 1}"
