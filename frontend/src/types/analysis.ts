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
  effort_level: ScoreMetadata;
  hidden_attitude: ScoreMetadata;
  self_focus: ScoreMetadata;
  manipulation_level: ScoreMetadata;
  red_flag_score: ScoreMetadata;
  peacemaker_index?: ScoreMetadata;
  instigator_score?: ScoreMetadata;
  chars_per_message?: ScoreMetadata;
  yap_score?: ScoreMetadata;
  clown_factor?: ScoreMetadata;
  simp_level?: ScoreMetadata;
  response_effort?: ScoreMetadata;
  apology_rate?: ScoreMetadata;
  top_emojis?: string[];
  swear_count?: number;
  late_night_ratio?: ScoreMetadata;
  response_time?: ScoreMetadata;
  conversation_starter?: ScoreMetadata;
  question_ratio?: ScoreMetadata;
  badges: string[];
  notable_quotes: NotableQuote[];
  message_count: number;
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
  participant_volumes?: Record<string, number>;
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
