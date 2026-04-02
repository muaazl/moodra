'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { ParticipantScoring, ScoreMetadata } from '@/types/analysis';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress, ProgressTrack, ProgressIndicator } from '@/components/ui/progress';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { User, Zap, Droplets, Flame, Star, Ghost, Flag, LucideIcon } from 'lucide-react';

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
          <div className={`p-1.5 rounded-md ${color} bg-opacity-20`}>
            <Icon className={`w-4 h-4 ${color.replace('bg-', 'text-')}`} />
          </div>
          <div>
            <span className="text-xs font-bold text-zinc-100 uppercase tracking-wider">{subLabel}</span>
            <p className="text-[10px] text-zinc-400/60 -mt-1">{label}</p>
          </div>
        </div>
        <div className="text-right">
          <span className="text-sm font-black text-zinc-50 font-mono">{Math.round(percentage)}%</span>
          <p className={`text-[10px] font-bold ${color.replace('bg-', 'text-')}`}>{data.label}</p>
        </div>
      </div>
      <Progress value={percentage} className="h-1.5" />
    </div>
  );
};

export const ParticipantCard: React.FC<ParticipantCardProps> = ({ participant }) => {
  return (
    <Card className="bg-black/40 backdrop-blur-xl border-zinc-500/10 overflow-hidden relative group hover:border-zinc-500/30 transition-all duration-500">
      <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
        <User size={120} strokeWidth={1} />
      </div>

      <CardHeader className="relative pb-0">
        <div className="flex items-center space-x-4">
          <Avatar className="h-16 w-16 border-2 border-zinc-500/20 ring-4 ring-zinc-500/5 group-hover:ring-zinc-500/10 transition-all">
            <AvatarFallback className="bg-zinc-950 text-zinc-200 text-xl font-bold">
              {participant.name.substring(0, 2).toUpperCase()}
            </AvatarFallback>
          </Avatar>
          <div className="space-y-1">
            <h3 className="text-2xl font-black text-white tracking-tight">{participant.name}</h3>
            <div className="flex flex-wrap gap-1.5 mt-1">
              {participant.badges.map((badge, idx) => (
                <Badge
                  key={idx}
                  variant="secondary"
                  className="bg-zinc-500/10 text-zinc-300 border-none text-[10px] px-2 py-0.5"
                >
                  <Star className="w-2.5 h-2.5 mr-1 text-zinc-400" />
                  {badge}
                </Badge>
              ))}
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-6 space-y-6 relative">
        <div className="grid grid-cols-1 gap-5">
          <ScoreMetric
            subLabel="Presence"
            label="Main Character Energy"
            Icon={Zap}
            data={participant.main_character_energy}
            color="bg-zinc-500"
          />
          <ScoreMetric
            subLabel="Manipulation"
            label="Gaslighting Index"
            Icon={Ghost}
            data={participant.gaslighting_index}
            color="bg-zinc-500"
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

        <div className="p-4 rounded-xl bg-zinc-500/5 border border-zinc-500/10">
          <p className="text-xs text-zinc-200/80 leading-relaxed italic">
            &quot;{participant.main_character_energy.explanation}&quot;
          </p>
        </div>
      </CardContent>
    </Card>
  );
};
