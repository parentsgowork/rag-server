from datetime import datetime
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from app.core.config import settings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

# 오늘 날짜
current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"현재 날짜 및 시간: {current_date}")

# 벡터스토어 준비
def get_vectorstore():
    pc = Pinecone(api_key=settings.PINECONE_API_KEY, environment=settings.PINECONE_ENV)
    index = pc.Index(settings.PINECONE_INDEX_NAME_REEMPLOYMENT)
    embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
    return PineconeVectorStore(index=index, embedding=embeddings, text_key="text")

# LLM 준비
def get_llm(model="gpt-4o"):
    return ChatOpenAI(openai_api_key=settings.OPENAI_API_KEY, model=model)

# 1단계: 업종 + 성별 추출
def extract_field_and_gender(question: str):
    llm = get_llm()

    extraction_prompt = ChatPromptTemplate.from_messages([
        ("system", 
        "사용자의 질문에서 재취업 관련 업종(예: 정보통신업, 부동산업, 제조업 등)과 성별(남성 또는 여성)을 JSON 형태로 추출하세요. "
        "예시: {{\"field\": \"부동산업\", \"gender\": \"여성\"}}. "
        "업종이 명확하지 않으면 '일반', 성별이 명확하지 않으면 '모름'으로 표시하세요."
        ),
        ("human", "{input}")
    ])

    chain = extraction_prompt | llm | StrOutputParser()
    extraction_result = chain.invoke({"input": question})
    print(f"🎯 추출 결과: {extraction_result}")

    try:
        result_dict = eval(extraction_result)
        field = result_dict.get("field", "일반")
        gender = result_dict.get("gender", "모름")
    except:
        field = "일반"
        gender = "모름"

    return field.strip(), gender.strip()

# 2단계: 쿼리 최적화
def reformat_query(field: str, gender: str):
    return f"{field} 업종의 55세 이상 {gender} 근로자 수는 몇 명인가요?"

# 3단계: 벡터 검색 + 요약
def search_and_summarize(field: str, gender: str, optimized_query: str):
    llm = get_llm()
    vectorstore = get_vectorstore()

    # 🔥 벡터 + 필터 동시 검색
    retriever = vectorstore.as_retriever(search_kwargs={
        "k": 10,
        "filter": {
            "field": {"$contains": field},  # 필터는 여전히 걸어주되
            "age_group": "55세 이상"
        }
    })

    # 쿼리 자체를 임베딩 → 벡터 유사도 검색
    docs = retriever.invoke(optimized_query)  # ← 여기만 수정
    print(f"🔍 Pinecone 검색 결과 수: {len(docs)}")
    
    for idx, doc in enumerate(docs):
        print(f"  [{idx+1}] {doc.page_content[:100]}... (metadata: {doc.metadata})")

    if not docs:
        print("⚠️ 검색 결과 없음. fallback으로 전체에서 검색합니다.")
        fallback_retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
        docs = fallback_retriever.get_relevant_documents(optimized_query)

    if not docs:
        return "관련 데이터를 찾을 수 없습니다."

    # 요약 지시
    system_prompt = (
        f"오늘 날짜는 {current_date}입니다.\n"
        f"사용자가 입력한 성별은 {gender}입니다.\n\n"
        "context(문서)로부터 다음 정보를 수치 기반으로 요약하세요:\n"
        "- 업종명\n"
        "- 55세 이상 전체 근로자 수\n"
        "- 55세 이상 남성/여성 근로자 수\n"
        "- 전체 근로자 대비 해당 성별 비율(%)\n"
        "- 업종의 비전\n"
        "- 재취업 가능성\n"
        "- 조언 한 마디\n\n"
        "**답변은 반드시 3줄 이내로 작성하십시오.**\n"
        "데이터가 없으면 '알 수 없음'으로 표시하세요."
    )

    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
        ("system", "참고 문서:\n{context}")
    ])

    document_chain = create_stuff_documents_chain(
        llm=llm,
        prompt=qa_prompt,
        output_parser=StrOutputParser()
    )

    retriever_chain = create_retrieval_chain(lambda _: docs, document_chain)

    result = retriever_chain.invoke({"input": optimized_query})

    return result.get("answer") if isinstance(result, dict) else str(result)

# 최종 API
def get_final_reemployment_analysis(user_question: str):
    field, gender = extract_field_and_gender(user_question)
    optimized_query = reformat_query(field, gender)
    summary = search_and_summarize(field, gender, optimized_query)

    return {
        "answer": summary
    }
