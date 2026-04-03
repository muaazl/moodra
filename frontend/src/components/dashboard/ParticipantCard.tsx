'use client';

import React from 'react';
import { ParticipantScoring, ScoreMetadata } from '@/types/analysis';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { User, Zap, Droplets, Ghost, Flag, LucideIcon, MessageSquare, Quote } from 'lucide-react';

interface ParticipantCardProps {
  participant: ParticipantScoring;
}

const ScoreMetric: React.FC<{
  label: string;
  Icon: LucideIcon;
  data: ScoreMetadata;
  color: string;
  subLabel: string;
}> = ({ label, Icon, data, color, subLabel }) => {
  const percentage = data.value * 100;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className={`p-1.5 rounded-md ${color} bg-opacity-10`}>
            <Icon className={`w-4 h-4 ${color.replace('bg-', 'text-').replace('-500', '-600')}`} />
          </div>
          <div>
            <span className="text-xs font-bold text-zinc-800 uppercase tracking-wider">{subLabel}</span>
            <p className="text-[10px] text-zinc-500 -mt-1">{label}</p>
          </div>
        </div>
        <div className="text-right">
          <span className="text-sm font-black text-zinc-800 font-mono">{Math.round(percentage)}%</span>
          <p className={`text-[10px] font-bold ${color.replace('bg-', 'text-').replace('-500', '-600')}`}>{data.label}</p>
        </div>
      </div>
      <Progress value={percentage} className="h-1.5 bg-black/5" />
    </div>
  );
};

export const ParticipantCard: React.FC<ParticipantCardProps> = ({ participant }) => {
  return (
    <Card className="bg-white/80 backdrop-blur-xl border-black/5 overflow-hidden relative group hover:border-black/10 transition-all duration-300 shadow-sm">
      <div className="absolute top-0 right-0 p-4 opacity-[0.03] group-hover:opacity-5 transition-opacity pointer-events-none">
        <User size={120} strokeWidth={1} />
      </div>

      <CardHeader className="relative pb-0 pt-6">
        <div className="flex flex-col sm:flex-row sm:items-center space-y-4 sm:space-y-0 sm:space-x-4">
          <Avatar className="h-16 w-16 border-2 border-white shadow-sm ring-4 ring-[#25D366]/10">
            <AvatarFallback className="bg-[#128C7E] text-white text-xl font-bold">
              {participant.name.substring(0, 2).toUpperCase()}
            </AvatarFallback>
          </Avatar>
          <div className="space-y-1">
            <h3 className="text-2xl font-black text-zinc-900 tracking-tight">{participant.name}</h3>
            <div className="flex flex-wrap gap-1.5 mt-1">
              {participant.badges.map((badge, idx) => (
                <Badge
                  key={idx}
                  variant="secondary"
                  className="bg-[#25D366]/10 text-[#075E54] border-none text-[10px] px-2 py-0.5 font-bold"
                >
                  {badge}
                </Badge>
              ))}
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-6 space-y-6 relative">
        <div className="grid grid-cols-1 gap-5 bg-zinc-50/50 p-4 rounded-2xl border border-black/5">
          <ScoreMetric
            subLabel="Presence"
            label="Main Character Energy"
            Icon={Zap}
            data={participant.main_character_energy}
            color="bg-[#128C7E]"
          />
          <ScoreMetric
            subLabel="Manipulation"
            label="Gaslighting Index"
            Icon={Ghost}
            data={participant.gaslighting_index}
            color="bg-purple-500"
          />
          <ScoreMetric
            subLabel="Dryness"
            label="Desert Vibes"
            Icon={Droplets}
            data={participant.dry_texting}
            color="bg-amber-500"
          />
          <ScoreMetric
            subLabel="Hazard"
            label="Red Flag Score"
            Icon={Flag}
            data={participant.red_flag_score}
            color="bg-red-500"
          />
        </div>

        {/* The Receipts Section */}
        <div className="mt-8 space-y-4">
          <div className="flex items-center justify-between border-b border-black/5 pb-2">
            <div className="flex items-center space-x-2">
              <Quote className="w-4 h-4 text-[#128C7E]" />
              <h4 className="text-sm font-black text-zinc-900 uppercase tracking-widest">The Receipts</h4>
            </div>
          </div>
          
          <div className="space-y-4 bg-[#efeae2] p-4 sm:p-5 rounded-2xl border border-black/5 relative overflow-hidden">
             {/* Add very faint whatsapp background to the receipts area explicitly */}
             <div 
                className="absolute inset-0 pointer-events-none opacity-[0.04] z-[0]" 
                style={{ backgroundImage: 'url(/whatsapp_bg.png)', backgroundSize: '200px' }}
             />
             
            {participant.notable_quotes && participant.notable_quotes.length > 0 ? (
              participant.notable_quotes.map((quote, idx) => (
                <div key={idx} className="flex flex-col items-start w-full relative z-10">
                  <span className="text-[10px] font-bold text-zinc-500 mb-1 ml-1 uppercase tracking-wider">{quote.context}</span>
                  <div className="relative max-w-[95%] sm:max-w-[85%] bg-white px-4 py-2.5 rounded-2xl rounded-tl-sm shadow-sm border border-black/5">
                    {/* Tail of the text bubble */}
                    <svg viewBox="0 0 8 13" width="8" height="13" className="absolute top-0 -left-[7px] text-white">
                      <path opacity="0.1" d="M1.533,3.568L8,12.193V1H2.812 C1.042,1,0.474,2.156,1.533,3.568z"></path>
                      <path fill="currentColor" d="M1.533,2.568L8,11.193V0H2.812 C1.042,0,0.474,1.156,1.533,2.568z"></path>
                    </svg>
                    <p className="text-[13px] text-[#111b21] leading-relaxed break-words">{quote.text}</p>
                  </div>
                </div>
              ))
            ) : (
              <div className="flex flex-col items-center justify-center py-6 relative z-10">
                <MessageSquare className="w-8 h-8 text-zinc-300 mb-2" />
                <p className="text-sm text-zinc-500 font-medium">No notable quotes detected.</p>
              </div>
            )}
          </div>
        </div>

      </CardContent>
    </Card>
  );
};
