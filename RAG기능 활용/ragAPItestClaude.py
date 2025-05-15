from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.docstore.document import Document
import os
import warnings

# 경고 무시 설정
warnings.filterwarnings('ignore', category=DeprecationWarning)

# OpenAI API 키 설정
os.environ["OPENAI_API_KEY"] = 'API Key'

def create_knowledge_base(documents):
    """
    문서를 받아서 벡터 데이터베이스를 생성합니다.
    """
    # 텍스트 분할기 설정
    text_splitter = CharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separator="\n"
    )
    
    # 문서를 청크로 분할
    texts = text_splitter.split_documents(documents)
    
    # 임베딩 생성 및 벡터 저장소 생성
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(texts, embeddings)
    
    return vectorstore

def create_rag_chain(vectorstore):
    """
    RAG 체인을 생성합니다.
    """
    # LLM 초기화
    llm = OpenAI(temperature=0)
    
    # RAG 체인 생성
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(),
        return_source_documents=True
    )
    
    return qa_chain

def query_rag(qa_chain, query):
    """
    질문에 대한 답변을 생성합니다.
    """
    result = qa_chain({"query": query})
    return {
        "answer": result["result"],
        "source_documents": result["source_documents"]
    }

# 사용 예시
if __name__ == "__main__":
    # 샘플 문서 데이터 (실제 사용시에는 파일이나 데이터베이스에서 로드)
    sample_docs = [
        Document(page_content="인공지능(AI)은 인간의 학습능력과 추론능력, 지각능력을 컴퓨터로 구현하는 기술입니다."),
        Document(page_content="머신러닝은 AI의 한 분야로, 데이터로부터 패턴을 학습하여 의사결정을 하는 기술입니다."),
        Document(page_content="딥러닝은 머신러닝의 한 종류로, 인공신경망을 기반으로 하는 학습 방법입니다.")
    ]
    
    # 벡터 데이터베이스 생성
    vectorstore = create_knowledge_base(sample_docs)
    
    # RAG 체인 생성
    qa_chain = create_rag_chain(vectorstore)
    
    # 질문하기
    #query =인공지능이  "무엇인지 설명해주세요."
    query = "인공지능과 딥러닝이 무엇인지 설명해주세요."
    result = query_rag(qa_chain, query)
    
    print("질문:", query)
    print("답변:", result["answer"])
    print("\n참고한 문서:")
    for doc in result["source_documents"]:
        print("-", doc.page_content)