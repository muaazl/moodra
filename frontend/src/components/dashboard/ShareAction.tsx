'use client';
import React, { useRef, useState } from 'react';
import { toPng } from 'html-to-image';
import { jsPDF } from 'jspdf';
import { Share2, Download, Check, Loader2, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ShareCard } from './ShareCard';
import { ScoringResponse } from '@/types/analysis';
import { useToast } from '@/components/ui/toast';
interface ShareActionProps {
  result: ScoringResponse;
}
export const ShareAction: React.FC<ShareActionProps> = ({ result }) => {
  const { toast } = useToast();
  const [isGenerating, setIsGenerating] = useState(false);
  const [isPdfGenerating, setIsPdfGenerating] = useState(false);
  const [isFinished, setIsFinished] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);
  const handleExport = async () => {
    if (!cardRef.current) return;
    setIsGenerating(true);
    try {
      await new Promise(r => setTimeout(r, 100));
      const dataUrl = await toPng(cardRef.current, {
        pixelRatio: 2,
        backgroundColor: '#050510',
        width: 540,
        height: 675,
      });
      const link = document.createElement('a');
      link.download = `moodra-vibe-${Date.now()}.png`;
      link.href = dataUrl;
      link.click();
      setIsFinished(true);
      toast('Share card exported!', 'success');
      setTimeout(() => setIsFinished(false), 3000);
    } catch (err) {
      toast('Failed to export card image', 'error');
    } finally {
      setIsGenerating(false);
    }
  };
  const handlePdfExport = async () => {
    setIsPdfGenerating(true);
    try {
      const resultsContainer = document.querySelector('[data-results-container]') as HTMLElement;
      if (!resultsContainer) {
        toast('Results container not found', 'error');
        return;
      }
      await new Promise(r => setTimeout(r, 200));
      const dataUrl = await toPng(resultsContainer, {
        pixelRatio: 2,
        backgroundColor: '#efeae2',
        style: {
          padding: '40px',
        },
      });
      const img = new Image();
      img.src = dataUrl;
      await new Promise<void>((resolve) => {
        img.onload = () => resolve();
      });
      const pdfWidth = img.width;
      const pdfHeight = img.height;
      const pdf = new jsPDF({
        orientation: pdfWidth > pdfHeight ? 'landscape' : 'portrait',
        unit: 'pt',
        format: [pdfWidth, pdfHeight],
      });
      pdf.addImage(dataUrl, 'PNG', 0, 0, pdfWidth, pdfHeight);
      pdf.save(`moodra-results-${Date.now()}.pdf`);
      setIsFinished(true);
      toast('PDF generated successfully!', 'success');
      setTimeout(() => setIsFinished(false), 3000);
    } catch (err) {
      toast('Failed to generate PDF', 'error');
    } finally {
      setIsPdfGenerating(false);
    }
  };
  const isAnyLoading = isGenerating || isPdfGenerating;
  return (
    <>
      <div className="flex items-center justify-end space-x-2 w-full sm:w-auto">
        <Button 
          variant="outline"
          disabled={isAnyLoading}
          onClick={handlePdfExport}
          className="border-black/10 text-zinc-700 bg-white hover:bg-zinc-50 shadow-sm font-semibold text-sm"
        >
          {isPdfGenerating ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <FileText className="w-4 h-4 mr-2" />
              Save PDF
            </>
          )}
        </Button>
        <Button 
          disabled={isAnyLoading}
          onClick={handleExport}
          className={`${
            isFinished 
            ? 'bg-[var(--color-wa-green)] hover:bg-[var(--color-wa-teal)]' 
            : 'bg-zinc-800 hover:bg-zinc-700'
          } text-white shadow-sm transition-all font-semibold text-sm min-w-[130px]`}
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
              Share Card
            </>
          )}
        </Button>
      </div>
      {}
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
