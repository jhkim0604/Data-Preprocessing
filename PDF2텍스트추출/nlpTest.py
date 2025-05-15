from konlpy.tag import Mecab
#from konlpy.tag import Okt

#okt = Okt()
#print(okt.morphs("한글 형태소 분석기 Mecab 설치 완료"))

mecab = Mecab(dicpath=r"C:\mecab\mecab-ko-dic")
print(mecab.morphs("한글 형태소 분석기 Mecab 설치 완료"))

print(mecab.morphs("아름답고 행복한 가족으로 통합하는 방법에 대해 알려줘."))


# 첫 번째 문장 분석
sentence1 = "한글 형태소 분석기 Mecab 설치 완료"
result1 = mecab.pos(sentence1)
print("\n첫 번째 문장 형태소 분석 결과:")
for word, pos in result1:
    print(f"단어: {word}\t품사: {pos}")

# 두 번째 문장 분석
sentence2 = "아름답고 행복한 가족으로 통합된 방법에 대해 알려줘."
result2 = mecab.pos(sentence2)
print("\n두 번째 문장 형태소 분석 결과:")
for word, pos in result2:
    print(f"단어: {word}\t품사: {pos}")

# 세 번째 문장 분석
#sentence3 = "NIA(국토교통부)	클라우드 기반의 공간정보 데이터 통합 및 융복합 활용체계 구축(1차) 위탁감리(NIA)"
sentence3 = "국토부(NIA)	클라우드 기반의 공간정보 데이터 통합 및 융복합 활용체계 구축(1차) 위탁감리(NIA)"
result3 = mecab.pos(sentence3)
print("\n세 번째 문장 형태소 분석 결과:")
for word, pos in result3:
    print(f"단어: {word}\t품사: {pos}")