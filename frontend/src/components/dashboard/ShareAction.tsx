'use client';

import React, { useRef, useState } from 'react';
import { toPng } from 'html-to-image';
import { Share2, Download, Check, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ShareCard } from './ShareCard';
import { ScoringResponse } from '@/types/analysis';

interface ShareActionProps {
  result: ScoringResponse;
}

export const ShareAction: React.FC<ShareActionProps> = ({ result }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [isFinished, setIsFinished] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);

  const handleExport = async () => {
    if (!cardRef.current) return;
    
    setIsGenerating(true);
    try {
      // Small delay to ensure any layout/rendering is complete
      await new Promise(r => setTimeout(r, 100));
      
      const dataUrl = await toPng(cardRef.current, {
        pixelRatio: 2, // Double quality for crisp images
        backgroundColor: '#050510',
        width: 540,
        height: 675,
      });

      // Simple browser download trigger
      const link = document.createElement('a');
      link.download = `moodra-vibe-${Date.now()}.png`;
      link.href = dataUrl;
      link.click();
      
      setIsFinished(true);
      setTimeout(() => setIsFinished(false), 3000);
    } catch (err) {
      console.error('Failed to export card image:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <>
      <div className="flex items-center justify-end space-x-3 w-full sm:w-auto">
        <Button 
          variant="outline"
          onClick={() => window.print()}
          className="border-zinc-300 text-zinc-700 bg-white hover:bg-zinc-50 shadow-sm font-bold"
        >
          <Download className="w-4 h-4 mr-2" />
          Save PDF
        </Button>
        <Button 
          disabled={isGenerating}
          onClick={handleExport}
          className={`${
            isFinished 
            ? 'bg-[#25D366] hover:bg-[#128C7E]' 
            : 'bg-zinc-800 hover:bg-zinc-700'
          } text-white shadow-lg transition-all font-bold min-w-[140px]`}
        >
          {isGenerating ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Rendering...
            </>
          ) : isFinished ? (
            <>
              <Check className="w-4 h-4 mr-2" />
              Saved!
            </>
          ) : (
            <>
              <Share2 className="w-4 h-4 mr-2" />
              Share Vibe
            </>
          )}
        </Button>
      </div>

      {/* Offscreen Rendering Container */}
      <div 
        aria-hidden="true"
        className="fixed top-[-9999px] left-[-9999px]"
        style={{ pointerEvents: 'none' }}
      >
        <div ref={cardRef}>
          <ShareCard result={result} />
        </div>
      </div>
    </>
  );
};
