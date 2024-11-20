from fastapi import FastAPI, HTTPException
import pandas as pd
import uvicorn
import json
import mlflow
from typing import List, Dict, Optional
from elasticsearch import Elasticsearch
from datetime import datetime
from pydantic import BaseModel

app = FastAPI()

# MLflow 설정
mlflow.set_tracking_uri("http://10.178.0.26:5000")
RUN_ID = "0e55e1060ecd42e2b7bcdc71a05de389"
MODEL_URI = f"runs:/{RUN_ID}/item_based_model"

class SaveSelectionRequest(BaseModel):
    room_name: str
    visitor_cnt: int
    selected_items: List[str]
    event_type: str  # "추천 선택" 또는 "추천 취소"

# ElasticSearch 설정
es = Elasticsearch(
    hosts=[{
        'host': 'elasticsearch',
        'port': 9200,
        'scheme': 'http'
    }],
    verify_certs=False
)
INDEX_NAME = 'recommendations_log'

# ElasticSearch 인덱스 생성 (수정된 매핑)
def create_index():
    if not es.indices.exists(index=INDEX_NAME):
        mappings = {
            "mappings": {
                "properties": {
                    "room_name": {"type": "keyword"},
                    "visitor_cnt": {"type": "integer"},
                    "selected_items": {"type": "keyword"},
                    "event_type": {"type": "keyword"},  # 새로운 필드 추가
                    "timestamp": {"type": "date"}
                }
            }
        }
        es.indices.create(index=INDEX_NAME, body=mappings)
    else:
        print("ElasticSearch 인덱스가 이미 생성되어 있습니다.")

try:
    create_index()
except Exception as e:
    print(f"ElasticSearch 인덱스 생성 중 오류 발생: {e}")

# 기존 모델 로드 코드...
try:
    model = mlflow.pyfunc.load_model(MODEL_URI)
except Exception as e:
    raise HTTPException(status_code=500, detail=f"초기화 실패: {str(e)}")

# 기존 CSV 데이터 로드 코드...
try:
    df = pd.read_csv('./csv_take.csv', dtype={
        'room_name': str,
        'visitor_cnt': int,
        'contents': str
    })

    def parse_contents(content):
        try:
            data = json.loads(content)
            return [data] if isinstance(data, dict) else data
        except:
            return []

    df['contents'] = df['contents'].apply(parse_contents)
except FileNotFoundError:
    raise HTTPException(status_code=500, detail="CSV 파일을 찾을 수 없습니다.")
except Exception as e:
    raise HTTPException(status_code=500, detail=f"데이터 로드 오류: {str(e)}")

@app.get("/filter_data")
async def filter_data(room_name: str, visitor_cnt: int):
    # 기존 코드와 동일...
    filtered_data = df[
        (df['room_name'].astype(str) == str(room_name)) &
        (df['visitor_cnt'] == int(visitor_cnt))
    ]

    if filtered_data.empty:
        return {"message": "조건에 맞는 데이터가 없습니다."}

    result = []
    for _, row in filtered_data.iterrows():
        item_names = [item.get('itemName', '') for item in row['contents']]
        result.append({
            'room_name': str(row['room_name']),
            'visitor_cnt': int(row['visitor_cnt']),
            'item_names': item_names
        })

    return result

@app.get("/get_recommendations")
async def get_recommendations(room_name: str) -> Dict[str, List[str]]:
    try:
        model_input = {"room_name": int(room_name)}
        recommendations = model.predict(model_input)

        return {
            "recommendations": recommendations if isinstance(recommendations, list) else recommendations.tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"추천 생성 중 오류 발생: {str(e)}")

@app.post("/save_selection")
async def save_selection(request: SaveSelectionRequest):
    try:
        print(f"수신된 데이터: {request}")
        
        # ElasticSearch에 데이터 저장
        doc = {
            "room_name": request.room_name,
            "visitor_cnt": request.visitor_cnt,
            "selected_items": request.selected_items,
            "event_type": request.event_type,  # 이벤트 타입 저장
            "timestamp": datetime.utcnow()
        }

        # ElasticSearch 인덱스에 데이터 저장
        response = es.index(index=INDEX_NAME, document=doc)
        
        return {"message": "데이터가 성공적으로 저장되었습니다.", "response": response}
    
    except Exception as e:
        import traceback
        print(f"예외 발생: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"데이터 저장 중 오류 발생: {str(e)}")

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
