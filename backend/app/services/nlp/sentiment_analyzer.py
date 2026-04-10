import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from transformers import pipeline
import torch
import emoji
from app.services.nlp.schemas import (
    MessageSentiment,
    SentimentAnalysisResponse,
    ParticipantSentiment,
    SentimentTrendPoint,
)
from app.services.parser.schemas import RawMessage
_BATCH_SIZE = 32
_MAX_CHARS = 512
class SentimentAnalyzer:
    """
    Local sentiment analysis using a RoBERTa-based model.
    Privacy-first: no external API calls.
    Optimizations vs. original:
    - ALL messages are encoded in ONE batched pipeline call instead of N calls.
    - Duplicate texts are inferred only once (dedup + re-expand).
    - Pipeline is still lazy-loaded on first use.
    """
    def __init__(
        self,
        model_name: str = "SamLowe/roberta-base-go_emotions",
    ):
        self.model_name = model_name
        self._pipeline = None
    @property
    def pipeline(self):
        if self._pipeline is None:
            self._pipeline = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                tokenizer=self.model_name,
                device=-1,
                top_k=None,
            )
        return self._pipeline
    def _get_continuous_score(
        self, results: List[Dict[str, Any]]
    ) -> Tuple[float, str, float]:
        """Convert GoEmotions multi-label logits into a continuous -1 → +1 score."""
        scores = {res["label"]: res["score"] for res in results}
        positive_emotions = ["admiration", "amusement", "approval", "caring", "desire", "excitement", "gratitude", "joy", "love", "optimism", "pride", "relief"]
        negative_emotions = ["anger", "annoyance", "disappointment", "disapproval", "disgust", "embarrassment", "fear", "grief", "nervousness", "remorse", "sadness"]
        pos = sum(scores.get(e, 0.0) for e in positive_emotions)
        neg = sum(scores.get(e, 0.0) for e in negative_emotions)
        neu = scores.get("neutral", 0.0) + sum(scores.get(e, 0.0) for e in ["confusion", "curiosity", "realization", "surprise"])
        continuous_score = pos - neg
        continuous_score = max(-1.0, min(1.0, continuous_score))
        max_score = max(pos, neg, neu)
        if max_score == pos:
            label = "positive"
        elif max_score == neg:
            label = "negative"
        else:
            label = "neutral"
        return float(continuous_score), label, float(min(1.0, max_score))
    def _make_neutral(self, msg_id: int, sender: Optional[str]) -> MessageSentiment:
        return MessageSentiment(
            message_id=msg_id, sender=sender,
            score=0.0, label="neutral", confidence=0.0,
        )
    def analyze_chat(self, messages: List[RawMessage]) -> SentimentAnalysisResponse:
        """
        Process the entire chat in one batched forward pass.
        Strategy
        --------
        1. Collect all non-trivial message texts (skip media / empty).
        2. Deduplicate identical texts → infer only unique ones.
        3. Map results back to original message indices.
        4. Build MessageSentiment objects and aggregate.
        """
        if not messages:
            return SentimentAnalysisResponse(
                messages=[], participants=[], timeline=[], summary_metrics={}
            )
        texts: List[str] = []
        msg_idx_map: List[int] = []
        for i, msg in enumerate(messages):
            if msg.is_media or not msg.content.strip():
                continue
            context_text = ""
            if i > 0 and not messages[i-1].is_media and messages[i-1].content.strip():
                prev = messages[i-1]
                context_text = f"[{prev.sender}]: {prev.content[:150]} \n "
            current_text = f"[{msg.sender}]: {msg.content[:_MAX_CHARS - len(context_text)]}"
            combined_text = context_text + current_text
            texts.append(combined_text)
            msg_idx_map.append(i)
        unique_texts = list(dict.fromkeys(texts))
        text_to_idx = {t: i for i, t in enumerate(unique_texts)}
        raw_batch: List[List[Dict]] = []
        if unique_texts:
            raw_batch = self.pipeline(
                unique_texts,
                batch_size=_BATCH_SIZE,
                truncation=True,
            )
        unique_scores: List[Tuple[float, str, float]] = [
            self._get_continuous_score(r) for r in raw_batch
        ]
        results: List[MessageSentiment] = [None] * len(messages)
        for text, orig_i in zip(texts, msg_idx_map):
            score, label, confidence = unique_scores[text_to_idx[text]]
            words = text.split()
            if len(words) < 3:
                confidence *= 0.8
            results[orig_i] = MessageSentiment(
                message_id=orig_i,
                sender=messages[orig_i].sender,
                score=score,
                label=label,
                confidence=confidence,
            )
        for i, msg in enumerate(messages):
            if results[i] is None:
                results[i] = self._make_neutral(i, msg.sender)
        return self._aggregate(results)
    def _aggregate(
        self, results: List[MessageSentiment]
    ) -> SentimentAnalysisResponse:
        participant_map: Dict[str, Dict[str, Any]] = {}
        for res in results:
            if not res.sender:
                continue
            if res.sender not in participant_map:
                participant_map[res.sender] = {
                    "scores": [], "pos": 0, "neg": 0, "neu": 0
                }
            p = participant_map[res.sender]
            p["scores"].append(res.score)
            if res.label == "positive":
                p["pos"] += 1
            elif res.label == "negative":
                p["neg"] += 1
            else:
                p["neu"] += 1
        participants = []
        for name, data in participant_map.items():
            avg_score = float(np.mean(data["scores"])) if data["scores"] else 0.0
            participants.append(
                ParticipantSentiment(
                    name=name,
                    overall_score=round(avg_score, 3),
                    pos_count=data["pos"],
                    neg_count=data["neg"],
                    neutral_count=data["neu"],
                )
            )
        all_scores = [r.score for r in results]
        volatility = float(np.std(all_scores)) if all_scores else 0.0
        pos_count = sum(1 for r in results if r.label == "positive")
        neg_count = sum(1 for r in results if r.label == "negative")
        total = len(results) or 1
        mean_score = float(np.mean(all_scores)) if all_scores else 0.0
        summary = {
            "overall_sentiment": (
                "positive" if mean_score > 0.05
                else ("negative" if mean_score < -0.05 else "neutral")
            ),
            "positivity_rate": round(pos_count / total, 3),
            "negativity_rate": round(neg_count / total, 3),
            "volatility": round(volatility, 3),
        }
        return SentimentAnalysisResponse(
            messages=results,
            participants=participants,
            timeline=self._calculate_timeline(results),
            summary_metrics=summary,
        )
    def _calculate_timeline(
        self, sentiments: List[MessageSentiment], bin_count: int = 25
    ) -> List[SentimentTrendPoint]:
        if not sentiments:
            return []
        chunks = np.array_split(sentiments, min(bin_count, len(sentiments)))
        raw_scores = []
        timeline = []
        for i, chunk in enumerate(chunks):
            if len(chunk) == 0:
                continue
            avg_score = float(np.mean([s.score for s in chunk]))
            raw_scores.append(avg_score)
            timeline.append({
                "label": f"Segment {i + 1}",
                "average_score": avg_score,
                "volume": len(chunk),
            })
        window_size = 3
        if len(raw_scores) >= window_size:
            smoothed = np.convolve(
                raw_scores, np.ones(window_size) / window_size, mode="same"
            )
        else:
            smoothed = raw_scores
        result = []
        for i, item in enumerate(timeline):
            result.append(
                SentimentTrendPoint(
                    label=item["label"],
                    average_score=round(item["average_score"], 3),
                    smoothed_score=round(float(smoothed[i]), 3),
                    volume=item["volume"],
                )
            )
        return result
