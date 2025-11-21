# uvicorn rag_api:app --reload

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# ----------------------------
# RAG functions
# ----------------------------

def load_pdf(file_path: str) -> str:
    from pypdf import PdfReader

    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def split_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50):
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.split_text(text)


def create_vector_store(chunks):
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_db = FAISS.from_texts(chunks, embeddings)
    return vector_db


def retrieve_chunks(vector_db, query: str, k: int = 3):
    return vector_db.similarity_search(query, k=k)


def build_llm():
    from transformers import pipeline
    from langchain_huggingface import HuggingFacePipeline

    gen_pipeline = pipeline(
        "text2text-generation",
        model="google/flan-t5-base",
        max_length=500,
    )
    return HuggingFacePipeline(pipeline=gen_pipeline)



def generate_answer(llm, context: str, query: str) -> str:
    prompt = (
        "You are a helpful assistant. "
        "Answer the question ONLY using the context below.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}\nAnswer:"
    )
    return llm.invoke(prompt)


# ----------------------------
# FastAPI app setup
# ----------------------------

app = FastAPI()

# Allow your React app (Vite/CRA) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev; later you can restrict to your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str


# ----------------------------
# Load RAG stuff ONCE at startup
# ----------------------------

PDF_PATH = r"C:/Users/RAJKIRAN REDDY/Desktop/final_projects/farm_finance/farm_finance_buddy/backend/AGRICULTURE.pdf"

print("[1] Loading PDF...")
text = load_pdf(PDF_PATH)

print("[2] Splitting into chunks...")
chunks = split_text(text)

print("[3] Creating vector store...")
vector_db = create_vector_store(chunks)

print("[4] Loading LLM (Flan-T5)...")
llm = build_llm()


# ----------------------------
# API route
# ----------------------------

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    query = req.question

    docs = retrieve_chunks(vector_db, query)
    context = "\n\n".join([d.page_content for d in docs])

    answer = generate_answer(llm, context, query)
    return ChatResponse(answer=answer)


# Run with:
# uvicorn rag_api:app --reload
