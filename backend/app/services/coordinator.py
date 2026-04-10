from typing import List, Optional
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
from sentence_transformers import SentenceTransformer
import spacy
import logging
from .parser import WhatsAppParser, ParseResult, RawMessage
from .preprocessing import MessageCleaner, PreprocessingResult
from .nlp import (
    EntityExtractor,
    SentimentAnalyzer,
    ToxicityAnalyzer,
    TonalityAnalyzer,
    TopicAnalyzer,
    SpeakerDetectionResult,
    SentimentAnalysisResponse,
    ToxicityAnalysisResponse,
    TonalityAnalysisResponse,
    TopicAnalysisResponse,
)
from .scoring import ScoringEngine, ScoringResponse
from app.core.config import settings
_MAX_DEEP_ANALYSIS_MSGS = 600
_THREAD_WORKERS = 2
logger = logging.getLogger(__name__)
class AnalysisCoordinator:
    """
    Orchestrates the entire chat analysis pipeline.
    Key optimizations vs. original:
    1. One shared SentenceTransformer instance injected into TopicAnalyzer.
       TonalityAnalyzer no longer uses sentence-transformer (model-free scoring).
    2. Independent analyzers run concurrently via asyncio + ThreadPoolExecutor.
       Pipeline order:
         Round 1 (parallel): Sentiment | Toxicity | EntityExtractor
         Round 2 (parallel): Tonality (needs sentiment) | Topics
         Round 3 (sequential): Scoring (needs all results)
    3. Topic/Tonality receive a sampled message list for very long chats.
    """
    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=_THREAD_WORKERS)
        logger.info(f"Initializing Moodra Analyzers (Model: {settings.TOPIC_MODEL}, {settings.SPACY_MODEL})...")
        shared_embedder = SentenceTransformer(settings.TOPIC_MODEL)
        try:
            shared_nlp = spacy.load(settings.SPACY_MODEL)
        except OSError:
            import subprocess, sys
            subprocess.check_call([sys.executable, "-m", "spacy", "download", settings.SPACY_MODEL])
            shared_nlp = spacy.load(settings.SPACY_MODEL)
        self.parser = WhatsAppParser()
        self.cleaner = MessageCleaner(nlp=shared_nlp)
        self.nlp = EntityExtractor(nlp=shared_nlp)
        self.sentiment = SentimentAnalyzer()
        self.toxicity = ToxicityAnalyzer()
        self.tonality = TonalityAnalyzer(nlp=shared_nlp)
        self.topics = TopicAnalyzer(embedder=shared_embedder)
        self.scoring = ScoringEngine()
    def warm_up(self):
        """Explicitly load all lazy ML models to avoid cold-start lag."""
        import time
        start = time.time()
        logger.info("Warming up ML models (Sentiment, Toxicity)...")
        _ = self.sentiment.pipeline
        _ = self.toxicity.pipeline
        _ = self.topics.model
        duration = round(time.time() - start, 2)
        logger.info(f"Warm-up complete in {duration}s. All systems ready.")
    def _run_sync(self, fn, *args):
        """Submit a synchronous callable to the thread pool."""
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(self._executor, fn, *args)
    @staticmethod
    def _sample_messages(
        messages: List[RawMessage], max_count: int
    ) -> List[RawMessage]:
        """
        Return a uniform sample of messages when the chat is very long.
        We always include the first and last message to preserve timeline context.
        """
        if len(messages) <= max_count:
            return messages
        step = len(messages) / max_count
        indices = sorted(set(
            [0]
            + [round(i * step) for i in range(1, max_count - 1)]
            + [len(messages) - 1]
        ))
        return [messages[i] for i in indices]
    async def run_full_analysis(self, raw_text: str) -> ScoringResponse:
        """Executes the full analysis pipeline with parallelism."""
        try:
            parse_result: ParseResult = self.parser.parse_text(raw_text)
            preprocessing_result: PreprocessingResult = self.cleaner.process_sequence(
                parse_result.messages
            )
            raw_msgs = [m.raw for m in preprocessing_result.messages]
            deep_msgs_raw = self._sample_messages(raw_msgs, _MAX_DEEP_ANALYSIS_MSGS)
            deep_msgs_preprocessed = self._sample_messages(
                preprocessing_result.messages, _MAX_DEEP_ANALYSIS_MSGS
            )
            sentiment_fut = self._run_sync(self.sentiment.analyze_chat, raw_msgs)
            toxicity_fut = self._run_sync(self.toxicity.analyze_chat, raw_msgs)
            speakers_fut = self._run_sync(
                self.nlp.analyze_speakers, preprocessing_result
            )
            sentiment, toxicity, speakers = await asyncio.gather(
                sentiment_fut, toxicity_fut, speakers_fut
            )
            sampled_sentiment_msgs = sentiment.messages[: len(deep_msgs_raw)]
            tonality_fut = self._run_sync(
                self.tonality.analyze_chat,
                deep_msgs_raw,
                sampled_sentiment_msgs,
            )
            topics_fut = self._run_sync(
                self.topics.analyze, deep_msgs_preprocessed
            )
            tonality, topics = await asyncio.gather(tonality_fut, topics_fut)
            final_scores: ScoringResponse = self.scoring.analyze(
                preprocessed=preprocessing_result,
                speakers=speakers,
                sentiment=sentiment,
                toxicity=toxicity,
                tonality=tonality,
                topics=topics,
            )
            return final_scores
        finally:
            for name in ("raw_text", "parse_result", "raw_msgs"):
                if name in locals():
                    del locals()[name]
    async def analyze_file_content(self, content_bytes: bytes) -> ScoringResponse:
        """Decodes file content and runs analysis."""
        try:
            try:
                raw_text = content_bytes.decode("utf-8-sig")
            except UnicodeDecodeError:
                try:
                    raw_text = content_bytes.decode("utf-16")
                except UnicodeDecodeError:
                    raw_text = content_bytes.decode("latin-1", errors="replace")
            del content_bytes
            return await self.run_full_analysis(raw_text)
        finally:
            if "raw_text" in locals():
                del locals()["raw_text"]
