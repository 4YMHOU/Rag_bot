from .start import router as start_router
from .add import router as add_router
from .get_all import router as get_all_router
from .search import router as search_router
from .generate import router as generate_router
from .rag import router as rag_router

routers = [
    start_router,
    add_router,
    get_all_router,
    search_router,
    generate_router,
    rag_router,
]