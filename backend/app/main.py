"""FastAPI transport for the local demonstration."""

from __future__ import annotations

from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse

from .loader import PipelineError
from .models import AnalysisResponse, DeterministicPipelineError, DeterministicPipelineErrorResponse
from .service import AnalysisService

app = FastAPI(
    title="VeriClaim Local FHIR Anomaly Investigation Demo API",
    version="0.1.0",
    description=(
        "Local synthetic-data demonstration. Deterministic signals and optional evidence-referenced "
        "Gemini candidate explanations are non-authoritative investigation aids."
    ),
    servers=[{"url": "http://127.0.0.1:8000", "description": "Local development only"}],
)


async def get_analysis_service() -> AnalysisService:
    return AnalysisService()


@app.post(
    "/api/v1/analyze-demo",
    response_model=AnalysisResponse,
    responses={500: {"model": DeterministicPipelineErrorResponse}},
    summary="Analyze the fixed approved synthetic FHIR sample",
)
async def analyze_demo(service: AnalysisService = Depends(get_analysis_service)) -> AnalysisResponse | JSONResponse:
    try:
        return service.analyze()
    except PipelineError as error:
        public = DeterministicPipelineErrorResponse(
            error=DeterministicPipelineError(code=error.code, message=error.public_message, model_called=False)
        )
        return JSONResponse(status_code=500, content=public.model_dump(mode="json"))
