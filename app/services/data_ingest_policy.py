"""
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from app.core.config import settings
# test

# PDF → 문서 추출 → 청크 분할 → 임베딩 → Pinecone 업로드
def ingest_policy_pdf():
    pdf_path = settings.DATA_PATH_POLICY_PDF  # 예: "/mnt/data/고용정책병합.pdf"
    print(f"[INFO] Loading policy PDF from: {pdf_path}")

    # 1. PDF 로딩 및 텍스트 추출
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    print(f"[INFO] Loaded {len(documents)} raw pages")

    # 2. 문서 분할
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)
    print(f"[INFO] Split into {len(chunks)} chunks")

    # 3. Pinecone 초기화 및 인덱스 생성 확인
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    index_name = settings.PINECONE_INDEX_NAME_POLICY

    if index_name not in pc.list_indexes().names():
        print(f"[INFO] Creating index '{index_name}'...")
        pc.create_index(
            name=index_name,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        print(f"[SUCCESS] Index '{index_name}' created.")

    # 4. OpenAI 임베딩 모델
    embeddings = OpenAIEmbeddings(
        openai_api_key=settings.OPENAI_API_KEY, model="text-embedding-ada-002"
    )

    # 5. Pinecone VectorStore에 업로드
    print("[INFO] Uploading embedded chunks to Pinecone...")
    vectorstore = PineconeVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        index_name=index_name,
        namespace="policy-info",  # 동일 도메인 내 정책용 namespace
    )

    stats = pc.Index(index_name).describe_index_stats()
    print("[SUCCESS] 벡터 업로드 완료. 인덱스 상태:")
    print(stats)


if __name__ == "__main__":
    ingest_policy_pdf()
"""
