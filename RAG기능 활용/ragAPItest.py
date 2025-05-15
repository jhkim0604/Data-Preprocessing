## 1. 데이터베이스 설정 및 관리

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()

class Proposal(Base):
    __tablename__ = 'proposals'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

engine = create_engine('sqlite:///proposals.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def save_proposal(title, content, tags):
    proposal = Proposal(title=title, content=content, tags=tags)
    session.add(proposal)
    session.commit()

def search_proposals_by_keyword(keyword):
    return session.query(Proposal).filter(Proposal.tags.contains(keyword)).all()

## 2. PDF 텍스트 추출

import pdfplumber

def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

## 3. OpenAI API와 RAG 방식

import openai

openai.api_key = "your_openai_api_key"

def generate_proposal(prompt, context):
    messages = [
        {"role": "system", "content": "You are an expert in creating audit project proposals."},
        {"role": "user", "content": f"Context: {context}"},
        {"role": "user", "content": prompt}
    ]
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7,
        max_tokens=1000
    )
    return response['choices'][0]['message']['content']

## 4. 통합 프로그램

def main():
    # 1. 기존 제안서 데이터 저장
    print("Saving a sample proposal to the database...")
    save_proposal(
        title="Sample Audit Proposal",
        content="This is a sample proposal content for an audit project focusing on compliance.",
        tags="audit, compliance, sample"
    )
    print("Sample proposal saved.")

    # 2. RFP 업로드 및 텍스트 추출
    rfp_path = "sample_rfp.pdf"  # 사용자로부터 파일 경로 입력 받기
    print("Extracting text from RFP...")
    rfp_text = extract_text_from_pdf(rfp_path)
    print("RFP text extracted.")

    # 3. 유사 제안서 검색
    keyword = "compliance"  # 키워드 예시
    similar_proposals = search_proposals_by_keyword(keyword)
    context = "\n".join([proposal.content for proposal in similar_proposals])
    
    # 4. OpenAI API를 이용한 제안서 생성
    prompt = "Generate a proposal for a compliance audit project based on the given RFP."
    generated_proposal = generate_proposal(prompt, context)
    
    # 5. 생성된 제안서 저장 및 출력
    print("\nGenerated Proposal:\n")
    print(generated_proposal)

    save_proposal(
        title="Generated Proposal for Compliance Audit",
        content=generated_proposal,
        tags="generated, compliance, audit"
    )
    print("Generated proposal saved to database.")

if __name__ == "__main__":
    main()


