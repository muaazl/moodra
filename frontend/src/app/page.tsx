'use client';
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, MessageSquare, Shield, Zap, RefreshCcw, AlertTriangle, Flame } from 'lucide-react';
import { ChatInputForm } from '@/components/input/ChatInputForm';
import { TimelineChart } from '@/components/dashboard/TimelineChart';
import { ParticipantCard } from '@/components/dashboard/ParticipantCard';
import { AnalysisSuccessResponse, ScoringResponse } from '@/types/analysis';
import { analyzeText, analyzeFile } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/components/ui/toast';
export default function Home() {
  const { toast } = useToast();
  const [result, setResult] = useState<ScoringResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [estimatedDuration, setEstimatedDuration] = useState(10);
  const playCompletionSound = () => {
    try {
      const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
      const oscillator = audioCtx.createOscillator();
      const gainNode = audioCtx.createGain();
      oscillator.type = 'sine';
      oscillator.frequency.setValueAtTime(880, audioCtx.currentTime); 
      oscillator.frequency.exponentialRampToValueAtTime(440, audioCtx.currentTime + 0.5); 
      gainNode.gain.setValueAtTime(0, audioCtx.currentTime);
      gainNode.gain.linearRampToValueAtTime(0.2, audioCtx.currentTime + 0.1);
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.8);
      oscillator.connect(gainNode);
      gainNode.connect(audioCtx.destination);
      oscillator.start();
      oscillator.stop(audioCtx.currentTime + 0.8);
    } catch (e) {  }
  };
  const handleAnalysis = async (text: string | null, file: File | null, anonymize: boolean) => {
    setIsLoading(true);
    setError(null);
    let est = 5;
    if (text) est = Math.max(5, Math.ceil(text.length / 5000) + 3);
    if (file) est = Math.max(8, Math.ceil(file.size / 50000) + 5);
    setEstimatedDuration(est);
    try {
      let response;
      if (text) {
        response = await analyzeText({ text, options: { anonymize } });
      } else if (file) {
        response = await analyzeFile(file);
      }
      if (response && response.data) {
        setResult(response.data);
        playCompletionSound();
      }
    } catch (err: any) {
      const msg = err.message || 'Something went wrong during analysis';
      setError(msg);
      toast(msg, 'error');
    } finally {
      setIsLoading(false);
    }
  };
  const handleReset = () => {
    setResult(null);
    setError(null);
  };
  return (
    <main className="min-h-screen bg-[var(--color-wa-bg)] text-zinc-900 selection:bg-[var(--color-wa-green)]/30 relative">
      {}
      <div 
        className="fixed inset-0 pointer-events-none opacity-[0.03] z-[0]" 
        style={{ backgroundImage: 'url(/whatsapp_bg.png)', backgroundSize: '400px' }}
      />
      <div className="relative z-10 container mx-auto px-4 py-12">
        {}
        <header className="flex items-center justify-between mb-16">
          <div className="flex items-center space-x-2">
            <img src="/favicon.svg" alt="Moodra" className="w-8 h-8 drop-shadow-sm" />
            <span className="text-xl font-black tracking-tighter text-zinc-800">Moodra</span>
          </div>
        </header>
        <AnimatePresence mode="wait">
          {!result ? (
            <motion.div
              key="input"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="max-w-4xl mx-auto space-y-12"
            >
              <div className="text-center space-y-4">
                <Badge variant="outline" className="border-[var(--color-wa-green)]/30 text-[var(--color-wa-dark)] bg-[var(--color-wa-green)]/10 px-4 py-1 rounded-full mb-4 font-bold">
                  <Sparkles className="w-3 h-3 mr-2 text-[var(--color-wa-green)]" />
                  AI-Powered Chat Analysis
                </Badge>
                <h1 className="text-5xl md:text-7xl font-black tracking-tight text-zinc-900 leading-[1.1]">
                  What does your chat <br /> <span className="text-[var(--color-wa-green)]">really say</span> about you?
                </h1>
                <p className="text-lg text-zinc-600 max-w-2xl mx-auto font-medium">
                  Drop your WhatsApp chat and find out who&apos;s the dry texter, who&apos;s the drama starter, and who&apos;s lowkey manipulative. 👀
                </p>
              </div>
              {error && (
                <Card className="border-red-200 bg-red-50/80 mb-8">
                  <CardContent className="flex items-center space-x-3 p-4">
                    <AlertTriangle className="text-red-500 w-5 h-5 flex-shrink-0" />
                    <p className="text-sm text-red-700 font-medium">{error}</p>
                  </CardContent>
                </Card>
              )}
              <ChatInputForm
                isLoading={isLoading}
                onAnalyze={handleAnalysis}
                estimatedDuration={estimatedDuration}
              />
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-12">
                {[
                  { title: "Participant Stats", desc: "Who carries the conversation and who ghosts.", icon: Zap },
                  { title: "Emotional Flow", desc: "Sentiment and tension tracking over time.", icon: MessageSquare },
                  { title: "Red Flag Detection", desc: "Spot the toxic patterns you might be missing.", icon: Shield },
                ].map((feature, i) => (
                  <div key={i} className="p-6 rounded-2xl bg-white/80 backdrop-blur-sm border border-black/5 shadow-sm space-y-3">
                    <feature.icon className="w-6 h-6 text-[var(--color-wa-green)]" />
                    <h3 className="font-bold text-zinc-800">{feature.title}</h3>
                    <p className="text-sm text-zinc-500 leading-relaxed font-medium">{feature.desc}</p>
                  </div>
                ))}
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="result"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              data-results-container
              className="space-y-8"
            >
              {}
              <div className="flex flex-col md:flex-row md:items-start justify-between gap-6 pb-8 border-b border-black/5">
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <h2 className="text-3xl font-black text-zinc-900">Analysis Results</h2>
                    <Badge className="bg-[var(--color-wa-teal)] text-white hover:bg-[var(--color-wa-dark)] border-none font-bold">{result.overall_mood}</Badge>
                  </div>
                  <p className="text-zinc-600 max-w-2xl font-medium text-lg leading-relaxed">{result.overall_summary}</p>
                  {result.roast_summary && (
                    <div className="p-4 bg-red-50 rounded-xl max-w-2xl relative overflow-hidden border border-red-200">
                       <div className="absolute top-0 right-0 p-2 opacity-10">
                         <Flame size={48} className="text-red-500" />
                       </div>
                       <p className="text-[10px] font-bold text-red-600 uppercase tracking-widest mb-1 relative z-10">The Brutal Truth</p>
                       <p className="text-sm font-medium text-red-800 relative z-10">{result.roast_summary}</p>
                    </div>
                  )}
                </div>
                <div className="flex items-center space-x-3 flex-shrink-0 no-print">
                  <Button variant="outline" className="border-black/10 bg-white/50 hover:bg-white text-zinc-700 shadow-sm" onClick={handleReset}>
                    <RefreshCcw className="w-4 h-4 mr-2" />
                    Reset
                  </Button>
                </div>
              </div>
              {}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-6 rounded-2xl bg-white border border-black/5 shadow-sm text-center md:text-left">
                  <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-1">Health</p>
                  <p className="text-3xl font-black text-[var(--color-wa-dark)]">{Math.round(result.global_metrics.conversation_health * 100)}%</p>
                </div>
                <div className="p-6 rounded-2xl bg-white border border-black/5 shadow-sm text-center md:text-left">
                  <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-1">Messages</p>
                  <p className="text-3xl font-black text-[var(--color-wa-teal)]">{result.global_metrics.total_messages}</p>
                </div>
              </div>
              {}
              <TimelineChart data={result.timeline} />
              {}
              <div className="flex overflow-x-auto pb-6 -mx-4 px-4 snap-x snap-mandatory scroll-smooth lg:grid lg:grid-cols-2 lg:gap-8 lg:overflow-visible lg:pb-0 lg:mx-0 lg:px-0 hide-scrollbar">
                {result.participants.map((p, i) => (
                  <div key={i} className="w-[85vw] sm:w-[60vw] lg:w-auto snap-center shrink-0 mr-4 lg:mr-0 last:mr-0">
                    <ParticipantCard participant={p} />
                  </div>
                ))}
              </div>
              {}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {result.standout_cards.map((card, i) => (
                  <Card key={i} className="bg-white/80 border-black/5 shadow-sm relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-[var(--color-wa-green)]/10 rounded-bl-[100px] -z-0"></div>
                    <CardContent className="p-6 space-y-4 relative z-10">
                      <div className={`w-12 h-12 rounded-full flex items-center justify-center shadow-sm ${
                        card.type === 'award' ? 'bg-yellow-100 text-yellow-600' :
                        card.type === 'red_flag' ? 'bg-red-100 text-red-600' :
                        'bg-blue-100 text-blue-600'
                      }`}>
                        <Sparkles className="w-5 h-5" />
                      </div>
                      <div className="space-y-1">
                        <h4 className="font-bold text-zinc-800 text-lg">{card.title}</h4>
                        <p className="text-sm text-zinc-600 leading-relaxed font-medium">
                          {card.description}
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        <footer className="mt-24 pt-8 border-t border-zinc-500/5 text-center">
          <p className="text-[10px] font-bold text-zinc-400 uppercase tracking-[0.2em]">
            Moodra &middot; {new Date().getFullYear()} &middot; Privacy First
          </p>
        </footer>
      </div>
    </main>
  );
}
