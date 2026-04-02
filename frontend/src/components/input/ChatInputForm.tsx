'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, ClipboardPaste, Sparkles, Wand2, ShieldCheck, History } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { AnalysisProgress } from './AnalysisProgress';

interface ChatInputFormProps {
  onAnalyze: (text: string | null, file: File | null, anonymize: boolean) => void;
  isLoading: boolean;
}

export const ChatInputForm: React.FC<ChatInputFormProps> = ({ onAnalyze, isLoading }) => {
  const [pastedText, setPastedText] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [anonymize, setAnonymize] = useState(false);
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

  const handleSubmit = async () => {
    if (isSubmitDisabled) return;

    if (mode === 'paste') {
      onAnalyze(pastedText, null, anonymize);
    } else if (file) {
      onAnalyze(null, file, anonymize);
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto overflow-hidden border-zinc-500/20 bg-black/40 backdrop-blur-xl">
      <CardContent className="p-6">
        <Tabs defaultValue="paste" onValueChange={(val) => setMode(val as 'paste' | 'upload')}>
          <TabsList className="grid w-full grid-cols-2 mb-6 bg-zinc-900/10">
            <TabsTrigger value="paste" className="data-[state=active]:bg-zinc-500/20">
              <ClipboardPaste className="w-4 h-4 mr-2" />
              Paste Transcript
            </TabsTrigger>
            <TabsTrigger value="upload" className="data-[state=active]:bg-zinc-500/20">
              <Upload className="w-4 h-4 mr-2" />
              Upload .txt
            </TabsTrigger>
          </TabsList>

          <AnimatePresence mode="wait">
            <TabsContent key="paste" value="paste">
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
              >
                <Textarea
                  placeholder="Paste your exported WhatsApp chat history here..."
                  className="h-[220px] bg-black/40 border-zinc-500/10 focus-visible:ring-zinc-500/30 text-zinc-50 resize-none overflow-y-auto"
                  value={pastedText}
                  onChange={handlePasteChange}
                />
              </motion.div>
            </TabsContent>

            <TabsContent key="upload" value="upload">
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
                className="flex flex-col items-center justify-center min-h-[220px] border-2 border-dashed border-zinc-500/20 rounded-lg bg-black/40 hover:bg-zinc-500/5 transition-colors cursor-pointer relative"
              >
                <input
                  type="file"
                  accept=".txt"
                  className="absolute inset-0 opacity-0 cursor-pointer"
                  onChange={handleFileChange}
                />
                <div className="text-center space-y-4">
                  <div className="p-4 rounded-full bg-zinc-500/10 mx-auto w-fit">
                    <Upload className="w-8 h-8 text-zinc-400" />
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-zinc-200">
                      {file ? file.name : "Drag and drop your WhatsApp .txt export"}
                    </p>
                    <p className="text-xs text-zinc-400/60 font-mono">
                      (WhatsApp &gt; More &gt; Export Chat &gt; Without Media)
                    </p>
                  </div>
                </div>
              </motion.div>
            </TabsContent>
          </AnimatePresence>
        </Tabs>

        <div className="mt-8 space-y-6">
          <div className="flex items-center justify-between p-4 rounded-xl bg-zinc-500/5 border border-zinc-500/10">
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded-lg bg-zinc-500/10">
                <ShieldCheck className="w-5 h-5 text-zinc-400" />
              </div>
              <div>
                <Label htmlFor="anonymize" className="text-sm font-semibold text-zinc-100">
                  Privacy Guard
                </Label>
                <p className="text-xs text-zinc-300/60">Anonymize all names before analysis</p>
              </div>
            </div>
            <Switch
              id="anonymize"
              checked={anonymize}
              onCheckedChange={setAnonymize}
              className="data-[state=checked]:bg-zinc-500"
            />
          </div>

          <Button
            type="button"
            onClick={handleSubmit}
            className="w-full h-14 text-lg font-bold bg-zinc-600 hover:bg-zinc-500 text-white shadow-none transition-all active:scale-[0.98] group relative overflow-hidden"
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
                <span>Analyzing Drama...</span>
              </div>
            ) : (
              <div className="flex items-center space-x-3">
                <Wand2 className="w-5 h-5" />
                <span>Expose Results</span>
              </div>
            )}
          </Button>

          <AnalysisProgress isAnalyzing={isLoading} />

          {!isLoading && (
            <p className="text-center text-[10px] text-zinc-300/40 uppercase tracking-widest font-mono pt-4">
              100% Client-Side Processing • No Backend Storage • Ephemeral Analysis
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
