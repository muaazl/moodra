'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, MessageSquare, Shield, Zap, Share2, RefreshCcw, AlertTriangle, Flame } from 'lucide-react';
import { ChatInputForm } from '@/components/input/ChatInputForm';
import { TimelineChart } from '@/components/dashboard/TimelineChart';
import { ParticipantCard } from '@/components/dashboard/ParticipantCard';
import { ShareAction } from '@/components/dashboard/ShareAction';
import { AnalysisSuccessResponse, ScoringResponse } from '@/types/analysis';
import { analyzeText, analyzeFile } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { PrivacyShield } from '@/components/privacy/PrivacyShield';
import { PrivacyBanner } from '@/components/privacy/PrivacyBanner';

export default function Home() {
  const [result, setResult] = useState<ScoringResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);



  const handleAnalysis = async (text: string | null, file: File | null, anonymize: boolean) => {
    setIsLoading(true);
    setError(null);
    try {
      let response;
      if (text) {
        response = await analyzeText({ text, options: { anonymize } });
      } else if (file) {
        response = await analyzeFile(file);
      }
      if (response && response.data) {
        setResult(response.data);
      }
    } catch (err: any) {
      setError(err.message || 'Something went wrong during analysis');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setError(null);
  };

  return (
    <main className="min-h-screen bg-[#020205] text-zinc-50 selection:bg-zinc-500/30">
      {/* Background Glow */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] bg-zinc-600/20 blur-[120px] rounded-full" />
        <div className="absolute top-[20%] -right-[10%] w-[35%] h-[35%] bg-zinc-600/10 blur-[120px] rounded-full" />
      </div>

      <div className="relative z-10 container mx-auto px-4 py-12">
        {/* Header */}
        <header className="flex items-center justify-between mb-16">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-zinc-600 flex items-center justify-center shadow-[0_0_15px_rgba(79,70,229,0.5)]">
              <MessageSquare className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-black tracking-tighter">EXPOSE<span className="text-zinc-400">CHAT</span></span>
          </div>
          <div className="hidden sm:flex items-center space-x-6">
            <PrivacyShield />
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
                <Badge variant="outline" className="border-zinc-500/30 text-zinc-400 bg-zinc-500/5 px-4 py-1 rounded-full mb-4">
                  <Sparkles className="w-3 h-3 mr-2" />
                  AI-Powered Conversational Intelligence
                </Badge>
                <h1 className="text-5xl md:text-7xl font-black tracking-tight bg-gradient-to-b from-white to-zinc-300/40 bg-clip-text text-transparent leading-[1.1]">
                  What does your chat <br /> really say about you?
                </h1>
                <p className="text-lg text-zinc-200/50 max-w-2xl mx-auto font-medium">
                  Upload your WhatsApp export or paste a thread. Our local AI models expose the truth about sentiment, dominance, and hidden vibes—privately.
                </p>
              </div>

              {error && (
                <Card className="border-zinc-500/20 bg-zinc-500/5 mb-8">
                  <CardContent className="flex items-center space-x-3 p-4">
                    <AlertTriangle className="text-zinc-500 w-5 h-5 flex-shrink-0" />
                    <p className="text-sm text-zinc-200 font-medium">{error}</p>
                  </CardContent>
                </Card>
              )}

              <ChatInputForm
                isLoading={isLoading}
                onAnalyze={handleAnalysis}
              />

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-12">
                {[
                  { title: "Participant Stats", desc: "Who carries the chat?", icon: Zap },
                  { title: "Emotional Flow", desc: "Tension & Sentiment tracking", icon: MessageSquare },
                  { title: "Topic Analysis", desc: "What are you actually talking about?", icon: Shield },
                ].map((feature, i) => (
                  <div key={i} className="p-6 rounded-2xl bg-white/5 border border-white/5 space-y-3">
                    <feature.icon className="w-6 h-6 text-zinc-400" />
                    <h3 className="font-bold text-white">{feature.title}</h3>
                    <p className="text-sm text-zinc-300/40 leading-relaxed">{feature.desc}</p>
                  </div>
                ))}
              </div>

              <div className="pt-24 -mx-4">
                <PrivacyBanner />
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="result"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-8"
            >
              {/* Result Header */}
              <div className="flex flex-col md:flex-row md:items-start justify-between gap-6 pb-8 border-b border-zinc-500/10">
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <h2 className="text-3xl font-black text-white">The Analysis Result</h2>
                    <Badge className="bg-zinc-600 text-white border-none">{result.overall_mood}</Badge>
                  </div>
                  <p className="text-zinc-200/50 max-w-2xl font-medium">{result.overall_summary}</p>
                  
                  {result.roast_summary && (
                    <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl max-w-2xl relative overflow-hidden">
                       <div className="absolute top-0 right-0 p-2 opacity-10">
                         <Flame size={48} className="text-red-500" />
                       </div>
                       <p className="text-[10px] font-bold text-red-400 uppercase tracking-widest mb-1 relative z-10">The Brutal Truth</p>
                       <p className="text-sm font-medium text-red-100/90 relative z-10">{result.roast_summary}</p>
                    </div>
                  )}
                </div>
                <div className="flex items-center space-x-3 flex-shrink-0">
                  <Button variant="outline" className="border-zinc-500/20 bg-zinc-500/5 hover:bg-zinc-500/10 text-zinc-200" onClick={handleReset}>
                    <RefreshCcw className="w-4 h-4 mr-2" />
                    Reset
                  </Button>
                  <ShareAction result={result} />
                </div>
              </div>

              {/* Global Metrics */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-6 rounded-2xl bg-zinc-500/5 border border-zinc-500/10">
                  <p className="text-[10px] font-bold text-zinc-400 uppercase tracking-widest mb-1">Health</p>
                  <p className="text-3xl font-black text-white">{Math.round(result.global_metrics.conversation_health * 100)}%</p>
                </div>
                <div className="p-6 rounded-2xl bg-zinc-500/5 border border-zinc-500/10">
                  <p className="text-[10px] font-bold text-zinc-400 uppercase tracking-widest mb-1">Messages</p>
                  <p className="text-3xl font-black text-white">{result.global_metrics.total_messages}</p>
                </div>
              </div>

              {/* Timeline */}
              <TimelineChart data={result.timeline} />

              {/* Participants */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {result.participants.map((p, i) => (
                  <ParticipantCard key={i} participant={p} />
                ))}
              </div>

              {/* Standout Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {result.standout_cards.map((card, i) => (
                  <Card key={i} className="bg-white/5 border-white/5 hover:bg-white/10 transition-colors">
                    <CardContent className="p-6 space-y-4">
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                        card.type === 'award' ? 'bg-zinc-500/20 text-zinc-400' :
                        card.type === 'red_flag' ? 'bg-zinc-500/20 text-zinc-400' :
                        'bg-zinc-500/20 text-zinc-400'
                      }`}>
                        <Sparkles className="w-6 h-6" />
                      </div>
                      <div className="space-y-1">
                        <h4 className="font-bold text-white text-lg">{card.title}</h4>
                        <p className="text-sm text-zinc-200/50 leading-relaxed font-medium">
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
          <p className="text-[10px] font-bold text-zinc-300/20 uppercase tracking-[0.2em]">
            EXPOSE THE CHAT • {new Date().getFullYear()} • PRIVACY FIRST AI
          </p>
        </footer>
      </div>
    </main>
  );
}
