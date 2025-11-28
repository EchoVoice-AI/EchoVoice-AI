"""Startup and shutdown handlers to initialize app resources (ported from Quart setup)."""
import logging
import mimetypes
import os
import time
from typing import Awaitable, Callable

from azure.cosmos.aio import CosmosClient
from azure.identity.aio import (
    AzureDeveloperCliCredential,
    ManagedIdentityCredential,
    get_bearer_token_provider,
)
from azure.monitor.opentelemetry import configure_azure_monitor
from azure.search.documents.aio import SearchClient
from azure.search.documents.indexes.aio import SearchIndexClient
from azure.search.documents.knowledgebases.aio import KnowledgeBaseRetrievalClient
from fastapi import FastAPI
from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.openai import OpenAIInstrumentor

from approaches.approach import Approach
from approaches.chatreadretrieveread import ChatReadRetrieveReadApproach
from approaches.promptmanager import PromptyManager
from approaches.retrievethenread import RetrieveThenReadApproach
from config import (
    CONFIG_AGENTIC_KNOWLEDGEBASE_ENABLED,
    CONFIG_ASK_APPROACH,
    CONFIG_AUTH_CLIENT,
    CONFIG_CHAT_APPROACH,
    CONFIG_CHAT_HISTORY_BROWSER_ENABLED,
    CONFIG_CHAT_HISTORY_COSMOS_ENABLED,
    CONFIG_COSMOS_HISTORY_CLIENT,
    CONFIG_COSMOS_HISTORY_CONTAINER,
    CONFIG_COSMOS_HISTORY_VERSION,
    CONFIG_CREDENTIAL,
    CONFIG_DEFAULT_REASONING_EFFORT,
    CONFIG_DEFAULT_RETRIEVAL_REASONING_EFFORT,
    CONFIG_ECHOVOICE_SEARCH_IMAGE_EMBEDDINGS,
    CONFIG_ECHOVOICE_SEARCH_TEXT_TARGETS,
    CONFIG_ECHOVOICE_SEND_IMAGE_SOURCES,
    CONFIG_ECHOVOICE_SEND_TEXT_SOURCES,
    CONFIG_GLOBAL_BLOB_MANAGER,
    CONFIG_IMAGE_EMBEDDINGS_CLIENT,
    CONFIG_INGESTER,
    CONFIG_KNOWLEDGEBASE_CLIENT,
    CONFIG_LANGUAGE_PICKER_ENABLED,
    CONFIG_MULTIMODAL_ENABLED,
    CONFIG_OPENAI_CLIENT,
    CONFIG_QUERY_REWRITING_ENABLED,
    CONFIG_REASONING_EFFORT_ENABLED,
    CONFIG_SEARCH_CLIENT,
    CONFIG_SEMANTIC_RANKER_DEPLOYED,
    CONFIG_SHAREPOINT_SOURCE_ENABLED,
    CONFIG_SPEECH_INPUT_ENABLED,
    CONFIG_SPEECH_OUTPUT_AZURE_ENABLED,
    CONFIG_SPEECH_OUTPUT_BROWSER_ENABLED,
    CONFIG_STREAMING_ENABLED,
    CONFIG_USER_BLOB_MANAGER,
    CONFIG_USER_UPLOAD_ENABLED,
    CONFIG_VECTOR_SEARCH_ENABLED,
    CONFIG_WEB_SOURCE_ENABLED,
)
from services.prepdocs import (
    OpenAIHost,
    setup_embeddings_service,
    setup_file_processors,
    setup_image_embeddings_service,
    setup_openai_client,
    setup_search_info,
)
from prepdocslib.blobmanager import AdlsBlobManager, BlobManager
from prepdocslib.embeddings import ImageEmbeddings
from prepdocslib.filestrategy import UploadUserFileStrategy

# from .. import app as legacy_app_module  # keep reference if needed


def register(app: FastAPI) -> None:
    """Register startup and shutdown handlers on the FastAPI app."""

    @app.on_event("startup")
    async def _startup() -> None:
        await setup_clients(app)

    @app.on_event("shutdown")
    async def _shutdown() -> None:
        await close_clients(app)


