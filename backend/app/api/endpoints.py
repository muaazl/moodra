from fastapi import APIRouter, HTTPException, File, UploadFile, Body
from datetime import datetime
import time

from ..services.coordinator import AnalysisCoordinator
from ..schemas.api_responses import AnalysisRequest, AnalysisSuccessResponse, ErrorResponse
from ..services.scoring.schemas import ScoringResponse

router = APIRouter(prefix="/analyze", tags=["Analysis"])
coordinator = AnalysisCoordinator()

@router.post("/text", response_model=AnalysisSuccessResponse)
async def analyze_text(request: AnalysisRequest = Body(...)):
    """Analyze a pasted excerpt of WhatsApp chat text."""
    start_t = time.time()
    try:
        # Run the full pipeline
        scoring_result: ScoringResponse = await coordinator.run_full_analysis(request.text)
        
        # Calculate duration
        duration = round(time.time() - start_t, 2)
        
        return AnalysisSuccessResponse(
            data=scoring_result,
            metadata={
                "timestamp": datetime.utcnow().isoformat(),
                "processing_time": duration
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Analysis failed: {str(e)}"
        )

@router.post("/file", response_model=AnalysisSuccessResponse)
async def analyze_file(file: UploadFile = File(...)):
    """Analyze a WhatsApp export .txt file."""
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are supported currently.")
    
    start_t = time.time()
    try:
        # Read file bytes directly into memory (Privacy: No permanent storage)
        content = await file.read()
        
        # Analyze content
        scoring_result: ScoringResponse = await coordinator.analyze_file_content(content)
        
        # Calculate duration
        duration = round(time.time() - start_t, 2)
        
        return AnalysisSuccessResponse(
            data=scoring_result,
            metadata={
                "timestamp": datetime.utcnow().isoformat(),
                "processing_time": duration
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"File analysis failed: {str(e)}"
        )
    finally:
        # Ensure the file handle is closed
        await file.close()
