'use client';
import React from 'react';
import { ShieldCheck, Lock, EyeOff } from 'lucide-react';
import { motion } from 'framer-motion';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
export const PrivacyShield = () => {
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger>
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-zinc-500/10 border border-zinc-500/20 text-zinc-400 cursor-help"
          >
            <ShieldCheck className="w-4 h-4" />
            <span className="text-xs font-medium uppercase tracking-wider">Local Only</span>
            <div className="flex gap-1 ml-1">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-zinc-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-zinc-500"></span>
              </span>
            </div>
          </motion.div>
        </TooltipTrigger>
        <TooltipContent className="bg-zinc-900 border-zinc-800 text-zinc-300 p-4 max-w-xs transition-all duration-300">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-zinc-400 font-semibold">
              <Lock className="w-4 h-4" />
              <span>Privacy Verified</span>
            </div>
            <p className="text-xs leading-relaxed">
              Your chat data never leaves your machine. Analysis is performed in-memory on this local server. 
              No trackers. No cloud storage. No permanent records.
            </p>
            <div className="flex items-center gap-2 pt-1 border-t border-zinc-800">
              <EyeOff className="w-3 h-3 text-zinc-500" />
              <span className="text-[10px] text-zinc-500 italic">Self-destructing data mode active</span>
            </div>
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};
