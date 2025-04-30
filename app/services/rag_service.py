import json
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from app.core.config import settings


# 벡터스토어 설정
def get_vectorstore():
    pc = Pinecone(api_key=settings.PINECONE_API_KEY, environment=settings.PINECONE_ENV)
    index = pc.Index(settings.PINECONE_INDEX_NAME_REEMPLOYMENT)
    embeddings = OpenAIEmbeddings(
        openai_api_key=settings.OPENAI_API_KEY, model="text-embedding-ada-002"
    )
    return PineconeVectorStore(index=index, embedding=embeddings, namespace="default")


# LLM 설정
def get_llm(model="gpt-4o"):
    return ChatOpenAI(openai_api_key=settings.OPENAI_API_KEY, model=model)


# 업종 및 성별 추출
def extract_field_and_gender(question: str):
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "사용자의 질문에서 재취업 관련 업종(예: 정보통신업, 제조업 등)과 성별(남성 또는 여성)을 JSON으로 추출하세요. "
                '예시: {{"field": "제조업", "gender": "여성"}} '
                "명확하지 않으면 각각 '일반', '모름'으로 표시하세요.",
            ),
            ("human", "{input}"),
        ]
    )
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"input": question})
    print(f"[추출 결과]: {result}")

    try:
        parsed = json.loads(result)
        field = parsed.get("field", "일반").strip()
        gender = parsed.get("gender", "모름").strip()
        if gender not in ["남성", "여성"]:
            gender = "모름"
    except Exception:
        field, gender = "일반", "모름"

    return field, gender


# 쿼리 생성
def reformat_query(field: str, gender: str):
    return f"{field} 업종의 55세 이상 {gender} 근로자 수는 몇 명인가요?"


# 검색 및 요약
def search_and_summarize(field: str, gender: str, query: str):
    vectorstore = get_vectorstore()
    llm = get_llm()

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 10, "filter": {"field": field, "age_group": "55세 이상"}}
    )

    docs = retriever.invoke(query)
    print(f"🔍 Pinecone 검색 결과 수: {len(docs)}")
    for i, doc in enumerate(docs):
        print(f"  [{i+1}] {doc.page_content[:100]}... (metadata: {doc.metadata})")

    if not docs:
        print("fallback: 전체에서 검색 시도")
        retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
        docs = retriever.invoke(query)

    if not docs:
        return "관련 데이터를 찾을 수 없습니다."

    summary_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "아래 context는 55세 이상 고령자에 대한 통계입니다.\n"
                "다음 조건에 맞게 간결하게 정리해 주세요:\n\n"
                "- 회원님의 업종에는 고령자 근로자가 전체 근로자 중 몇 명인지 언급해 주세요.\n"
                "- 요청 성별이 '남성' 또는 '여성'일 경우, 해당 성별 고령자 수와 전체 대비 비율(%)을 계산해서 포함해 주세요.\n"
                "- 업종의 비전과 재취업 가능성은 GPT가 자유롭게 예측해 주세요.\n\n"
                "**형식 예시**:\n"
                "회원님이 종사하는 제조업 분야에는 고령자 근로자 11만 명(전체 118만 명 중)이 근무 중이며, 여성은 약 1.0%인 11,679명이 종사 중입니다. 해당 업종은 안정적인 기술 기반으로 재취업 기회가 보통 수준이며, 자동화로 인한 변화에 주의가 필요합니다.\n",
            ),
            ("human", "{input}"),
            ("system", "참고 문서:\n{context}"),
        ]
    )

    document_chain = create_stuff_documents_chain(
        llm=llm, prompt=summary_prompt, output_parser=StrOutputParser()
    )

    rag_chain = create_retrieval_chain(retriever, document_chain)
    result = rag_chain.invoke({"input": query})

    return result.get("answer") if isinstance(result, dict) else str(result)


# 최종 API
def get_final_reemployment_analysis(user_question: str):
    field, gender = extract_field_and_gender(user_question)
    query = reformat_query(field, gender)
    answer = search_and_summarize(field, gender, query)
    return {"answer": answer}
