'use client';
import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { TimelinePoint } from '@/types/analysis';
import { Card, CardContent } from '@/components/ui/card';
interface TimelineChartProps {
  data: TimelinePoint[];
}
const LINE_COLORS = [
  '#8B5A2B',
  '#556B2F',
  '#CD853F',
  '#8FBC8F',
  '#CD5C5C',
  '#B8860B',
  '#8B4513',
  '#6B8E23',
];
export const TimelineChart: React.FC<TimelineChartProps> = ({ data }) => {
  const [isMounted, setIsMounted] = React.useState(false);
  React.useEffect(() => {
    setIsMounted(true);
  }, []);
  if (!data || data.length === 0) return null;
  const participantNames = data[0]?.participant_volumes
    ? Object.keys(data[0].participant_volumes)
    : [];
  const hasParticipantData = participantNames.length > 0;
  const chartData = data.map((point, i) => {
    const entry: Record<string, any> = {
      name: point.time.startsWith('Segment') ? point.time.replace('Segment ', '#') : point.time,
    };
    if (hasParticipantData && point.participant_volumes) {
      for (const name of participantNames) {
        entry[name] = point.participant_volumes[name] || 0;
      }
    } else {
      entry['Messages'] = point.volume;
    }
    return entry;
  });
  const lineKeys = hasParticipantData ? participantNames : ['Messages'];
  return (
    <Card className="w-full bg-white/80 backdrop-blur-sm border-black/5 shadow-sm mb-8 overflow-hidden">
      <CardContent className="p-6">
        <div className="mb-1">
          <h3 className="text-lg font-bold text-zinc-800">Chat Activity</h3>
          <p className="text-sm text-zinc-500">
            Who was talking and when — from start to end
          </p>
        </div>
        <div className="h-[300px] w-full mt-4">
          {isMounted ? (
            <ResponsiveContainer width="100%" height="100%" minHeight={0}>
              <LineChart
                data={chartData}
                margin={{ top: 10, right: 20, left: -10, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#00000008" vertical={false} />
                <XAxis
                  dataKey="name"
                  stroke="#a1a1aa"
                  fontSize={11}
                  tickLine={false}
                  axisLine={{ stroke: '#e4e4e7' }}
                />
                <YAxis
                  stroke="#a1a1aa"
                  fontSize={11}
                  tickLine={false}
                  axisLine={false}
                  label={{ value: 'Messages', angle: -90, position: 'insideLeft', offset: 15, style: { fill: '#a1a1aa', fontSize: 11 } }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#fafaf9',
                    borderColor: '#e4e4e7',
                    borderRadius: '10px',
                    color: '#18181b',
                    fontSize: '12px',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
                  }}
                  itemStyle={{ fontSize: '12px', padding: '2px 0' }}
                  cursor={{ stroke: '#d4d4d8', strokeWidth: 1 }}
                />
                <Legend
                  verticalAlign="top"
                  height={36}
                  iconType="plainline"
                  wrapperStyle={{ fontSize: '12px', fontWeight: 600, color: '#3f3f46' }}
                />
                {lineKeys.map((key, idx) => (
                  <Line
                    key={key}
                    type="monotone"
                    dataKey={key}
                    name={key}
                    stroke={LINE_COLORS[idx % LINE_COLORS.length]}
                    strokeWidth={2.5}
                    dot={false}
                    activeDot={{ r: 4, strokeWidth: 0 }}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="w-full h-full flex items-center justify-center">
               <div className="w-8 h-8 border-2 border-[var(--color-wa-green)] border-t-transparent rounded-full animate-spin" />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
