'use client';
import React from 'react';
import { ParticipantScoring, ScoreMetadata } from '@/types/analysis';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { User, MessageSquare, Quote } from 'lucide-react';
interface ParticipantCardProps {
  participant: ParticipantScoring;
}
const ScoreMetric: React.FC<{
  label: string;
  subLabel: string;
  data: ScoreMetadata;
  color: string;
}> = ({ label, subLabel, data, color }) => {
  const percentage = Math.round(data.value * 100);
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div>
          <span className="text-xs font-bold text-zinc-700 uppercase tracking-wider">{subLabel}</span>
          <p className="text-[10px] text-zinc-400">{label}</p>
        </div>
        <div className="text-right">
          <span className="text-sm font-black text-zinc-800 font-mono">{percentage}%</span>
          <p className={`text-[10px] font-bold ${color}`}>{data.label}</p>
        </div>
      </div>
      <div className="h-1.5 w-full bg-black/5 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500`}
          style={{
            width: `${percentage}%`,
            backgroundColor: color.includes('teal') ? '#128C7E'
              : color.includes('purple') ? '#8b5cf6'
              : color.includes('amber') ? '#f59e0b'
              : color.includes('red') ? '#ef4444'
              : color.includes('blue') ? '#3b82f6'
              : color.includes('pink') ? '#ec4899'
              : color.includes('green') ? '#25D366'
              : color.includes('zinc') ? '#a1a1aa'
              : '#128C7E'
          }}
        />
      </div>
    </div>
  );
};
export const ParticipantCard: React.FC<ParticipantCardProps> = ({ participant }) => {
  const rfScore = Math.round(participant.red_flag_score.value * 100);
  let verdictLabel = 'Green Flag';
  let verdictColor = 'text-[var(--color-wa-green)]';
  let verdictBg = 'bg-[var(--color-wa-green)]/5 border-[var(--color-wa-green)]/15';
  if (rfScore > 60) {
    verdictLabel = 'Red Flag';
    verdictColor = 'text-red-600';
    verdictBg = 'bg-red-50 border-red-200';
  } else if (rfScore > 35) {
    verdictLabel = 'Yellow Flag';
    verdictColor = 'text-amber-600';
    verdictBg = 'bg-amber-50 border-amber-200';
  }
  return (
    <Card className="bg-white/80 backdrop-blur-sm border-black/5 overflow-hidden relative group hover:border-black/10 transition-all duration-300 shadow-sm">
      <div className="absolute top-0 right-0 p-4 opacity-[0.03] group-hover:opacity-5 transition-opacity pointer-events-none">
        <User size={120} strokeWidth={1} />
      </div>
      <CardHeader className="relative pb-0 pt-6">
        <div className="flex flex-col sm:flex-row sm:items-center space-y-4 sm:space-y-0 sm:space-x-4">
          <Avatar className="h-14 w-14 border-2 border-white shadow-sm ring-4 ring-[var(--color-wa-green)]/10">
            <AvatarFallback className="bg-[var(--color-wa-teal)] text-white text-lg font-bold">
              {participant.name.substring(0, 2).toUpperCase()}
            </AvatarFallback>
          </Avatar>
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <h3 className="text-xl font-black text-zinc-900 tracking-tight">{participant.name}</h3>
              {participant.top_emojis && participant.top_emojis.length > 0 && (
                <span className="text-lg tracking-widest">{participant.top_emojis.join('')}</span>
              )}
            </div>
            <div className="flex flex-wrap gap-1.5 mt-1">
              <Badge className={`${verdictBg} ${verdictColor} border text-[10px] px-2.5 py-0.5 font-bold`}>
                {verdictLabel}
              </Badge>
              {participant.message_count !== undefined && (
                <Badge variant="outline" className="text-zinc-500 bg-white/50 border-zinc-200 text-[10px] px-2 py-0.5 font-bold">
                  {participant.message_count} Messages
                </Badge>
              )}
              {participant.swear_count !== undefined && participant.swear_count > 0 && (
                <Badge variant="outline" className="text-red-500 bg-red-50 border-red-200 text-[10px] px-2 py-0.5 font-bold">
                  Swear Jar: {participant.swear_count}
                </Badge>
              )}
              {participant.badges.slice(0, 3).map((badge, idx) => (
                <Badge
                  key={idx}
                  variant="secondary"
                  className="bg-black/[0.03] text-zinc-600 border-none text-[10px] px-2 py-0.5 font-semibold"
                >
                  {badge}
                </Badge>
              ))}
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-5 space-y-5 relative">
        {}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-zinc-50/50 p-4 rounded-xl border border-black/5">
          <ScoreMetric subLabel="Presence" label="Self Focus" data={participant.self_focus} color="text-teal-600" />
          <ScoreMetric subLabel="Manipulation" label="Manipulation Level" data={participant.manipulation_level} color="text-purple-600" />
          <ScoreMetric subLabel="Dryness" label="Effort Level" data={participant.effort_level} color="text-amber-600" />
          <ScoreMetric subLabel="Red Flag" label="Red Flag Score" data={participant.red_flag_score} color="text-red-600" />
        </div>
        {}
        {(participant.yap_score || participant.simp_level) && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-zinc-50/50 p-4 rounded-xl border border-black/5">
            {participant.yap_score && (
              <>
                <ScoreMetric subLabel="Volume" label="Yap Score" data={participant.yap_score} color="text-blue-600" />
                <ScoreMetric subLabel="Drama" label="Instigator Score" data={participant.instigator_score!} color="text-red-500" />
                <ScoreMetric subLabel="Harmony" label="Peacemaker Index" data={participant.peacemaker_index!} color="text-green-600" />
                <ScoreMetric subLabel="Content" label="Chars / Msg" data={participant.chars_per_message!} color="text-indigo-600" />
              </>
            )}
            {participant.simp_level && (
              <>
                <ScoreMetric subLabel="Devotion" label="Simp Level" data={participant.simp_level} color="text-pink-600" />
                <ScoreMetric subLabel="Energy" label="Response Effort" data={participant.response_effort!} color="text-blue-500" />
              </>
            )}
          </div>
        )}
        {}
        {(participant.response_time || participant.conversation_starter || participant.late_night_ratio || participant.question_ratio) && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-[var(--color-wa-bg)]/30 p-4 rounded-xl border border-black/5">
            {participant.response_time && <ScoreMetric subLabel="Speed" label="Leaves on Read" data={participant.response_time} color="text-amber-500" />}
            {participant.conversation_starter && <ScoreMetric subLabel="Initiative" label="Chat Starter" data={participant.conversation_starter} color="text-teal-500" />}
            {participant.late_night_ratio && <ScoreMetric subLabel="Time Preference" label="Night Owl" data={participant.late_night_ratio} color="text-slate-600" />}
            {participant.question_ratio && <ScoreMetric subLabel="Inquisitive" label="Asks Lots of Questions" data={participant.question_ratio} color="text-purple-500" />}
          </div>
        )}
        {}
        <div className="mt-4 space-y-3">
          <div className="flex items-center space-x-2 border-b border-black/5 pb-2">
            <Quote className="w-4 h-4 text-[var(--color-wa-teal)]" />
            <h4 className="text-xs font-black text-zinc-800 uppercase tracking-widest">The Receipts</h4>
          </div>
          <div className="space-y-3 bg-[var(--color-wa-bg)] p-4 rounded-xl border border-black/5 relative overflow-hidden">
             <div 
                className="absolute inset-0 pointer-events-none opacity-[0.04] z-[0]" 
                style={{ backgroundImage: 'url(/whatsapp_bg.png)', backgroundSize: '200px' }}
             />
            {participant.notable_quotes && participant.notable_quotes.length > 0 ? (
              <div className="space-y-4 relative z-10 max-h-[400px] overflow-y-auto hide-scrollbar pb-2 pt-1">
                {Object.entries(
                  participant.notable_quotes.reduce((acc, quote) => {
                    if (!acc[quote.context]) acc[quote.context] = [];
                    acc[quote.context].push(quote);
                    return acc;
                  }, {} as Record<string, typeof participant.notable_quotes>)
                ).map(([context, quotes], idx) => (
                  <div key={idx} className="flex flex-col space-y-1">
                    <span className="text-[10px] font-bold text-zinc-500 mb-1 ml-1 uppercase tracking-wider">{context}</span>
                    <div className="flex overflow-x-auto snap-x snap-mandatory pb-2 -mx-2 px-2 hide-scrollbar w-full gap-4">
                      {quotes.map((quote, qIdx) => (
                        <div key={qIdx} className="relative min-w-[85%] sm:min-w-[70%] snap-center shrink-0 bg-white px-4 py-2.5 rounded-2xl rounded-tl-sm shadow-sm border border-black/5">
                          <svg viewBox="0 0 8 13" width="8" height="13" className="absolute top-0 -left-[7px] text-white">
                            <path opacity="0.1" d="M1.533,3.568L8,12.193V1H2.812 C1.042,1,0.474,2.156,1.533,3.568z"></path>
                            <path fill="currentColor" d="M1.533,2.568L8,11.193V0H2.812 C1.042,0,0.474,1.156,1.533,2.568z"></path>
                          </svg>
                          <p className="text-[13px] text-[#111b21] leading-relaxed break-words whitespace-pre-wrap max-h-[120px] overflow-y-auto hide-scrollbar">{quote.text}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-6 relative z-10">
                <MessageSquare className="w-6 h-6 text-zinc-300 mb-2" />
                <p className="text-xs text-zinc-400 font-medium">No notable quotes detected.</p>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
