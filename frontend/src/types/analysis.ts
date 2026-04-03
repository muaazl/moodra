export interface ScoreMetadata {
  value: number;
  label: string;
  explanation: string;
  confidence: number;
}

export interface NotableQuote {
  message_id: number | null;
  text: string;
  context: string;
}

export interface ParticipantScoring {
  name: string;
  dominance: ScoreMetadata;
  dry_texting: ScoreMetadata;
  passive_aggression: ScoreMetadata;
  main_character_energy: ScoreMetadata;
  gaslighting_index: ScoreMetadata;
  red_flag_score: ScoreMetadata;
  badges: string[];
  notable_quotes: NotableQuote[];
}

export interface SegmentScoring {
  segment_id: number;
  topic_label: string;
  tension: number;
  mood: string;
  notable_message_id?: number | null;
  notable_reason?: string | null;
}

export interface TimelinePoint {
  time: string;
  sentiment: number;
  volume: number;
  tension: number;
}

export interface StandoutCard {
  title: string;
  description: string;
  type: 'award' | 'red_flag' | 'statistic';
  icon?: string;
}

export interface GlobalMetrics {
  conversation_health: number;
  total_messages: number;
}

export interface ScoringResponse {
  overall_summary: string;
  roast_summary: string;
  overall_mood: string;
  participants: ParticipantScoring[];
  segments: SegmentScoring[];
  timeline: TimelinePoint[];
  standout_cards: StandoutCard[];
  global_metrics: GlobalMetrics;
}

export interface AnalysisSuccessResponse {
  status: 'success';
  data: ScoringResponse;
  metadata: {
    timestamp: string;
    processing_time: number;
  };
}

export interface AnalysisRequest {
  text: string;
  options?: {
    anonymize?: boolean;
  };
}
