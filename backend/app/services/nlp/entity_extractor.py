import spacy
from typing import List, Dict, Set, Optional, Tuple
from collections import Counter
import difflib
from .schemas import EntityMatch, ParticipantProfile, SpeakerDetectionResult
from ..preprocessing.schemas import PreprocessingResult, PreprocessedMessage
from app.core.config import settings
_SPACY_BATCH_SIZE = 64
class EntityExtractor:
    """
    Extracts people entities and resolves participants using spaCy.
    Optimization vs. original:
    - Replaced per-message `self.nlp(text)` calls with `self.nlp.pipe(texts)`
      which processes all messages in one efficient batched pass.
    """
    def __init__(self, model_name: str = settings.SPACY_MODEL, use_ner_for_mentions: bool = False, nlp: Optional[spacy.language.Language] = None):
        self.use_ner_for_mentions = use_ner_for_mentions
        self._model_name = model_name
        self._nlp = nlp
    @property
    def nlp(self) -> spacy.language.Language:
        if self._nlp is None:
            try:
                self._nlp = spacy.load(self._model_name)
            except OSError:
                import subprocess, sys
                subprocess.check_call(
                    [sys.executable, "-m", "spacy", "download", self._model_name]
                )
                self._nlp = spacy.load(self._model_name)
        return self._nlp
    def analyze_speakers(
        self, preprocessed_data: PreprocessingResult
    ) -> SpeakerDetectionResult:
        messages = preprocessed_data.messages
        participant_profiles: Dict[str, ParticipantProfile] = {}
        for msg in messages:
            sender = msg.raw.sender
            if sender and not msg.raw.is_system:
                if sender not in participant_profiles:
                    participant_profiles[sender] = ParticipantProfile(
                        name=sender, is_sender=True, aliases=[sender]
                    )
                participant_profiles[sender].messages_sent += 1
                participant_profiles[sender].words_total += msg.metadata.word_count
        all_mentions: List[EntityMatch] = []
        if self.use_ner_for_mentions:
            valid_messages = [
                m for m in messages if not (m.raw.is_system or m.raw.is_media)
            ]
            texts = [m.base_clean for m in valid_messages]
            docs = list(
                self.nlp.pipe(texts, batch_size=_SPACY_BATCH_SIZE, n_process=1)
            )
            for msg, doc in zip(valid_messages, docs):
                for ent in doc.ents:
                    if ent.label_ == "PERSON":
                        context = ent.sent.text if hasattr(ent, "sent") else None
                        match = EntityMatch(
                            text=ent.text,
                            label=ent.label_,
                            start_char=ent.start_char,
                            end_char=ent.end_char,
                            confidence=0.8,
                            message_id=msg.message_id,
                            context=context,
                        )
                        all_mentions.append(match)
                        self._resolve_entity(match, participant_profiles, msg)
        return self._finalize_analysis(participant_profiles, all_mentions, messages)
    def _resolve_entity(
        self,
        match: EntityMatch,
        profiles: Dict[str, ParticipantProfile],
        message: PreprocessedMessage,
    ):
        best_match_name = None
        highest_score = 0.0
        for p_name, profile in profiles.items():
            for alias in profile.aliases:
                if match.text.lower() == alias.lower():
                    best_match_name = p_name
                    highest_score = 1.0
                    break
            if best_match_name:
                break
        if not best_match_name:
            for p_name in profiles:
                parts = p_name.split()
                if len(parts) > 1 and match.text.lower() == parts[0].lower():
                    best_match_name = p_name
                    highest_score = 0.9
                    break
        if not best_match_name:
            for p_name, profile in profiles.items():
                score = difflib.SequenceMatcher(
                    None, match.text.lower(), p_name.lower()
                ).ratio()
                if score > 0.85 and score > highest_score:
                    highest_score = score
                    best_match_name = p_name
        if best_match_name:
            profile = profiles[best_match_name]
            profile.mentions.append(match)
            profile.mention_count += 1
            match.confidence = (match.confidence + highest_score) / 2
            if message.raw.sender:
                mentioned_by = profile.metadata.get("mentioned_by", Counter())
                mentioned_by[message.raw.sender] += 1
                profile.metadata["mentioned_by"] = mentioned_by
        else:
            name_key = match.text.strip()
            if name_key not in profiles:
                profiles[name_key] = ParticipantProfile(
                    name=name_key, is_sender=False, aliases=[name_key]
                )
            profiles[name_key].mentions.append(match)
            profiles[name_key].mention_count += 1
    def _finalize_analysis(
        self,
        profiles: Dict[str, ParticipantProfile],
        all_mentions: List[EntityMatch],
        messages: List[PreprocessedMessage],
    ) -> SpeakerDetectionResult:
        all_profiles = list(profiles.values())
        total_messages = len([m for m in messages if not m.raw.is_system])
        total_mentions = sum(p.mention_count for p in all_profiles)
        for profile in all_profiles:
            vol_score = (
                profile.messages_sent / total_messages if total_messages > 0 else 0
            )
            ment_score = (
                profile.mention_count / total_mentions if total_mentions > 0 else 0
            )
            profile.dominance_score = min(
                (vol_score * 0.7) + (ment_score * 0.3), 1.0
            )
            mentioned_by = profile.metadata.get("mentioned_by", {})
            unique_mentioners = len(mentioned_by)
            total_possible = (
                len([p for p in all_profiles if p.is_sender])
                - (1 if profile.is_sender else 0)
            )
            if total_possible > 0:
                profile.centrality_score = unique_mentioners / total_possible
        alias_map = {
            alias: p.name for p in all_profiles for alias in p.aliases
        }
        top_referenced = None
        most_dominant = None
        if all_profiles:
            top_referenced = max(all_profiles, key=lambda x: x.mention_count).name
            most_dominant = max(all_profiles, key=lambda x: x.dominance_score).name
        return SpeakerDetectionResult(
            participants=all_profiles,
            unidentified_entities=[],
            alias_map=alias_map,
            global_metrics={
                "top_referenced_person": top_referenced,
                "most_dominant_speaker": most_dominant,
                "total_entities_detected": total_mentions,
                "participant_count": len(all_profiles),
            },
        )
