import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, Loader2 } from 'lucide-react';
interface AnalysisProgressProps {
  isAnalyzing: boolean;
  onComplete?: () => void;
  estimatedDuration?: number;
}
const PHASES = [
  { id: 1, label: "Analyzing sentiment and toxicity" },
  { id: 2, label: "Detecting tonality and topics" },
  { id: 3, label: "Scoring and aggregating results" },
];
export const AnalysisProgress: React.FC<AnalysisProgressProps> = ({ 
  isAnalyzing, 
  onComplete,
  estimatedDuration = 10 
}) => {
  const [currentPhase, setCurrentPhase] = useState<number>(0);
  const [timeLeft, setTimeLeft] = useState<number>(estimatedDuration);
  useEffect(() => {
    if (!isAnalyzing) {
      setCurrentPhase(0);
      return;
    }
    setCurrentPhase(1);
    setTimeLeft(estimatedDuration);
    const phaseDuration = (estimatedDuration * 1000) / 3;
    const timer1 = setTimeout(() => setCurrentPhase(2), phaseDuration);
    const timer2 = setTimeout(() => setCurrentPhase(3), phaseDuration * 2);
    const countdown = setInterval(() => {
      setTimeLeft((prev) => Math.max(0, prev - 1));
    }, 1000);
    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearInterval(countdown);
    };
  }, [isAnalyzing, estimatedDuration]);
  if (!isAnalyzing) return null;
  return (
    <div className="w-full max-w-md mx-auto mt-4 space-y-3">
      <div className="flex justify-between items-center">
        <span className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">
          Processing
        </span>
        <span className="text-xs font-medium text-zinc-500">
          {timeLeft > 0 ? `~${timeLeft}s remaining` : 'Finishing up...'}
        </span>
      </div>
      <div className="space-y-2">
        {PHASES.map((phase) => {
          const isActive = currentPhase === phase.id;
          const isPast = currentPhase > phase.id;
          return (
            <motion.div
              key={phase.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className={`flex items-center space-x-3 p-2.5 rounded-lg border transition-colors ${
                isActive 
                  ? "bg-[var(--color-wa-green)]/5 border-[var(--color-wa-green)]/15 text-zinc-800" 
                  : isPast 
                    ? "bg-white/50 border-black/5 text-zinc-400"
                    : "bg-transparent border-transparent text-zinc-300"
              }`}
            >
              <div className="flex-shrink-0 w-5 h-5 flex items-center justify-center">
                {isPast ? (
                  <CheckCircle2 className="w-4 h-4 text-[var(--color-wa-green)]" />
                ) : isActive ? (
                  <Loader2 className="w-4 h-4 text-[var(--color-wa-teal)] animate-spin" />
                ) : (
                  <div className="w-1.5 h-1.5 rounded-full bg-zinc-300" />
                )}
              </div>
              <span className={`text-sm ${isActive ? "font-medium" : ""}`}>
                {phase.label}
              </span>
            </motion.div>
          );
        })}
      </div>
      <div className="h-1 w-full bg-black/5 rounded-full overflow-hidden mt-3">
        <motion.div
          className="h-full bg-[var(--color-wa-green)] rounded-full"
          initial={{ width: "0%" }}
          animate={{
            width: `${Math.min((currentPhase / 3) * 100, 95)}%`,
          }}
          transition={{ duration: 0.5, ease: "easeInOut" }}
        />
      </div>
    </div>
  );
};
