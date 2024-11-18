from fastapi import FastAPI, HTTPException
import pandas as pd
import uvicorn
import json
import mlflow
from typing import List, Dict, Optional

app = FastAPI()

# MLflow 설정
mlflow.set_tracking_uri("http://10.178.0.26:5000")
RUN_ID = "0e55e1060ecd42e2b7bcdc71a05de389"
MODEL_URI = f"runs:/{RUN_ID}/item_based_model"

try:
    # MLflow 모델 로드
    model = mlflow.pyfunc.load_model(MODEL_URI)
except Exception as e:
    raise HTTPException(status_code=500, detail=f"MLflow 모델 로드 실패: {str(e)}")

# CSV 데이터 로드
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
    # 기존 데이터 필터링
    filtered_data = df[
        (df['room_name'].astype(str) == str(room_name)) &
        (df['visitor_cnt'] == int(visitor_cnt))
        ]

    if filtered_data.empty:
        return {"message": "조건에 맞는 데이터가 없습니다."}

    # 결과 데이터 준비
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
        # MLflow 모델을 사용한 추천
        model_input = {"room_name": int(room_name)}
        recommendations = model.predict(model_input)

        return {
            "recommendations": recommendations if isinstance(recommendations, list) else recommendations.tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"추천 생성 중 오류 발생: {str(e)}")


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)