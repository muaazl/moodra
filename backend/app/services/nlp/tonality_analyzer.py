import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import Counter
import spacy
import emoji

from app.services.nlp.schemas import (
    TonalityAnalysisResponse,
    MessageTonality,
    TonalitySignal,
    ParticipantTonality,
    MessageSentiment
)
from app.services.parser.schemas import RawMessage


class TonalityAnalyzer:
    """
    Analyzes chat messages for 'dryness' and 'passive-aggression'.

    Scoring is fully model-driven — no hardcoded reference phrase lists.
    Dryness is derived from brevity + vibrancy + sentiment neutrality.
    Passive aggression is derived from sentiment mismatch, punctuation
    patterns, response delay, and capitalization signals. All sub-signals
    are explainable via TonalitySignal objects.

    Privacy-first: No external API calls. No sentence-transformer needed.
    """

    def __init__(
        self,
        spacy_model: str = "en_core_web_sm",
        # embedder kwarg kept for backwards compat with coordinator but ignored
        embedder=None,
        nlp: Optional[spacy.language.Language] = None,
    ):
        self.spacy_model = spacy_model
        self._nlp = nlp

    # ------------------------------------------------------------------
    # Lazy loaders
    # ------------------------------------------------------------------

    @property
    def nlp(self):
        if self._nlp is None:
            try:
                self._nlp = spacy.load(self.spacy_model)
            except Exception:
                import subprocess
                subprocess.run(["python", "-m", "spacy", "download", self.spacy_model])
                self._nlp = spacy.load(self.spacy_model)
        return self._nlp

    # ------------------------------------------------------------------
    # Scoring helpers (stateless, no model calls)
    # ------------------------------------------------------------------

    def _calculate_brevity(self, text: str) -> float:
        """Short texts score higher. ≤1 word = 1.0, ≥10 words = 0.0."""
        words = text.split()
        if not words:
            return 1.0
        return max(0.0, min(1.0, (10 - len(words)) / 9))

    def _calculate_vibrancy(self, text: str) -> float:
        """Presence of emojis or exclamations signals expressiveness (0–1)."""
        emoji_count = len(emoji.emoji_list(text))
        exclamation_count = text.count("!")
        return min(1.0, (emoji_count + exclamation_count) / 2)

    def _sentiment_neutrality_boost(self, sentiment: Optional[MessageSentiment]) -> float:
        """A neutral sentiment on a short message is a dryness signal."""
        if sentiment is None:
            return 0.0
        if sentiment.label == "neutral":
            return 0.2
        return 0.0

    def _sentiment_mismatch_boost(
        self,
        sentiment: Optional[MessageSentiment],
        brevity: float,
        content: str,
    ) -> float:
        """
        Positive-sentiment label + dry delivery = passive-aggression signal.
        The sentiment model sees 'positive' words but the message is terse —
        classic 'fine.' energy.
        """
        if sentiment is None:
            return 0.0
        if sentiment.label == "positive" and brevity > 0.65:
            return 0.3
        return 0.0

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def analyze_chat(
        self,
        messages: List[RawMessage],
        sentiment_results: List[MessageSentiment],
    ) -> TonalityAnalysisResponse:
        if not messages:
            return TonalityAnalysisResponse(messages=[], participants=[])

        participant_baselines = self._calculate_baselines(messages)

        message_results: List[MessageTonality] = []
        for i, msg in enumerate(messages):
            sentiment = sentiment_results[i] if i < len(sentiment_results) else None
            prev_msg = messages[i - 1] if i > 0 else None
            baseline = participant_baselines.get(msg.sender, {})

            result = self._analyze_single_message(
                msg=msg,
                msg_id=i,
                sentiment=sentiment,
                prev_msg=prev_msg,
                baseline=baseline,
            )
            message_results.append(result)

        participant_results = self._aggregate_participants(message_results)
        summary = self._calculate_summary(message_results)

        return TonalityAnalysisResponse(
            messages=message_results,
            participants=participant_results,
            summary_metrics=summary,
        )

    # ------------------------------------------------------------------
    # Per-message analysis (pure linguistics + sentiment — no embeddings)
    # ------------------------------------------------------------------

    def _analyze_single_message(
        self,
        msg: RawMessage,
        msg_id: int,
        sentiment: Optional[MessageSentiment],
        prev_msg: Optional[RawMessage],
        baseline: Dict[str, Any],
    ) -> MessageTonality:
        content = msg.content.strip()
        if msg.is_media or not content:
            return MessageTonality(
                message_id=msg_id,
                sender=msg.sender,
                dryness_score=0.0,
                passive_aggression_score=0.0,
                confidence=0.0,
            )

        signals: List[TonalitySignal] = []
        words = content.split()

        # ----------------------------------------------------------------
        # DRYNESS
        # Combines: brevity + lack of expressiveness + sentiment neutrality
        # ----------------------------------------------------------------
        brevity = self._calculate_brevity(content)
        vibrancy = self._calculate_vibrancy(content)
        neutral_boost = self._sentiment_neutrality_boost(sentiment)

        dryness_score = (brevity * 0.5) + ((1 - vibrancy) * 0.3) + (neutral_boost * 0.2)

        if brevity > 0.7:
            signals.append(TonalitySignal(
                type="brevity",
                score_influence=round(brevity * 0.5, 3),
                description="Message is unusually short.",
            ))
        if vibrancy < 0.2:
            signals.append(TonalitySignal(
                type="low_vibrancy",
                score_influence=0.3,
                description="Lack of emojis or expressive punctuation.",
            ))
        if neutral_boost > 0:
            signals.append(TonalitySignal(
                type="neutral_sentiment",
                score_influence=neutral_boost * 0.2,
                description="Sentiment model detected a flat, neutral tone.",
            ))

        # ----------------------------------------------------------------
        # PASSIVE AGGRESSION
        # Combines: sentiment mismatch, abruptness, delay, casing signals
        # ----------------------------------------------------------------
        pa_score = 0.0

        # Signal 1: Positive label on a short/terse reply
        mismatch_boost = self._sentiment_mismatch_boost(sentiment, brevity, content)
        if mismatch_boost > 0:
            pa_score += mismatch_boost
            signals.append(TonalitySignal(
                type="mismatch",
                score_influence=mismatch_boost,
                description="Sentiment model says positive, but delivery is terse — classic dry sarcasm.",
            ))

        # Signal 2: Short message ending with a period (deliberate abruptness)
        if (
            content.endswith(".")
            and baseline.get("period_rate", 0) < 0.3
            and len(words) < 5
        ):
            abrupt_boost = 0.2
            pa_score += abrupt_boost
            signals.append(TonalitySignal(
                type="abruptness",
                score_influence=abrupt_boost,
                description="Unexpected period at the end of a short message.",
            ))

        # Signal 3: Long delay followed by a very brief response
        if prev_msg and prev_msg.sender != msg.sender:
            delay = (msg.timestamp - prev_msg.timestamp).total_seconds()
            if delay > 300 and brevity > 0.8:
                delay_boost = 0.15
                pa_score += delay_boost
                signals.append(TonalitySignal(
                    type="delay",
                    score_influence=delay_boost,
                    description="Significant delay followed by a very brief response.",
                ))

        # Signal 4: All-lowercase + terminal punctuation (dismissive style)
        if (
            len(words) >= 1
            and content == content.lower()
            and content[-1] in ".!"
            and len(words) < 6
        ):
            casing_boost = 0.1
            pa_score += casing_boost
            signals.append(TonalitySignal(
                type="dismissive_casing",
                score_influence=casing_boost,
                description="All-lowercase with terminal punctuation — dismissive tone pattern.",
            ))

        return MessageTonality(
            message_id=msg_id,
            sender=msg.sender,
            dryness_score=round(float(np.clip(dryness_score, 0, 1)), 3),
            passive_aggression_score=round(float(np.clip(pa_score, 0, 1)), 3),
            confidence=0.85 if len(words) > 1 else 0.6,
            signals=signals,
        )

    # ------------------------------------------------------------------
    # Baselines + aggregation
    # ------------------------------------------------------------------

    def _calculate_baselines(self, messages: List[RawMessage]) -> Dict[str, Dict[str, Any]]:
        baselines: Dict[str, Dict] = {}
        for m in messages:
            if not m.sender or m.is_media:
                continue
            if m.sender not in baselines:
                baselines[m.sender] = {"lengths": [], "ends_with_period": 0, "total": 0}
            b = baselines[m.sender]
            b["lengths"].append(len(m.content.split()))
            if m.content.strip().endswith("."):
                b["ends_with_period"] += 1
            b["total"] += 1

        return {
            sender: {
                "avg_length": np.mean(d["lengths"]) if d["lengths"] else 0,
                "period_rate": d["ends_with_period"] / d["total"] if d["total"] > 0 else 0,
            }
            for sender, d in baselines.items()
        }

    def _aggregate_participants(
        self, tonalities: List[MessageTonality]
    ) -> List[ParticipantTonality]:
        p_map: Dict[str, Dict] = {}
        for t in tonalities:
            if not t.sender:
                continue
            if t.sender not in p_map:
                p_map[t.sender] = {"dry": [], "pa": [], "signals": []}
            p_map[t.sender]["dry"].append(t.dryness_score)
            p_map[t.sender]["pa"].append(t.passive_aggression_score)
            p_map[t.sender]["signals"].extend([s.type for s in t.signals])

        results = []
        for name, data in p_map.items():
            top_signals = (
                [item for item, _ in Counter(data["signals"]).most_common(3)]
                if data["signals"]
                else []
            )
            results.append(
                ParticipantTonality(
                    name=name,
                    avg_dryness=round(float(np.mean(data["dry"])), 3) if data["dry"] else 0.0,
                    avg_passive_aggression=round(float(np.mean(data["pa"])), 3)
                    if data["pa"]
                    else 0.0,
                    top_signals=top_signals,
                    consistency_score=round(
                        1.0 - float(np.std(data["dry"] or [0])), 3
                    ),
                )
            )
        return results

    def _calculate_summary(self, tonalities: List[MessageTonality]) -> Dict[str, Any]:
        if not tonalities:
            return {}

        avg_dry = np.mean([t.dryness_score for t in tonalities])
        avg_pa = np.mean([t.passive_aggression_score for t in tonalities])

        pa_scores = [t.passive_aggression_score for t in tonalities]
        window = 5
        tension_points = []
        if len(pa_scores) >= window:
            rolling_pa = np.convolve(pa_scores, np.ones(window) / window, mode="valid")
            max_idx = int(np.argmax(rolling_pa))
            if rolling_pa[max_idx] > 0.4:
                tension_points.append(
                    {"index": max_idx, "intensity": float(rolling_pa[max_idx])}
                )

        return {
            "overall_dryness": round(float(avg_dry), 3),
            "overall_passive_aggression": round(float(avg_pa), 3),
            "tension_points": tension_points,
        }
