'use client';

import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { TimelinePoint } from '@/types/analysis';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface TimelineChartProps {
  data: TimelinePoint[];
}

export const TimelineChart: React.FC<TimelineChartProps> = ({ data }) => {
  return (
    <Card className="w-full bg-black/40 backdrop-blur-xl border-zinc-500/10 mb-8 overflow-hidden">
      <CardHeader className="flex flex-row items-center justify-between pb-6">
        <div>
          <CardTitle className="text-xl font-bold text-zinc-100 flex items-center space-x-2">
            <span>Emotional Timeline</span>
            <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
          </CardTitle>
          <p className="text-sm text-zinc-300/60 mt-1">Sentiment and tension over the chat timeline</p>
        </div>
      </CardHeader>
      <CardContent className="p-0 sm:p-6">
        <div className="h-[350px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={data}
              margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
            >
              <defs>
                <linearGradient id="colorSentiment" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorTension" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#f43f5e" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff0a" vertical={false} />
              <XAxis
                dataKey="time"
                stroke="#6366f140"
                fontSize={12}
                tickFormatter={(val) => new Date(val).toLocaleDateString()}
              />
              <YAxis stroke="#6366f140" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0a0a0a',
                  borderColor: '#6366f120',
                  borderRadius: '12px',
                  color: '#e0e7ff',
                }}
                itemStyle={{ fontSize: '12px' }}
                cursor={{ stroke: '#6366f140', strokeWidth: 2 }}
              />
              <Legend verticalAlign="top" height={36} iconType="circle" />
              <Area
                type="monotone"
                dataKey="sentiment"
                name="Sentiment"
                stroke="#6366f1"
                fillOpacity={1}
                fill="url(#colorSentiment)"
                strokeWidth={3}
              />
              <Area
                type="monotone"
                dataKey="tension"
                name="Tension"
                stroke="#f43f5e"
                fillOpacity={1}
                fill="url(#colorTension)"
                strokeWidth={3}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
};
