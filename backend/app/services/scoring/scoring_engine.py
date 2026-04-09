import numpy as np
from typing import List, Dict, Any, Optional
from scipy.special import expit # sigmoid function for normalization

from ..nlp.schemas import (
    SpeakerDetectionResult,
    SentimentAnalysisResponse,
    ToxicityAnalysisResponse,
    TonalityAnalysisResponse,
    TopicAnalysisResponse
)
from ..preprocessing.schemas import PreprocessingResult
from .schemas import (
    ScoringResponse, 
    ParticipantScoring, 
    SegmentScoring, 
    StandoutCard, 
    ScoreMetadata,
    NotableQuote
)

class ScoringEngine:
    """Aggregates low-level NLP features into high-level conversation metrics."""

    def __init__(self):
        # Weight configurations for different metrics
        self.tension_weights = {
            "toxicity": 0.5,
            "negative_sentiment": 0.3,
            "low_positivity": 0.1,
            "volatility": 0.1
        }
        
        self.dominance_weights = {
            "msg_ratio": 0.4,
            "word_ratio": 0.4,
            "opener_ratio": 0.2
        }

    def analyze(
        self,
        preprocessed: PreprocessingResult,
        speakers: SpeakerDetectionResult,
        sentiment: SentimentAnalysisResponse,
        toxicity: ToxicityAnalysisResponse,
        tonality: TonalityAnalysisResponse,
        topics: TopicAnalysisResponse
    ) -> ScoringResponse:
        """The main entry point for the scoring layer."""
        
        # 1. Map messages to their respective analysis objects for easier lookup
        msg_map = self._build_message_map(preprocessed, sentiment, toxicity, tonality)
        
        # 2. Calculate Participant Scoring
        participant_scores = self._calculate_participant_metrics(
            speakers, sentiment, toxicity, tonality, topics, msg_map
        )
        
        # 3. Calculate Segment-level Scoring
        segment_scores = self._calculate_segment_metrics(
            topics, sentiment, toxicity, tonality, speakers, msg_map
        )
        
        # 4. Generate Timeline (Chart data)
        timeline = self._generate_timeline(sentiment, toxicity, tonality, topics, preprocessed, speakers)
        
        # 5. Generate Standout Cards
        standout_cards = self._generate_standout_cards(
            participant_scores, segment_scores, sentiment, toxicity
        )
        
        # 6. Overall Mood and Summary
        overall_mood = self._determine_overall_mood(sentiment, toxicity, tonality)
        overall_summary = self._generate_overall_summary(overall_mood, participant_scores)
        roast_summary = self._generate_roast(overall_mood, participant_scores, standout_cards)

        return ScoringResponse(
            overall_summary=overall_summary,
            roast_summary=roast_summary,
            overall_mood=overall_mood,
            participants=participant_scores,
            segments=segment_scores,
            timeline=timeline,
            standout_cards=standout_cards,
            global_metrics={
                "conversation_health": self._calculate_health(toxicity, sentiment),
                "total_messages": len(preprocessed.messages)
            }
        )

    def _build_message_map(self, preprocessed, sentiment, toxicity, tonality) -> Dict[int, Dict[str, Any]]:
        """Helpers to index messages by ID across all analysis results."""
        m_map: Dict[int, Dict[str, Any]] = {}
        
        for pm in preprocessed.messages:
            m_map[pm.message_id] = {
                "text": pm.base_clean,
                "sender": pm.raw.sender,
                "sentiment": None,
                "toxicity": None,
                "tonality": None
            }
            
        for s in sentiment.messages:
            if s.message_id in m_map:
                m_map[s.message_id]["sentiment"] = s
            
        for t in toxicity.messages:
            if t.message_id in m_map:
                m_map[t.message_id]["toxicity"] = t
            
        for tn in tonality.messages:
            if tn.message_id in m_map:
                m_map[tn.message_id]["tonality"] = tn
            
        return m_map

    def _calculate_participant_metrics(
        self, speakers, sentiment, toxicity, tonality, topics, msg_map
    ) -> List[ParticipantScoring]:
        results = []
        
        # Get baseline for normalization
        total_msgs = sum(p.messages_sent for p in speakers.participants)
        total_words = sum(p.words_total for p in speakers.participants)
        
        for p_profile in speakers.participants:
            # A. Dominance calculation
            msg_ratio = p_profile.messages_sent / total_msgs if total_msgs > 0 else 0
            word_ratio = p_profile.words_total / total_words if total_words > 0 else 0
            # Opener logic could be added here (e.g. who sent the first msg in segments)
            
            dom_val = (msg_ratio * self.dominance_weights["msg_ratio"] +
                       word_ratio * self.dominance_weights["word_ratio"])
            # Weighting it up to feel more granular
            dom_val = min(1.0, dom_val * 1.5) 
            
            dominance = ScoreMetadata(
                value=dom_val,
                label=self._get_label_for_score(dom_val, ["Listener", "Active", "Driver", "Shot-caller"]),
                explanation=f"Responsible for {msg_ratio:.1%} of messages and {word_ratio:.1%} of word volume.",
                confidence=0.9
            )
            
            # B. Tonality stats (Dryness / Passive Aggression)
            p_tonality = next((t for t in tonality.participants if t.name == p_profile.name), None)
            dry_val = p_tonality.avg_dryness if p_tonality else 0.0
            pa_val = p_tonality.avg_passive_aggression if p_tonality else 0.0
            
            effort_level = ScoreMetadata(
                value=dry_val,
                label=self._get_label_for_score(dry_val, ["Warm", "Normal", "Direct", "Dry AF"]),
                explanation="Based on word count, punctuation usage, and response latency.",
                confidence=0.8
            )
            
            hidden_attitude = ScoreMetadata(
                value=pa_val,
                label=self._get_label_for_score(pa_val, ["Chill", "Direct", "Slightly Edgy", "Highly P.A."]),
                explanation="Calculated by mismatch between sentiment and tone signals.",
                confidence=0.75
            )
            
            # C. Main Character Energy: High dominance + being mentioned
            mention_ratio = p_profile.mention_count / (total_msgs * 0.1 + 1)
            mce_val = (dom_val * 0.6 + min(1.0, mention_ratio * 2) * 0.4)
            
            self_focus = ScoreMetadata(
                value=mce_val,
                label=self._get_label_for_score(mce_val, ["NPC", "Supporting", "Main Story", "The Protagonist"]),
                explanation="A combination of how much they speak and how much they are the subject of conversation.",
                confidence=0.7
            )
            
            # D. Badges
            badges = []
            if dom_val > 0.7: badges.append("The Driver")
            if dry_val > 0.6: badges.append("Very Dry")
            if pa_val > 0.6: badges.append("Hidden Attitude")
            if mce_val > 0.8: badges.append("Self Focus")
            
            # E. Gaslighting Index (High Dominance + High PA + Low variability -> confident manipulation)
            gaslight_val = (dom_val * 0.4) + (pa_val * 0.6)
            manipulation_level = ScoreMetadata(
                value=gaslight_val,
                label=self._get_label_for_score(gaslight_val, ["Innocent", "Slightly Sus", "Manipulative", "Master Gaslighter"]),
                explanation="Calculated via combination of conversational dominance and latent passive-aggression.",
                confidence=0.75
            )

            # F. Red Flag Score
            p_tox = next((t for t in toxicity.participants if t.name == p_profile.name), None)
            tox_val = p_tox.intensity_index if p_tox else 0.0
            rf_val = (tox_val * 0.4) + (pa_val * 0.3) + (dry_val * 0.1) + (dom_val * 0.2)
            rf_val = min(1.0, rf_val * 1.3)
            red_flag_score = ScoreMetadata(
                value=rf_val,
                label=self._get_label_for_score(rf_val, ["Green Flag", "Yellow Flag", "Walking Red Flag", "Nuclear Hazard"]),
                explanation="Aggregated toxicity, emotional withdrawal, and passive aggression markers.",
                confidence=0.8
            )
            
            # Group Attributes calculations
            p_sent_score = sum(getattr(msg_map.get(m, {}).get("sentiment"), "score", 0.0) for m in range(max(1, total_msgs)) if msg_map.get(m, {}).get("sender") == p_profile.name)
            p_sent_avg = p_sent_score / max(1, p_profile.messages_sent)
            
            pm_val = max(0.0, (1.0 - tox_val) * (0.5 + p_sent_avg * 0.5))
            peacemaker_index = ScoreMetadata(value=pm_val, label=self._get_label_for_score(pm_val, ["Stirrer", "Neutral", "De-escalator", "The UN"]), explanation="Attempts to restore peace.", confidence=0.6)
            
            inst_val = min(1.0, tox_val * dom_val * 1.5)
            instigator_score = ScoreMetadata(value=inst_val, label=self._get_label_for_score(inst_val, ["Peaceful", "Slightly Messy", "Pot Stirrer", "Chaos Agent"]), explanation="Generates conflict and engagement spikes.", confidence=0.7)
            
            ghost_val = max(0.0, 1.0 - dom_val)
            ghost_level = ScoreMetadata(value=ghost_val, label=self._get_label_for_score(ghost_val, ["Always There", "Occasional", "Rare Appearance", "The Ghost"]), explanation="Present but rarely speaks.", confidence=0.8)
            
            yap_val = min(1.0, word_ratio * 2.0)
            yap_score = ScoreMetadata(value=yap_val, label=self._get_label_for_score(yap_val, ["Silent", "Talkative", "Yapper", "Chief Yapping Officer"]), explanation="High word volume.", confidence=0.9)
            
            clown_val = min(1.0, (pa_val * 0.2 + p_sent_avg * 0.5 + dom_val * 0.3) * 1.5)
            clown_factor = ScoreMetadata(value=clown_val, label=self._get_label_for_score(clown_val, ["Serious", "Casual", "Joker", "Meme Lord"]), explanation="Humor and comedic relief.", confidence=0.6)
            
            # Dyad Attributes calculations
            simp_val = max(0.0, p_sent_avg * dom_val * 1.2)
            simp_level = ScoreMetadata(value=simp_val, label=self._get_label_for_score(simp_val, ["Independent", "Caring", "Devoted", "Mega Simp"]), explanation="High affection output.", confidence=0.7)
            
            resp_val = max(0.0, 1.0 - dry_val)
            response_effort = ScoreMetadata(value=resp_val, label=self._get_label_for_score(resp_val, ["One Word", "Basic", "Thoughtful", "Paragraphs"]), explanation="Effort placed in replies.", confidence=0.8)
            
            apology_rate = ScoreMetadata(value=0.1, label="Average", explanation="Apology frequency", confidence=0.5)

            # G. Badges Addition
            if gaslight_val > 0.7: badges.append("The Gaslighter")
            if rf_val > 0.8: badges.append("Walking Red Flag")
            elif rf_val < 0.2: badges.append("Green Flag Status")
            if yap_val > 0.8: badges.append("CEO of Yapping")
            if inst_val > 0.7: badges.append("Drama Starter")
            if ghost_val > 0.8: badges.append("The Ghost")
            if pm_val > 0.7: badges.append("The Peacemaker")
            
            # H. Extract Notable Quotes (The Receipts)
            notable_quotes = []
            user_msgs = [(mid, data) for mid, data in msg_map.items() if data.get("sender") == p_profile.name]
            
            if user_msgs:
                # 1. Biggest Red Flag (Max Toxicity)
                red_flag_msg = max(user_msgs, key=lambda x: getattr(x[1].get("toxicity"), "score", 0.0) if x[1].get("toxicity") else 0.0, default=None)
                if red_flag_msg and self._x_tox(red_flag_msg[1]) > 0.4:
                     notable_quotes.append(NotableQuote(
                         message_id=red_flag_msg[0], 
                         text=red_flag_msg[1]["text"], 
                         context="Biggest Red Flag 🚩"
                     ))

                # 2. Most Passive Aggressive
                pa_msg = max(user_msgs, key=lambda x: getattr(x[1].get("tonality"), "passive_aggression_score", 0.0) if x[1].get("tonality") else 0.0, default=None)
                if pa_msg and self._x_pa(pa_msg[1]) > 0.4 and pa_msg[0] not in [q.message_id for q in notable_quotes]:
                     notable_quotes.append(NotableQuote(
                         message_id=pa_msg[0], 
                         text=pa_msg[1]["text"], 
                         context="Passive Aggression 🙄"
                     ))

                # 3. Very Dry (filter short texts)
                dry_msg = max(user_msgs, key=lambda x: getattr(x[1].get("tonality"), "dryness_score", 0.0) if x[1].get("tonality") else 0.0, default=None)
                if dry_msg and self._x_dry(dry_msg[1]) > 0.5 and dry_msg[0] not in [q.message_id for q in notable_quotes]:
                     notable_quotes.append(NotableQuote(
                         message_id=dry_msg[0], 
                         text=dry_msg[1]["text"], 
                         context="Very Dry 🌵"
                     ))
                     
                # 4. Most Wholesome (Max Positive Sentiment)
                wholesome_msg = max(user_msgs, key=lambda x: getattr(x[1].get("sentiment"), "score", 0.0) if x[1].get("sentiment") else 0.0, default=None)
                if wholesome_msg and self._x_sent(wholesome_msg[1]) > 0.6 and wholesome_msg[0] not in [q.message_id for q in notable_quotes]:
                     notable_quotes.append(NotableQuote(
                         message_id=wholesome_msg[0], 
                         text=wholesome_msg[1]["text"], 
                         context="A Rare Wholesome Moment 💚"
                     ))
                     
            results.append(ParticipantScoring(
                name=p_profile.name,
                dominance=dominance,
                effort_level=effort_level,
                hidden_attitude=hidden_attitude,
                self_focus=self_focus,
                manipulation_level=manipulation_level,
                red_flag_score=red_flag_score,
                peacemaker_index=peacemaker_index,
                instigator_score=instigator_score,
                ghost_level=ghost_level,
                yap_score=yap_score,
                clown_factor=clown_factor,
                simp_level=simp_level,
                response_effort=response_effort,
                apology_rate=apology_rate,
                badges=badges,
                notable_quotes=notable_quotes
            ))
            
        return results

    # Helpers for quote extraction
    def _x_tox(self, x): return getattr(x.get("toxicity"), "score", 0.0) if x.get("toxicity") else 0.0
    def _x_pa(self, x): return getattr(x.get("tonality"), "passive_aggression_score", 0.0) if x.get("tonality") else 0.0
    def _x_dry(self, x): return getattr(x.get("tonality"), "dryness_score", 0.0) if x.get("tonality") else 0.0
    def _x_sent(self, x): return getattr(x.get("sentiment"), "score", 0.0) if x.get("sentiment") else 0.0

    def _calculate_segment_metrics(
        self, topics, sentiment, toxicity, tonality, speakers, msg_map
    ) -> List[SegmentScoring]:
        results = []
        for seg in topics.segments:
            # Aggregate-based segment scoring
            tension_val = self._calculate_range_tension(seg, toxicity, sentiment)
            
            # Find the most notable message in this segment
            seg_msg_ids = list(range(seg.start_id, seg.end_id + 1))
            notable_id = self._rank_notable_messages(seg_msg_ids, msg_map)
            
            results.append(SegmentScoring(
                segment_id=seg.id,
                topic_label=seg.label,
                tension=ScoreMetadata(
                    value=tension_val,
                    label=self._get_label_for_score(tension_val, ["Chill", "Rising", "Tense", "Explosive"]),
                    explanation="Determined by shifts in toxicity and sentiment within this topic.",
                    confidence=0.8
                ),
                mood=self._determine_segment_mood(seg),
                notable_message_id=notable_id,
                notable_reason="This message stood out due to its unusual intensity or tone markers." if notable_id else None
            ))
        return results

    def _generate_timeline(self, sentiment, toxicity, tonality, topics, preprocessed=None, speakers=None) -> List[Dict[str, Any]]:
        # Syncing sentiment timeline with toxicity peaks to compute true tension
        timeline = []
        num_bins = len(sentiment.timeline)
        if num_bins == 0:
            return timeline
            
        # Distribute toxicity scores into bins
        tox_scores = [m.score for m in toxicity.messages]
        bin_size = len(tox_scores) / num_bins if len(tox_scores) > 0 else 1
        
        # Calculate per-participant message counts per bin
        participant_names = [p.name for p in speakers.participants] if speakers else []
        all_messages = preprocessed.messages if preprocessed else []
        total_msgs = len(all_messages)
        msgs_per_bin = total_msgs / num_bins if num_bins > 0 else total_msgs
        
        for i, point in enumerate(sentiment.timeline):
            # Toxicity binning
            tox_start = int(i * bin_size)
            tox_end = int((i + 1) * bin_size)
            bin_tox = tox_scores[tox_start:tox_end]
            avg_bin_tox = sum(bin_tox) / len(bin_tox) if bin_tox else 0.0
            
            # Tension peaks when sentiment is highly negative OR toxicity is high
            sent_tension = max(0.0, -point.average_score) * 0.6
            tension_val = min(1.0, sent_tension + avg_bin_tox * 0.6)
            
            # Per-participant message count in this bin
            msg_start = int(i * msgs_per_bin)
            msg_end = int((i + 1) * msgs_per_bin)
            bin_messages = all_messages[msg_start:msg_end]
            participant_volumes = {}
            for name in participant_names:
                participant_volumes[name] = sum(1 for m in bin_messages if m.raw.sender == name)
            
            timeline.append({
                "time": point.label,
                "sentiment": point.average_score,
                "volume": point.volume,
                "tension": tension_val,
                "participant_volumes": participant_volumes
            })
        return timeline

    def _generate_standout_cards(self, participants, segments, sentiment, toxicity) -> List[StandoutCard]:
        cards = []
        # Example achievement
        top_mce = max(participants, key=lambda x: x.self_focus.value, default=None)
        if top_mce and top_mce.self_focus.value > 0.5:
             cards.append(StandoutCard(
                type="award",
                title="The Center of Attention",
                recipient=top_mce.name,
                description="This conversation was basically their solo performance. Everyone else was just listening.",
                icon_hint="crown"
            ))
             
        # Example red flag
        most_dry = max(participants, key=lambda x: x.effort_level.value, default=None)
        if most_dry and most_dry.effort_level.value > 0.6:
            cards.append(StandoutCard(
                type="red_flag",
                title="The Silent Treatment",
                recipient=most_dry.name,
                description="Response energy is extremely low. Talking to them feels like sending messages into a void.",
                icon_hint="ice-cube"
            ))

        return cards

    def _determine_overall_mood(self, sentiment, toxicity, tonality) -> str:
        s_score = sentiment.summary_metrics["overall_sentiment"]
        t_intense = toxicity.global_intensity
        
        if t_intense > 0.5: return "Chaotic / Aggressive"
        if s_score == "positive": return "Wholesome & Energetic"
        if s_score == "negative": return "Drained or Heavy"
        return "Typical / Varied"

    def _generate_overall_summary(self, mood, participant_scores) -> str:
        # Probabilistic summarizer
        return f"This conversation was {mood.lower()}. " \
               "The dynamics were driven by significant shifts in engagement."

    def _generate_roast(self, mood, participant_scores, standout_cards) -> str:
        # A brutally honest assessment
        roast = ""
        top_tox = max(participant_scores, key=lambda x: x.red_flag_score.value, default=None)
        if top_tox and top_tox.red_flag_score.value > 0.6:
            roast = f"Basically, {top_tox.name} needs a therapist. "
        elif mood == "Drained or Heavy":
            roast = "This chat is an absolute emotional vampire. Everyone needs some vitamin D. "
        elif mood == "Chaos / Aggressive":
            roast = "This group chat should be illegal. Pure unadulterated hostility. "
        else:
            roast = "Y'all are actually kinda boring. "

        most_dry = max(participant_scores, key=lambda x: x.effort_level.value, default=None)
        if most_dry and most_dry.effort_level.value > 0.6:
            roast += f" Also, talking to {most_dry.name} is like talking to a wall that occasionally sighs."
            
        manipulator = max(participant_scores, key=lambda x: x.manipulation_level.value, default=None)
        if manipulator and manipulator.manipulation_level.value > 0.7:
            roast += f" {manipulator.name} is lowkey manipulating everyone and they think we don't notice."

        if not roast.strip():
            roast = "Honestly, this chat is so aggressively mid there's almost nothing to roast."

        return roast

    def _get_label_for_score(self, score: float, labels: List[str]) -> str:
        """Helper to map 0-1 score to an array of labels."""
        idx = int(score * (len(labels) - 1))
        return labels[min(idx, len(labels) - 1)]

    def _rank_notable_messages(self, msg_ids: List[int], msg_map: Dict[int, Dict[str, Any]]) -> Optional[int]:
        """Rank messages in a list by how 'notable' they are."""
        if not msg_ids: return None
        
        scores = []
        for mid in msg_ids:
            m_data = msg_map.get(mid, {})
            # Score logic: toxicity + absolute sentiment variation + tonality intensity
            # Toxicity (high weight)
            t_val = getattr(m_data.get("toxicity"), "score", 0.0)
            # Sentiment absolute distance from neutral (0.0 is neutral)
            s_val = abs(getattr(m_data.get("sentiment"), "score", 0.0))
            # Passive aggression (if high, very notable)
            pa_val = getattr(m_data.get("tonality"), "passive_aggression_score", 0.0)
            
            # Combine scores with weights
            composite = (t_val * 0.5) + (s_val * 0.3) + (pa_val * 0.2)
            scores.append((mid, composite))
            
        # Return the best one
        if not scores: return None
        return max(scores, key=lambda x: x[1])[0]

    def _calculate_range_tension(self, segment, toxicity, sentiment) -> float:
        """Calculate tension for specific segment by averaging and peak-finding toxicity."""
        seg_toxicity = [m.score for m in toxicity.messages if segment.start_id <= m.message_id <= segment.end_id]
        if not seg_toxicity: return 0.0
        
        avg_tox = np.mean(seg_toxicity)
        max_tox = np.max(seg_toxicity)
        
        # Tension is high if either high avg or high peaks
        val = (avg_tox * 0.4) + (max_tox * 0.6)
        # Apply sigmoid to make it more sensitive at the edges
        return float(expit((val - 0.2) * 10))

    def _determine_segment_mood(self, segment) -> str:
        # Based on average sentiment of segment
        s_avg = segment.sentiment_avg if segment.sentiment_avg is not None else 0.0
        if s_avg > 0.4: return "Wholesome"
        if s_avg < -0.4: return "Heavy / Heated"
        return "Standard"

    def _calculate_health(self, toxicity, sentiment) -> float:
        # (1 - toxicity) * positivity_bias
        t_base = 1.0 - toxicity.global_intensity
        # Sentiment can dampen health if extremely negative or dry
        return max(0.0, min(1.0, t_base))
