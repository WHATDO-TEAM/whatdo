
# Dowhat 기업연계 프로젝트

## 프로젝트 개요

본 프로젝트는 **Dowhat**과의 협업을 통해 데이터 기반 서비스 추천을 위한 데이터 엔지니어링 및 모델 서빙을 주제로 진행되었습니다.  
Dowhat의 빠른 성장에 따라 **AI 기반 추천 시스템** 구축 요구가 있었으며, 이를 바탕으로 데이터 파이프라인, 데이터베이스 설계, 모델링 및 서빙 시스템 구축을 목표로 프로젝트를 수행하였습니다.

---

## 아키텍처 개요

### 아키텍처 설계 고려사항
1. **머신러닝 도입 초기 상황**을 고려하여 설계.
2. 데이터 분석 전문가가 없는 상황에서도 쉽게 이해하고 활용할 수 있는 데이터 가공 및 적재 필요.
3. **운영적 효율성**: 신규 기술 도입 시 낮은 러닝 커브와 빠른 활용 가능성 강조.

### 아키텍처 구성
- 단일 처리 시스템: Spark 기반의 분산처리가 아닌 Pandas 기반의 단일 처리 시스템 선택.
  - 데이터량과 복잡도가 비교적 낮아 단일 처리로 충분히 처리 가능.
  - 고가용성 분산 시스템 구성 대비 유지보수 간소화.
- 관계형 데이터베이스(MariaDB)를 활용한 정규화 테이블 설계:
  - 데이터 분석 효율성 향상.
  - 데이터웨어하우스로의 마이그레이션을 염두에 둔 설계.

---

## 구현 세부사항

### 데이터 파이프라인
- **GCS**에 업로드된 CSV 파일을 시작점으로 설정.
- **Apache Airflow**를 통해 데이터 전처리 자동화:
  - 원본 데이터 백업 및 새로운 데이터 감지.
  - 데이터 전처리 후 MariaDB 적재.
  - 전처리 결과를 기반으로 피처스토어 구성.

### 데이터베이스 설계
- **MariaDB 채택 이유**:
  - 기본적인 고가용성 솔루션 지원 (MHA, Galera Cluster).
  - 기존 Dowhat의 MySQL 활용 경험 및 마이그레이션 용이성.
  - 보안성과 안정성 고려.
- **정규화된 스타 스키마 설계**:
  - 데이터 일관성 유지.
  - 향후 데이터웨어하우스 확장을 고려.

### 모델링 및 서빙
- **Latent Factor Collaborative Filtering**:
  - 데이터가 부족한 상황에 적합한 협업 필터링 모델 활용.
  - Optuna를 통한 하이퍼파라미터 최적화.
  - MLflow를 사용한 모델 등록 및 관리.
- **FastAPI**와 **MLflow**를 연계하여 실시간 추론 API 제공:
  - 사용자 추천 데이터를 ElasticSearch에 적재.
  - Grafana를 통한 실시간 만족도 시각화 및 Slack 알림 연동.

---

## 시스템 구성도

아키텍처 및 데이터 흐름은 다음과 같이 구성되었습니다:

1. **GCS 업로드**: 새로운 원본 데이터 업로드 감지.
2. **Airflow**:
   - 새로운 데이터 확인 및 백업.
   - 데이터 전처리 및 MariaDB 적재.
3. **MariaDB**:
   - 정규화된 테이블 스키마로 데이터 저장.
   - 모델 학습 및 평가를 위한 데이터 제공.
4. **MLflow**:
   - 모델 학습, 하이퍼파라미터 최적화 및 재학습.
   - 추천 모델 서빙 API 제공.
5. **ElasticSearch & Grafana**:
   - 고객 추천 선택/취소 데이터를 실시간 적재 및 시각화.
   - Slack 알림을 통해 고객 반응 추적.

---

## 주요 기술 스택

- **데이터 엔지니어링**: Python, Pandas, Apache Airflow
- **데이터베이스**: MariaDB (MHA, Galera Cluster 활용)
- **모델링 및 서빙**: Optuna, MLflow, FastAPI
- **실시간 분석 및 모니터링**: ElasticSearch, Grafana, Slack

---

## 결과 및 성과

- **추천 성능 향상**: 단순 추천 대비 Accuracy 14% 증가.
- **운영 효율성 개선**: MLflow를 통한 모델 서빙 및 종속성 문제 해결.
- **실시간 고객 반응 추적**: ElasticSearch와 Grafana 연계를 통해 고객 만족도 시각화.

---

## 추후 방향

1. 데이터 수집 및 피처 엔지니어링 강화.
2. 대규모 데이터 처리를 위한 데이터웨어하우스 구축 준비.
3. 딥러닝 기반 추천 시스템으로 확장 가능성 탐색.
4. 실시간 모델 재학습 및 성능 개선 자동화.

---

## 질문 및 피드백

질문 사항이나 피드백은 언제든지 환영합니다.  
감사합니다! 😊

---

