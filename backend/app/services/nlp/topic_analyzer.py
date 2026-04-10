import numpy as np
import collections
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import AgglomerativeClustering
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from app.services.preprocessing.schemas import PreprocessedMessage
from app.services.nlp.schemas import (
    TopicSegment,
    TopicCluster,
    TopicAnalysisResponse,
)
from app.core.config import settings
_EMBED_BATCH_SIZE = 64
class TopicAnalyzer:
    """
    Analyzes chat messages to detect topic shifts and group related segments.
    Uses local embeddings and statistical methods — no external API calls.
    Optimization vs. original:
    - Accepts an optional shared SentenceTransformer to avoid loading a
      second copy of MiniLM when both TopicAnalyzer and TonalityAnalyzer
      are in use (the coordinator injects one shared instance).
    """
    def __init__(
        self,
        model_name: str = settings.TOPIC_MODEL,
        embedder: Optional[SentenceTransformer] = None,
    ):
        self._embedder = embedder
        self._model_name = model_name
        self.window_size = 5
        self.similarity_threshold = 0.50
    @property
    def model(self) -> SentenceTransformer:
        if self._embedder is None:
            self._embedder = SentenceTransformer(self._model_name)
        return self._embedder
    def analyze(self, messages: List[PreprocessedMessage]) -> TopicAnalysisResponse:
        if not messages:
            return TopicAnalysisResponse(segments=[], clusters=[], shifts=[])
        filtered_texts = [
            m.base_clean if m.base_clean.strip() else " " for m in messages
        ]
        embeddings = self._get_embeddings(filtered_texts)
        n = len(messages)
        W = self.window_size
        if n < W * 4:
            W = max(2, n // 6)
        shift_indices = self._detect_topic_shifts(embeddings, W)
        segments = self._create_segments(messages, embeddings, shift_indices)
        clusters = self._cluster_segments(segments, embeddings)
        summary_metrics = self._calculate_summary_metrics(
            segments, clusters, len(messages)
        )
        return TopicAnalysisResponse(
            segments=segments,
            clusters=clusters,
            shifts=[messages[idx].message_id for idx in shift_indices],
            summary_metrics=summary_metrics,
        )
    def _get_embeddings(self, texts: List[str]) -> np.ndarray:
        return self.model.encode(
            texts,
            batch_size=_EMBED_BATCH_SIZE,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
    def _detect_topic_shifts(
        self, embeddings: np.ndarray, W: int
    ) -> List[int]:
        shifts = []
        n = len(embeddings)
        if n < W * 2:
            return shifts
        similarities = []
        for i in range(W, n - W):
            prev_emb = np.mean(embeddings[i - W : i], axis=0).reshape(1, -1)
            next_emb = np.mean(embeddings[i : i + W], axis=0).reshape(1, -1)
            sim = cosine_similarity(prev_emb, next_emb)[0][0]
            similarities.append((i, sim))
        for i, sim in similarities:
            if sim < self.similarity_threshold:
                shifts.append(i)
        refined_shifts = []
        if shifts:
            shifts.sort()
            refined_shifts.append(shifts[0])
            for s in shifts[1:]:
                if s - refined_shifts[-1] >= W:
                    refined_shifts.append(s)
        return refined_shifts
    def _create_segments(
        self,
        messages: List[PreprocessedMessage],
        embeddings: np.ndarray,
        shift_indices: List[int],
    ) -> List[TopicSegment]:
        segments = []
        boundaries = [0] + shift_indices + [len(messages)]
        for i in range(len(boundaries) - 1):
            start_idx = boundaries[i]
            end_idx = boundaries[i + 1]
            segment_msgs = messages[start_idx:end_idx]
            if not segment_msgs:
                continue
            segment_text = " ".join(
                [m.base_clean for m in segment_msgs if m.base_clean.strip()]
            )
            keywords = self._extract_keywords(segment_text)
            label = keywords[0].title() if keywords else "General Chat"
            start_time = getattr(segment_msgs[0].raw, "timestamp", None)
            end_time = getattr(segment_msgs[-1].raw, "timestamp", None)
            segments.append(
                TopicSegment(
                    id=i,
                    start_id=segment_msgs[0].message_id,
                    end_id=segment_msgs[-1].message_id,
                    start_time=str(start_time) if start_time else None,
                    end_time=str(end_time) if end_time else None,
                    label=label,
                    keywords=keywords,
                    confidence=0.75,
                    message_count=len(segment_msgs),
                )
            )
        return segments
    def _cluster_segments(
        self,
        segments: List[TopicSegment],
        embeddings: np.ndarray,
    ) -> List[TopicCluster]:
        if not segments:
            return []
        segment_embeddings = []
        current_idx = 0
        for seg in segments:
            count = seg.message_count
            seg_emb = np.mean(embeddings[current_idx : current_idx + count], axis=0)
            segment_embeddings.append(seg_emb)
            current_idx += count
        if len(segments) < 2:
            return [
                TopicCluster(
                    cluster_id=0,
                    label=segments[0].label,
                    segment_ids=[segments[0].id],
                    keywords=segments[0].keywords,
                    reoccurrence_count=1,
                    total_messages=segments[0].message_count,
                )
            ]
        clustering = AgglomerativeClustering(
            n_clusters=None,
            distance_threshold=0.5,
            metric="cosine",
            linkage="average",
        )
        try:
            cluster_labels = clustering.fit_predict(segment_embeddings)
        except Exception:
            cluster_labels = [0] * len(segments)
        clusters_map = collections.defaultdict(list)
        for idx, label in enumerate(cluster_labels):
            clusters_map[label].append(segments[idx])
        topic_clusters = []
        for cluster_id, segs in clusters_map.items():
            all_keywords: List[str] = []
            for s in segs:
                all_keywords.extend(s.keywords)
            common_keywords = [
                k
                for k, _ in collections.Counter(all_keywords).most_common(5)
            ]
            topic_clusters.append(
                TopicCluster(
                    cluster_id=int(cluster_id),
                    label=common_keywords[0].title() if common_keywords else "Topic",
                    segment_ids=[s.id for s in segs],
                    keywords=common_keywords,
                    reoccurrence_count=len(segs),
                    total_messages=sum(s.message_count for s in segs),
                )
            )
        return topic_clusters
    def _extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        if not text.strip():
            return []
        try:
            vectorizer = TfidfVectorizer(stop_words="english", max_features=20)
            X = vectorizer.fit_transform([text])
            feature_names = vectorizer.get_feature_names_out()
            scores = X.toarray().flatten()
            indices = np.argsort(scores)[::-1][:max_keywords]
            return [feature_names[i] for i in indices]
        except Exception:
            tokens = [t.lower() for t in text.split() if len(t) > 3]
            return [
                k
                for k, _ in collections.Counter(tokens).most_common(max_keywords)
            ]
    def _calculate_summary_metrics(
        self, segments, clusters, total_msgs
    ) -> Dict[str, Any]:
        if not segments:
            return {
                "total_topics": 0,
                "most_recurring_topic": None,
                "conversation_fluidity": 0.0,
                "dominant_topic": None,
            }
        most_recurring = (
            max(clusters, key=lambda c: c.reoccurrence_count) if clusters else None
        )
        dominant = (
            max(clusters, key=lambda c: c.total_messages) if clusters else None
        )
        fluidity = min(1.0, len(segments) / (total_msgs / 20 + 1))
        return {
            "total_topics": len(clusters),
            "most_recurring_topic": most_recurring.label if most_recurring else None,
            "conversation_fluidity": round(fluidity, 2),
            "dominant_topic": dominant.label if dominant else None,
        }
