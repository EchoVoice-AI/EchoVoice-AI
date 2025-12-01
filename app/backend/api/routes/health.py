"""Health and config endpoints."""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from config import (
    CONFIG_AGENTIC_KNOWLEDGEBASE_ENABLED,
    CONFIG_DEFAULT_REASONING_EFFORT,
    CONFIG_DEFAULT_RETRIEVAL_REASONING_EFFORT,
    CONFIG_ECHOVOICE_SEARCH_IMAGE_EMBEDDINGS,
    CONFIG_ECHOVOICE_SEARCH_TEXT_TARGETS,
    CONFIG_ECHOVOICE_SEND_IMAGE_SOURCES,
    CONFIG_ECHOVOICE_SEND_TEXT_SOURCES,
    CONFIG_CHAT_HISTORY_BROWSER_ENABLED,
    CONFIG_CHAT_HISTORY_COSMOS_ENABLED,
    CONFIG_LANGUAGE_PICKER_ENABLED,
    CONFIG_MULTIMODAL_ENABLED,
    CONFIG_QUERY_REWRITING_ENABLED,
    CONFIG_REASONING_EFFORT_ENABLED,
    CONFIG_SEMANTIC_RANKER_DEPLOYED,
    CONFIG_SPEECH_INPUT_ENABLED,
    CONFIG_SPEECH_OUTPUT_AZURE_ENABLED,
    CONFIG_SPEECH_OUTPUT_BROWSER_ENABLED,
    CONFIG_STREAMING_ENABLED,
    CONFIG_USER_UPLOAD_ENABLED,
    CONFIG_VECTOR_SEARCH_ENABLED,
    CONFIG_WEB_SOURCE_ENABLED,
    CONFIG_SHAREPOINT_SOURCE_ENABLED,
    CONFIG_ECHOVOICE_SEARCH_IMAGE_EMBEDDINGS,
    CONFIG_ECHOVOICE_SEND_TEXT_SOURCES,
)

router = APIRouter()


@router.get("/health",tags=["Health"])
async def health():
    return JSONResponse({"status": "ok"})


@router.get("/config",tags=["Health"])
async def config(request: Request):
    cfg = getattr(request.app.state, "config", None)
    if cfg is None:
        raise HTTPException(status_code=503, detail="App not initialized")

    return JSONResponse({
        "showMultimodalOptions": cfg.get(CONFIG_MULTIMODAL_ENABLED),
        "showSemanticRankerOption": cfg.get(CONFIG_SEMANTIC_RANKER_DEPLOYED),
        "showQueryRewritingOption": cfg.get(CONFIG_QUERY_REWRITING_ENABLED),
        "showReasoningEffortOption": cfg.get(CONFIG_REASONING_EFFORT_ENABLED),
        "streamingEnabled": cfg.get(CONFIG_STREAMING_ENABLED),
        "defaultReasoningEffort": cfg.get(CONFIG_DEFAULT_REASONING_EFFORT),
        "defaultRetrievalReasoningEffort": cfg.get(CONFIG_DEFAULT_RETRIEVAL_REASONING_EFFORT),
        "showVectorOption": cfg.get(CONFIG_VECTOR_SEARCH_ENABLED),
        "showUserUpload": cfg.get(CONFIG_USER_UPLOAD_ENABLED),
        "showLanguagePicker": cfg.get(CONFIG_LANGUAGE_PICKER_ENABLED),
        "showSpeechInput": cfg.get(CONFIG_SPEECH_INPUT_ENABLED),
        "showSpeechOutputBrowser": cfg.get(CONFIG_SPEECH_OUTPUT_BROWSER_ENABLED),
        "showSpeechOutputAzure": cfg.get(CONFIG_SPEECH_OUTPUT_AZURE_ENABLED),
        "showChatHistoryBrowser": cfg.get(CONFIG_CHAT_HISTORY_BROWSER_ENABLED),
        "showChatHistoryCosmos": cfg.get(CONFIG_CHAT_HISTORY_COSMOS_ENABLED),
        "showAgenticRetrievalOption": cfg.get(CONFIG_AGENTIC_KNOWLEDGEBASE_ENABLED),
        "textTargetsSearchEnabled": cfg.get(CONFIG_ECHOVOICE_SEARCH_TEXT_TARGETS),
        "imageSearchEmbeddingsEnabled": cfg.get(CONFIG_ECHOVOICE_SEARCH_IMAGE_EMBEDDINGS),
        "textTargetsSendSources": cfg.get(CONFIG_ECHOVOICE_SEND_TEXT_SOURCES),
        "imageSendSources": cfg.get(CONFIG_ECHOVOICE_SEND_IMAGE_SOURCES),
        "ragSearchTextEmbeddings": cfg.get(CONFIG_ECHOVOICE_SEARCH_TEXT_TARGETS),
        "ragSearchImageEmbeddings": cfg.get(CONFIG_ECHOVOICE_SEARCH_IMAGE_EMBEDDINGS),
        "ragSendTextSources": cfg.get(CONFIG_ECHOVOICE_SEND_TEXT_SOURCES),
        "ragSendImageSources": cfg.get(CONFIG_ECHOVOICE_SEND_IMAGE_SOURCES),
        "webSourceEnabled": cfg.get(CONFIG_WEB_SOURCE_ENABLED),
        "sharepointSourceEnabled": cfg.get(CONFIG_SHAREPOINT_SOURCE_ENABLED),
    })