async def setup_clients(app: FastAPI) -> None:
    """Port of the Quart `setup_clients()` into FastAPI app.state.

    This initializes Azure credentials, search clients, blob managers, OpenAI client, and
    config flags — mirroring the original Quart behavior and storing values in `app.state.config`.
    """
    # Fix Windows registry issue with mimetypes
    mimetypes.add_type("application/javascript", ".js")
    mimetypes.add_type("text/css", ".css")

    # Create a config mapping on app.state similar to current_app.config
    app.state.config = {}

    # Load environment values (these mirror values set in the original Quart setup)
    AZURE_STORAGE_ACCOUNT = os.environ.get("AZURE_STORAGE_ACCOUNT", "")
    AZURE_STORAGE_CONTAINER = os.environ.get("AZURE_STORAGE_CONTAINER", "")
    AZURE_IMAGESTORAGE_CONTAINER = os.environ.get("AZURE_IMAGESTORAGE_CONTAINER")
    AZURE_USERSTORAGE_ACCOUNT = os.environ.get("AZURE_USERSTORAGE_ACCOUNT")
    AZURE_USERSTORAGE_CONTAINER = os.environ.get("AZURE_USERSTORAGE_CONTAINER")
    AZURE_SEARCH_SERVICE = os.environ.get("AZURE_SEARCH_SERVICE", "")
    AZURE_SEARCH_ENDPOINT = f"https://{AZURE_SEARCH_SERVICE}.search.windows.net" if AZURE_SEARCH_SERVICE else ""
    AZURE_SEARCH_INDEX = os.environ.get("AZURE_SEARCH_INDEX", "")
    AZURE_SEARCH_KNOWLEDGEBASE_NAME = os.getenv("AZURE_SEARCH_KNOWLEDGEBASE_NAME", "")

    OPENAI_HOST = OpenAIHost(os.getenv("OPENAI_HOST", "azure"))
    OPENAI_CHATGPT_MODEL = os.environ.get("AZURE_OPENAI_CHATGPT_MODEL", "")
    AZURE_OPENAI_KNOWLEDGEBASE_MODEL = os.getenv("AZURE_OPENAI_KNOWLEDGEBASE_MODEL")
    AZURE_OPENAI_KNOWLEDGEBASE_DEPLOYMENT = os.getenv("AZURE_OPENAI_KNOWLEDGEBASE_DEPLOYMENT")
    OPENAI_EMB_MODEL = os.getenv("AZURE_OPENAI_EMB_MODEL_NAME", "text-embedding-ada-002")
    OPENAI_EMB_DIMENSIONS = int(os.getenv("AZURE_OPENAI_EMB_DIMENSIONS") or 1536)
    OPENAI_REASONING_EFFORT = os.getenv("AZURE_OPENAI_REASONING_EFFORT")

    AZURE_OPENAI_SERVICE = os.getenv("AZURE_OPENAI_SERVICE")
    AZURE_OPENAI_CHATGPT_DEPLOYMENT = (
        os.getenv("AZURE_OPENAI_CHATGPT_DEPLOYMENT") if OPENAI_HOST in [OpenAIHost.AZURE, OpenAIHost.AZURE_CUSTOM] else None
    )
    AZURE_OPENAI_EMB_DEPLOYMENT = (
        os.getenv("AZURE_OPENAI_EMB_DEPLOYMENT") if OPENAI_HOST in [OpenAIHost.AZURE, OpenAIHost.AZURE_CUSTOM] else None
    )
    AZURE_OPENAI_CUSTOM_URL = os.getenv("AZURE_OPENAI_CUSTOM_URL")
    AZURE_VISION_ENDPOINT = os.getenv("AZURE_VISION_ENDPOINT", "")
    AZURE_OPENAI_API_KEY_OVERRIDE = os.getenv("AZURE_OPENAI_API_KEY_OVERRIDE")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_ORGANIZATION = os.getenv("OPENAI_ORGANIZATION")

    AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
    AZURE_USE_AUTHENTICATION = os.getenv("AZURE_USE_AUTHENTICATION", "").lower() == "true"
    AZURE_ENFORCE_ACCESS_CONTROL = os.getenv("AZURE_ENFORCE_ACCESS_CONTROL", "").lower() == "true"
    AZURE_ENABLE_UNAUTHENTICATED_ACCESS = os.getenv("AZURE_ENABLE_UNAUTHENTICATED_ACCESS", "").lower() == "true"
    AZURE_SERVER_APP_ID = os.getenv("AZURE_SERVER_APP_ID")
    AZURE_SERVER_APP_SECRET = os.getenv("AZURE_SERVER_APP_SECRET")
    AZURE_CLIENT_APP_ID = os.getenv("AZURE_CLIENT_APP_ID")
    AZURE_AUTH_TENANT_ID = os.getenv("AZURE_AUTH_TENANT_ID", AZURE_TENANT_ID)

    KB_FIELDS_CONTENT = os.getenv("KB_FIELDS_CONTENT", "content")
    KB_FIELDS_SOURCEPAGE = os.getenv("KB_FIELDS_SOURCEPAGE", "sourcepage")

    AZURE_SEARCH_QUERY_LANGUAGE = os.getenv("AZURE_SEARCH_QUERY_LANGUAGE") or "en-us"
    AZURE_SEARCH_QUERY_SPELLER = os.getenv("AZURE_SEARCH_QUERY_SPELLER") or "lexicon"
    AZURE_SEARCH_SEMANTIC_RANKER = os.getenv("AZURE_SEARCH_SEMANTIC_RANKER", "free").lower()
    AZURE_SEARCH_QUERY_REWRITING = os.getenv("AZURE_SEARCH_QUERY_REWRITING", "false").lower()
    AZURE_SEARCH_FIELD_NAME_EMBEDDING = os.getenv("AZURE_SEARCH_FIELD_NAME_EMBEDDING", "embedding")

    AZURE_SPEECH_SERVICE_ID = os.getenv("AZURE_SPEECH_SERVICE_ID")
    AZURE_SPEECH_SERVICE_LOCATION = os.getenv("AZURE_SPEECH_SERVICE_LOCATION")
    AZURE_SPEECH_SERVICE_VOICE = os.getenv("AZURE_SPEECH_SERVICE_VOICE") or "en-US-AndrewMultilingualNeural"

    USE_MULTIMODAL = os.getenv("USE_MULTIMODAL", "").lower() == "true"
    ECHOVOICE_SEARCH_TEXT_TARGETS = os.getenv("ECHOVOICE_SEARCH_TEXT_TARGETS", "true").lower() == "true"
    ECHOVOICE_SEARCH_IMAGE_EMBEDDINGS = os.getenv("ECHOVOICE_SEARCH_IMAGE_EMBEDDINGS", "true").lower() == "true"
    ECHOVOICE_SEND_TEXT_SOURCES = os.getenv("ECHOVOICE_SEND_TEXT_SOURCES", "true").lower() == "true"
    ECHOVOICE_SEND_IMAGE_SOURCES = os.getenv("ECHOVOICE_SEND_IMAGE_SOURCES", "true").lower() == "true"
    USE_USER_UPLOAD = os.getenv("USE_USER_UPLOAD", "").lower() == "true"
    ENABLE_LANGUAGE_PICKER = os.getenv("ENABLE_LANGUAGE_PICKER", "").lower() == "true"
    USE_SPEECH_INPUT_BROWSER = os.getenv("USE_SPEECH_INPUT_BROWSER", "").lower() == "true"
    USE_SPEECH_OUTPUT_BROWSER = os.getenv("USE_SPEECH_OUTPUT_BROWSER", "").lower() == "true"
    USE_SPEECH_OUTPUT_AZURE = os.getenv("USE_SPEECH_OUTPUT_AZURE", "").lower() == "true"
    USE_CHAT_HISTORY_BROWSER = os.getenv("USE_CHAT_HISTORY_BROWSER", "").lower() == "true"
    USE_CHAT_HISTORY_COSMOS = os.getenv("USE_CHAT_HISTORY_COSMOS", "").lower() == "true"
    USE_AGENTIC_KNOWLEDGEBASE = os.getenv("USE_AGENTIC_KNOWLEDGEBASE", "").lower() == "true"
    USE_WEB_SOURCE = os.getenv("USE_WEB_SOURCE", "").lower() == "true"
    USE_SHAREPOINT_SOURCE = os.getenv("USE_SHAREPOINT_SOURCE", "").lower() == "true"
    AGENTIC_KNOWLEDGEBASE_REASONING_EFFORT = os.getenv("AGENTIC_KNOWLEDGEBASE_REASONING_EFFORT", "low")
    USE_VECTORS = os.getenv("USE_VECTORS", "").lower() != "false"

    RUNNING_ON_AZURE = os.getenv("WEBSITE_HOSTNAME") is not None or os.getenv("RUNNING_IN_PRODUCTION") is not None

    # Initialize Azure credential
    if RUNNING_ON_AZURE:
        logging.getLogger("uvicorn").info("Setting up Azure credential using ManagedIdentityCredential")
        if AZURE_CLIENT_ID := os.getenv("AZURE_CLIENT_ID"):
            azure_credential = ManagedIdentityCredential(client_id=AZURE_CLIENT_ID)
        else:
            azure_credential = ManagedIdentityCredential()
    elif AZURE_TENANT_ID:
        logging.getLogger("uvicorn").info("Setting up Azure credential using AzureDeveloperCliCredential with tenant_id %s", AZURE_TENANT_ID)
        azure_credential = AzureDeveloperCliCredential(tenant_id=AZURE_TENANT_ID, process_timeout=60)
    else:
        logging.getLogger("uvicorn").info("Setting up Azure credential using AzureDeveloperCliCredential for home tenant")
        azure_credential = AzureDeveloperCliCredential(process_timeout=60)

    azure_ai_token_provider: Callable[[], Awaitable[str]] = get_bearer_token_provider(
        azure_credential, "https://cognitiveservices.azure.com/.default"
    )

    # store credential
    app.state.config[CONFIG_CREDENTIAL] = azure_credential

    # Setup search clients
    search_client = None
    if AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_INDEX:
        search_client = SearchClient(endpoint=AZURE_SEARCH_ENDPOINT, index_name=AZURE_SEARCH_INDEX, credential=azure_credential)
    app.state.config[CONFIG_SEARCH_CLIENT] = search_client

    knowledgebase_client = None
    if AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KNOWLEDGEBASE_NAME:
        knowledgebase_client = KnowledgeBaseRetrievalClient(endpoint=AZURE_SEARCH_ENDPOINT, knowledge_base_name=AZURE_SEARCH_KNOWLEDGEBASE_NAME, credential=azure_credential)
    app.state.config[CONFIG_KNOWLEDGEBASE_CLIENT] = knowledgebase_client

    # Set up authentication helper
    search_index = None
    if AZURE_USE_AUTHENTICATION and AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_INDEX:
        search_index_client = SearchIndexClient(endpoint=AZURE_SEARCH_ENDPOINT, credential=azure_credential)
        try:
            search_index = await search_index_client.get_index(AZURE_SEARCH_INDEX)
        finally:
            await search_index_client.close()

    from core.authentication import AuthenticationHelper

    auth_helper = AuthenticationHelper(
        search_index=search_index,
        use_authentication=AZURE_USE_AUTHENTICATION,
        server_app_id=AZURE_SERVER_APP_ID,
        server_app_secret=AZURE_SERVER_APP_SECRET,
        client_app_id=AZURE_CLIENT_APP_ID,
        tenant_id=AZURE_AUTH_TENANT_ID,
        enforce_access_control=AZURE_ENFORCE_ACCESS_CONTROL,
        enable_unauthenticated_access=AZURE_ENABLE_UNAUTHENTICATED_ACCESS,
    )
    app.state.config[CONFIG_AUTH_CLIENT] = auth_helper

    # Global blob manager
    global_blob_manager = None
    if AZURE_STORAGE_ACCOUNT and AZURE_STORAGE_CONTAINER:
        global_blob_manager = BlobManager(
            endpoint=f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net",
            credential=azure_credential,
            container=AZURE_STORAGE_CONTAINER,
            image_container=AZURE_IMAGESTORAGE_CONTAINER,
        )
    app.state.config[CONFIG_GLOBAL_BLOB_MANAGER] = global_blob_manager

    # Setup OpenAI client wrapper
    # Initialize OpenAI client wrapper. In development environments some env vars
    # (e.g. AZURE_OPENAI_SERVICE) may be intentionally missing — don't fail startup
    # in that case. Log a warning and continue with a None client so the app can
    # still run for local development. Production deployments should ensure these
    # variables are set.
    try:
        openai_client, azure_openai_endpoint = setup_openai_client(
            openai_host=OPENAI_HOST,
            azure_credential=azure_credential,
            azure_openai_service=AZURE_OPENAI_SERVICE,
            azure_openai_custom_url=AZURE_OPENAI_CUSTOM_URL,
            azure_openai_api_key=AZURE_OPENAI_API_KEY_OVERRIDE,
            openai_api_key=OPENAI_API_KEY,
            openai_organization=OPENAI_ORGANIZATION,
            
        )
    except Exception as exc:  # broad catch so missing envs or misconfiguration don't crash startup
        logging.getLogger("uvicorn").warning(
            "OpenAI client initialization failed during startup: %s. Continuing without OpenAI client."
            " Set proper env vars for full functionality.",
            exc,
        )
        openai_client = None
        azure_openai_endpoint = None

    app.state.config[CONFIG_OPENAI_CLIENT] = openai_client

    # Optional user blob manager + ingester
    if USE_USER_UPLOAD:
        user_blob_manager = AdlsBlobManager(
            endpoint=f"https://{AZURE_USERSTORAGE_ACCOUNT}.dfs.core.windows.net",
            container=AZURE_USERSTORAGE_CONTAINER,
            credential=azure_credential,
        )
        app.state.config[CONFIG_USER_BLOB_MANAGER] = user_blob_manager

        file_processors, figure_processor = setup_file_processors(
            azure_credential=azure_credential,
            document_intelligence_service=os.getenv("AZURE_DOCUMENTINTELLIGENCE_SERVICE"),
            local_pdf_parser=os.getenv("USE_LOCAL_PDF_PARSER", "").lower() == "true",
            local_html_parser=os.getenv("USE_LOCAL_HTML_PARSER", "").lower() == "true",
            use_content_understanding=os.getenv("USE_CONTENT_UNDERSTANDING", "").lower() == "true",
            content_understanding_endpoint=os.getenv("AZURE_CONTENTUNDERSTANDING_ENDPOINT"),
            use_multimodal=USE_MULTIMODAL,
            openai_client=openai_client,
            openai_model=OPENAI_CHATGPT_MODEL,
            openai_deployment=AZURE_OPENAI_CHATGPT_DEPLOYMENT if OPENAI_HOST == OpenAIHost.AZURE else None,
        )

        search_info = setup_search_info(
            search_service=AZURE_SEARCH_SERVICE,
            index_name=AZURE_SEARCH_INDEX,
            azure_credential=azure_credential,
            use_agentic_knowledgebase=USE_AGENTIC_KNOWLEDGEBASE,
            azure_openai_endpoint=azure_openai_endpoint,
            knowledgebase_name=AZURE_SEARCH_KNOWLEDGEBASE_NAME,
            azure_openai_knowledgebase_deployment=AZURE_OPENAI_KNOWLEDGEBASE_DEPLOYMENT,
            azure_openai_knowledgebase_model=AZURE_OPENAI_KNOWLEDGEBASE_MODEL,
        )

        text_embeddings_service = None
        if USE_VECTORS:
            text_embeddings_service = setup_embeddings_service(
                open_ai_client=openai_client,
                openai_host=OPENAI_HOST,
                emb_model_name=OPENAI_EMB_MODEL,
                emb_model_dimensions=OPENAI_EMB_DIMENSIONS,
                azure_openai_deployment=AZURE_OPENAI_EMB_DEPLOYMENT,
                azure_openai_endpoint=azure_openai_endpoint,
            )

        image_embeddings_service = setup_image_embeddings_service(
            azure_credential=azure_credential, vision_endpoint=AZURE_VISION_ENDPOINT, use_multimodal=USE_MULTIMODAL
        )

        ingester = UploadUserFileStrategy(
            search_info=search_info,
            file_processors=file_processors,
            embeddings=text_embeddings_service,
            image_embeddings=image_embeddings_service,
            search_field_name_embedding=AZURE_SEARCH_FIELD_NAME_EMBEDDING,
            blob_manager=user_blob_manager,
            figure_processor=figure_processor,
        )
        app.state.config[CONFIG_INGESTER] = ingester

    # Image embeddings client
    if USE_MULTIMODAL:
        image_embeddings_client = ImageEmbeddings(AZURE_VISION_ENDPOINT, azure_ai_token_provider)
    else:
        image_embeddings_client = None
    app.state.config[CONFIG_IMAGE_EMBEDDINGS_CLIENT] = image_embeddings_client

    # Store feature flags and computed config values
    app.state.config[CONFIG_SEMANTIC_RANKER_DEPLOYED] = AZURE_SEARCH_SEMANTIC_RANKER != "disabled"
    app.state.config[CONFIG_QUERY_REWRITING_ENABLED] = (
        AZURE_SEARCH_QUERY_REWRITING == "true" and AZURE_SEARCH_SEMANTIC_RANKER != "disabled"
    )
    app.state.config[CONFIG_DEFAULT_REASONING_EFFORT] = OPENAI_REASONING_EFFORT
    app.state.config[CONFIG_DEFAULT_RETRIEVAL_REASONING_EFFORT] = AGENTIC_KNOWLEDGEBASE_REASONING_EFFORT
    app.state.config[CONFIG_REASONING_EFFORT_ENABLED] = OPENAI_CHATGPT_MODEL in Approach.GPT_REASONING_MODELS
    app.state.config[CONFIG_STREAMING_ENABLED] = (
        OPENAI_CHATGPT_MODEL not in Approach.GPT_REASONING_MODELS
        or Approach.GPT_REASONING_MODELS[OPENAI_CHATGPT_MODEL].streaming
    )
    app.state.config[CONFIG_VECTOR_SEARCH_ENABLED] = bool(USE_VECTORS)
    app.state.config[CONFIG_USER_UPLOAD_ENABLED] = bool(USE_USER_UPLOAD)
    app.state.config[CONFIG_LANGUAGE_PICKER_ENABLED] = ENABLE_LANGUAGE_PICKER
    app.state.config[CONFIG_SPEECH_INPUT_ENABLED] = USE_SPEECH_INPUT_BROWSER
    app.state.config[CONFIG_SPEECH_OUTPUT_BROWSER_ENABLED] = USE_SPEECH_OUTPUT_BROWSER
    app.state.config[CONFIG_SPEECH_OUTPUT_AZURE_ENABLED] = USE_SPEECH_OUTPUT_AZURE
    app.state.config[CONFIG_CHAT_HISTORY_BROWSER_ENABLED] = USE_CHAT_HISTORY_BROWSER
    app.state.config[CONFIG_CHAT_HISTORY_COSMOS_ENABLED] = USE_CHAT_HISTORY_COSMOS
    app.state.config[CONFIG_AGENTIC_KNOWLEDGEBASE_ENABLED] = USE_AGENTIC_KNOWLEDGEBASE
    app.state.config[CONFIG_MULTIMODAL_ENABLED] = USE_MULTIMODAL
    app.state.config[CONFIG_ECHOVOICE_SEARCH_TEXT_TARGETS] = ECHOVOICE_SEARCH_TEXT_TARGETS
    app.state.config[CONFIG_ECHOVOICE_SEARCH_IMAGE_EMBEDDINGS] = ECHOVOICE_SEARCH_IMAGE_EMBEDDINGS
    app.state.config[CONFIG_ECHOVOICE_SEND_TEXT_SOURCES] = ECHOVOICE_SEND_TEXT_SOURCES
    app.state.config[CONFIG_ECHOVOICE_SEND_IMAGE_SOURCES] = ECHOVOICE_SEND_IMAGE_SOURCES
    app.state.config[CONFIG_WEB_SOURCE_ENABLED] = USE_WEB_SOURCE
    app.state.config[CONFIG_SHAREPOINT_SOURCE_ENABLED] = USE_SHAREPOINT_SOURCE

    # Prompt manager
    app.state.config["PROMPT_MANAGER"] = PromptyManager()

    # Optional CosmosDB chat history setup
    if USE_CHAT_HISTORY_COSMOS:
        AZURE_COSMOSDB_ACCOUNT = os.getenv("AZURE_COSMOSDB_ACCOUNT")
        AZURE_CHAT_HISTORY_DATABASE = os.getenv("AZURE_CHAT_HISTORY_DATABASE")
        AZURE_CHAT_HISTORY_CONTAINER = os.getenv("AZURE_CHAT_HISTORY_CONTAINER")
        if not AZURE_COSMOSDB_ACCOUNT or not AZURE_CHAT_HISTORY_DATABASE or not AZURE_CHAT_HISTORY_CONTAINER:
            logging.getLogger("uvicorn").warning(
                "USE_CHAT_HISTORY_COSMOS is true but AZURE_COSMOSDB_ACCOUNT/AZURE_CHAT_HISTORY_DATABASE/AZURE_CHAT_HISTORY_CONTAINER not set; skipping Cosmos setup"
            )
        else:
            cosmos_client = CosmosClient(
                url=f"https://{AZURE_COSMOSDB_ACCOUNT}.documents.azure.com:443/", credential=azure_credential
            )
            cosmos_db = cosmos_client.get_database_client(AZURE_CHAT_HISTORY_DATABASE)
            cosmos_container = cosmos_db.get_container_client(AZURE_CHAT_HISTORY_CONTAINER)

            app.state.config[CONFIG_COSMOS_HISTORY_CLIENT] = cosmos_client
            app.state.config[CONFIG_COSMOS_HISTORY_CONTAINER] = cosmos_container
            app.state.config[CONFIG_COSMOS_HISTORY_VERSION] = os.getenv("AZURE_CHAT_HISTORY_VERSION")

    # Set up approaches similar to Quart app
    app.state.config[CONFIG_ASK_APPROACH] = RetrieveThenReadApproach(
        search_client=search_client,
        search_index_name=AZURE_SEARCH_INDEX,
        knowledgebase_model=AZURE_OPENAI_KNOWLEDGEBASE_MODEL,
        knowledgebase_deployment=AZURE_OPENAI_KNOWLEDGEBASE_DEPLOYMENT,
        knowledgebase_client=knowledgebase_client,
        knowledgebase_client_with_web=None,
        knowledgebase_client_with_sharepoint=None,
        knowledgebase_client_with_web_and_sharepoint=None,
        openai_client=openai_client,
        chatgpt_model=OPENAI_CHATGPT_MODEL,
        chatgpt_deployment=AZURE_OPENAI_CHATGPT_DEPLOYMENT,
        embedding_model=OPENAI_EMB_MODEL,
        embedding_deployment=AZURE_OPENAI_EMB_DEPLOYMENT,
        embedding_dimensions=OPENAI_EMB_DIMENSIONS,
        embedding_field=AZURE_SEARCH_FIELD_NAME_EMBEDDING,
        sourcepage_field=KB_FIELDS_SOURCEPAGE,
        content_field=KB_FIELDS_CONTENT,
        query_language=AZURE_SEARCH_QUERY_LANGUAGE,
        query_speller=AZURE_SEARCH_QUERY_SPELLER,
        prompt_manager=app.state.config["PROMPT_MANAGER"],
        reasoning_effort=OPENAI_REASONING_EFFORT,
        multimodal_enabled=USE_MULTIMODAL,
        image_embeddings_client=image_embeddings_client,
        global_blob_manager=global_blob_manager,
        user_blob_manager=app.state.config.get(CONFIG_USER_BLOB_MANAGER),
        use_web_source=app.state.config.get(CONFIG_WEB_SOURCE_ENABLED, False),
        use_sharepoint_source=app.state.config.get(CONFIG_SHAREPOINT_SOURCE_ENABLED, False),
        retrieval_reasoning_effort=AGENTIC_KNOWLEDGEBASE_REASONING_EFFORT,
    )

    app.state.config[CONFIG_CHAT_APPROACH] = ChatReadRetrieveReadApproach(
        search_client=search_client,
        search_index_name=AZURE_SEARCH_INDEX,
        knowledgebase_model=AZURE_OPENAI_KNOWLEDGEBASE_MODEL,
        knowledgebase_deployment=AZURE_OPENAI_KNOWLEDGEBASE_DEPLOYMENT,
        knowledgebase_client=knowledgebase_client,
        knowledgebase_client_with_web=None,
        knowledgebase_client_with_sharepoint=None,
        knowledgebase_client_with_web_and_sharepoint=None,
        openai_client=openai_client,
        chatgpt_model=OPENAI_CHATGPT_MODEL,
        chatgpt_deployment=AZURE_OPENAI_CHATGPT_DEPLOYMENT,
        embedding_model=OPENAI_EMB_MODEL,
        embedding_deployment=AZURE_OPENAI_EMB_DEPLOYMENT,
        embedding_dimensions=OPENAI_EMB_DIMENSIONS,
        embedding_field=AZURE_SEARCH_FIELD_NAME_EMBEDDING,
        sourcepage_field=KB_FIELDS_SOURCEPAGE,
        content_field=KB_FIELDS_CONTENT,
        query_language=AZURE_SEARCH_QUERY_LANGUAGE,
        query_speller=AZURE_SEARCH_QUERY_SPELLER,
        prompt_manager=app.state.config["PROMPT_MANAGER"],
        reasoning_effort=OPENAI_REASONING_EFFORT,
        multimodal_enabled=USE_MULTIMODAL,
        image_embeddings_client=image_embeddings_client,
        global_blob_manager=global_blob_manager,
        user_blob_manager=app.state.config.get(CONFIG_USER_BLOB_MANAGER),
        use_web_source=app.state.config.get(CONFIG_WEB_SOURCE_ENABLED, False),
        use_sharepoint_source=app.state.config.get(CONFIG_SHAREPOINT_SOURCE_ENABLED, False),
        retrieval_reasoning_effort=AGENTIC_KNOWLEDGEBASE_REASONING_EFFORT,
    )

    # Instrumentation and telemetry if Application Insights configured
    if os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
        logging.getLogger("uvicorn").info("APPLICATIONINSIGHTS_CONNECTION_STRING is set, enabling Azure Monitor")
        configure_azure_monitor(
            instrumentation_options={
                "django": {"enabled": False},
                "psycopg2": {"enabled": False},
                "fastapi": {"enabled": False},
            }
        )
        AioHttpClientInstrumentor().instrument()
        HTTPXClientInstrumentor().instrument()
        OpenAIInstrumentor().instrument()
        # Wrap app with OpenTelemetry middleware
        app.add_middleware(OpenTelemetryMiddleware)  # type: ignore[arg-type]


async def close_clients(app: FastAPI) -> None:
    """Close persistent clients on shutdown."""
    cfg = getattr(app.state, "config", {})
    try:
        if search_client := cfg.get(CONFIG_SEARCH_CLIENT):
            await search_client.close()
    except Exception:
        logging.exception("Exception while closing search client")

    try:
        if global_blob := cfg.get(CONFIG_GLOBAL_BLOB_MANAGER):
            await global_blob.close_clients()
    except Exception:
        logging.exception("Exception while closing global blob manager")

    try:
        if user_blob := cfg.get(CONFIG_USER_BLOB_MANAGER):
            await user_blob.close_clients()
    except Exception:
        logging.exception("Exception while closing user blob manager")

    try:
        if cred := cfg.get(CONFIG_CREDENTIAL):
            await cred.close()
    except Exception:
        logging.exception("Exception while closing credential")

    try:
        if cosmos_client := cfg.get(CONFIG_COSMOS_HISTORY_CLIENT):
            await cosmos_client.close()
    except Exception:
        logging.exception("Exception while closing cosmos client")
