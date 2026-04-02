import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, Loader2 } from 'lucide-react';

interface AnalysisProgressProps {
  isAnalyzing: boolean;
  onComplete?: () => void; // Optional callback when all simulated phases finish
}

const PHASES = [
  { id: 1, label: "Analyzing sentiment & toxicity" },
  { id: 2, label: "Detecting tonality & topics" },
  { id: 3, label: "Scoring & aggregating results" },
];

// Time to wait per phase (in milliseconds)
const PHASE_DURATION_MS = 3000;

export const AnalysisProgress: React.FC<AnalysisProgressProps> = ({ isAnalyzing, onComplete }) => {
  const [currentPhase, setCurrentPhase] = useState<number>(0);

  useEffect(() => {
    if (!isAnalyzing) {
      setCurrentPhase(0);
      return;
    }

    // Start at phase 1 when analyzing begins
    setCurrentPhase(1);

    // Simulate progress through phases
    const timer1 = setTimeout(() => setCurrentPhase(2), PHASE_DURATION_MS);
    const timer2 = setTimeout(() => setCurrentPhase(3), PHASE_DURATION_MS * 2);
    const timer3 = setTimeout(() => {
      // Stay on phase 3 until isAnalyzing becomes false (when API actually returns)
      // but we could fire an optional callback here if needed.
      if (onComplete) onComplete();
    }, PHASE_DURATION_MS * 3);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
    };
  }, [isAnalyzing, onComplete]);

  if (!isAnalyzing) return null;

  return (
    <div className="w-full max-w-md mx-auto mt-6 space-y-4">
      <div className="flex justify-between items-center mb-2">
        <span className="text-xs font-bold text-zinc-400 uppercase tracking-wider">
          Processing
        </span>
        <span className="text-xs font-mono text-zinc-500">
          {Math.min(currentPhase, 3)}/3
        </span>
      </div>

      <div className="space-y-3">
        {PHASES.map((phase) => {
          const isActive = currentPhase === phase.id;
          const isPast = currentPhase > phase.id;
          const isPending = currentPhase < phase.id;

          return (
            <motion.div
              key={phase.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className={`flex items-center space-x-3 p-3 rounded-lg border transition-colors ${
                isActive 
                  ? "bg-zinc-800/50 border-zinc-500/30 text-white" 
                  : isPast 
                    ? "bg-zinc-900/30 border-zinc-800 text-zinc-400"
                    : "bg-transparent border-transparent text-zinc-600"
              }`}
            >
              <div className="flex-shrink-0 w-5 h-5 flex items-center justify-center">
                {isPast ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                ) : isActive ? (
                  <Loader2 className="w-4 h-4 text-indigo-400 animate-spin" />
                ) : (
                  <div className="w-1.5 h-1.5 rounded-full bg-zinc-700" />
                )}
              </div>
              <span className={`text-sm ${isActive ? "font-medium" : ""}`}>
                {phase.label}...
              </span>
            </motion.div>
          );
        })}
      </div>

      {/* Progress Bar Track */}
      <div className="h-1 w-full bg-zinc-900 rounded-full overflow-hidden mt-6">
        <motion.div
          className="h-full bg-indigo-500"
          initial={{ width: "0%" }}
          animate={{
            width: `${Math.min((currentPhase / 3) * 100, 95)}%`, // Don't go to 100% until API is fully done
          }}
          transition={{ duration: 0.5, ease: "easeInOut" }}
        />
      </div>
    </div>
  );
};
