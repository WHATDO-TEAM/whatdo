from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import mlflow
from typing import List, Dict
from elasticsearch import AsyncElasticsearch  # 비동기 Elasticsearch 클라이언트
from datetime import datetime

# Pydantic 모델
class RecommendationRequest(BaseModel):
    room_name: str
    visitor_cnt: int

class SelectionRequest(BaseModel):
    room_name: str
    visitor_cnt: int
    selected_menu: List[str]
    recommendations: List[str]

# 비동기 Elasticsearch 클라이언트
# class AsyncElasticsearchClient:
#     def __init__(self, host: str, port: int, scheme: str = "http"):
#         self.client = AsyncElasticsearch(
#             hosts=[{"host": host, "port": port, "scheme": scheme}]
#         )
#         self.index_name = "room_recommendations"

#     async def _create_index(self) -> None:
#         """인덱스 생성 및 매핑 설정"""
#         mapping = {
#             "mappings": {
#                 "properties": {
#                     "room_name": {"type": "keyword"},
#                     "visitor_cnt": {"type": "integer"},
#                     "selected_menu": {"type": "keyword"},
#                     "recommendations": {"type": "keyword"},
#                     "timestamp": {"type": "date"}
#                 }
#             }
#         }

#         if not await self.client.indices.exists(index=self.index_name):
#             await self.client.indices.create(index=self.index_name, body=mapping)

    # async def save_recommendation_data(self, data: SelectionRequest) -> Dict:
    #     """추천 데이터를 Elasticsearch에 저장"""
    #     document = {
    #         'room_name': data.room_name,
    #         'visitor_cnt': data.visitor_cnt,
    #         'selected_menu': data.selected_menu,
    #         'recommendations': data.recommendations,
    #         'timestamp': datetime.now()
    #     }
    #     return await self.client.index(index=self.index_name, document=document)

# FastAPI 애플리케이션
app = FastAPI()

# # Elasticsearch 클라이언트 초기화
# es_client = AsyncElasticsearchClient(
#     host="elasticsearch",  # Docker 내부 통신을 고려한 설정
#     port=9200,
#     scheme="http"
# )

# @app.on_event("startup")
# async def startup_event():
#     """Elasticsearch 인덱스 초기화"""
#     await es_client._create_index()

# MLflow 설정
mlflow.set_tracking_uri("http://10.178.0.26:5000")
RUN_ID = "0e55e1060ecd42e2b7bcdc71a05de389"
MODEL_URI = f"runs:/{RUN_ID}/item_based_model"

# 비동기 모델 로드
try:
    model = mlflow.pyfunc.load_model(MODEL_URI)
except Exception as e:
    raise HTTPException(status_code=500, detail=f"MLflow 모델 로드 실패: {str(e)}")

# @app.post("/save_selection")
# async def save_selection(data: SelectionRequest):
#     """선택된 메뉴와 추천 데이터를 Elasticsearch에 저장"""
#     try:
#         response = await es_client.save_recommendation_data(data)
#         return {"message": "선택이 성공적으로 저장되었습니다.", "response": response}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"선택 저장 중 오류 발생: {str(e)}")

@app.post("/get_recommendations")
async def get_recommendations(request: RecommendationRequest) -> Dict[str, List[str]]:
    """방 번호에 기반한 메뉴 추천"""
    try:
        model_input = {"room_name": int(request.room_name)}  # 입력 데이터를 정수로 변환
        # 비동기 호출로 가정 (MLflow가 I/O 작업을 포함하는 경우)
        recommendations = await model.predict(model_input)  # MLflow가 동기 호출이면 그대로 사용
        return {
            "recommendations": recommendations if isinstance(recommendations, list) else recommendations.tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"추천 생성 중 오류 발생: {str(e)}")

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
