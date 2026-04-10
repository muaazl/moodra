'use client';
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, ClipboardPaste, Sparkles, Wand2, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AnalysisProgress } from './AnalysisProgress';
interface ChatInputFormProps {
  onAnalyze: (text: string | null, file: File | null, anonymize: boolean) => void;
  isLoading: boolean;
  estimatedDuration: number;
}
export const ChatInputForm: React.FC<ChatInputFormProps> = ({ onAnalyze, isLoading, estimatedDuration }) => {
  const [pastedText, setPastedText] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [mode, setMode] = useState<'paste' | 'upload'>('paste');
  const handlePasteChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setPastedText(e.target.value);
  };
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };
  const isSubmitDisabled = isLoading || (mode === 'paste' ? !pastedText.trim() : !file);
  const getEstimatedTime = () => {
    if (mode === 'paste' && pastedText.trim()) {
      const est = Math.max(5, Math.ceil(pastedText.length / 5000) + 3);
      return est;
    }
    if (mode === 'upload' && file) {
      return Math.max(8, Math.ceil(file.size / 50000) + 5);
    }
    return null;
  };
  const estimatedTime = getEstimatedTime();
  const handleSubmit = async () => {
    if (isSubmitDisabled) return;
    if (mode === 'paste') {
      onAnalyze(pastedText, null, false);
    } else if (file) {
      onAnalyze(null, file, false);
    }
  };
  return (
    <Card className="w-full max-w-2xl mx-auto overflow-hidden border-black/5 bg-white/70 backdrop-blur-sm shadow-sm">
      <CardContent className="p-6 sm:p-8">
        <Tabs defaultValue="paste" onValueChange={(val) => setMode(val as 'paste' | 'upload')}>
          <TabsList className="grid w-full grid-cols-2 mb-6 bg-black/[0.03] rounded-xl h-11">
            <TabsTrigger value="paste" className="data-[state=active]:bg-white data-[state=active]:shadow-sm text-zinc-600 rounded-lg text-sm font-semibold">
              <ClipboardPaste className="w-4 h-4 mr-2" />
              Paste Chat
            </TabsTrigger>
            <TabsTrigger value="upload" className="data-[state=active]:bg-white data-[state=active]:shadow-sm text-zinc-600 rounded-lg text-sm font-semibold">
              <Upload className="w-4 h-4 mr-2" />
              Upload File
            </TabsTrigger>
          </TabsList>
          <AnimatePresence mode="wait" initial={false}>
            <motion.div
              key={mode}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.15 }}
            >
              {mode === 'paste' ? (
                <TabsContent value="paste">
                  <Textarea
                    placeholder="Paste your exported WhatsApp chat here..."
                    className="h-[200px] bg-[var(--color-wa-bg)]/50 border-black/5 focus-visible:ring-[var(--color-wa-green)]/30 text-zinc-800 placeholder:text-zinc-400 resize-none overflow-y-auto rounded-xl text-sm"
                    value={pastedText}
                    onChange={handlePasteChange}
                  />
                </TabsContent>
              ) : (
                <TabsContent value="upload">
                  <div className="flex flex-col items-center justify-center min-h-[200px] border-2 border-dashed border-black/8 rounded-xl bg-[var(--color-wa-bg)]/30 hover:bg-[var(--color-wa-bg)]/50 transition-colors cursor-pointer relative">
                    <input
                      type="file"
                      accept=".txt"
                      className="absolute inset-0 opacity-0 cursor-pointer"
                      onChange={handleFileChange}
                    />
                    <div className="text-center space-y-3">
                      <div className="p-3 rounded-full bg-black/[0.03] mx-auto w-fit">
                        <Upload className="w-7 h-7 text-zinc-400" />
                      </div>
                      <div className="space-y-1">
                        <p className="text-sm font-semibold text-zinc-700">
                          {file ? file.name : "Drop your WhatsApp .txt export"}
                        </p>
                        <p className="text-xs text-zinc-400">
                          WhatsApp → More → Export Chat → Without Media
                        </p>
                      </div>
                    </div>
                  </div>
                </TabsContent>
              )}
            </motion.div>
          </AnimatePresence>
        </Tabs>
        <div className="mt-6 space-y-4">
          {}
          {estimatedTime && !isLoading && (
            <div className="flex items-center justify-center space-x-2 text-zinc-400">
              <Clock className="w-3.5 h-3.5" />
              <span className="text-xs font-medium">Estimated time: ~{estimatedTime}s</span>
            </div>
          )}
          <Button
            type="button"
            onClick={handleSubmit}
            className="w-full h-12 text-base font-bold bg-[var(--color-wa-green)] hover:bg-[var(--color-wa-teal)] text-white shadow-none transition-all active:scale-[0.98] group relative overflow-hidden rounded-xl"
            disabled={isSubmitDisabled}
          >
             <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:animate-[shimmer_2s_infinite]" />
            {isLoading ? (
              <div className="flex items-center space-x-3">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                >
                  <Sparkles className="w-5 h-5" />
                </motion.div>
                <span>Analyzing...</span>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Wand2 className="w-5 h-5" />
                <span>Analyze Chat</span>
              </div>
            )}
          </Button>
          <AnalysisProgress isAnalyzing={isLoading} estimatedDuration={estimatedDuration} />
          {!isLoading && (
            <p className="text-center text-[10px] text-zinc-400 tracking-wide pt-1">
              Your data stays on your device. Nothing is stored.
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
