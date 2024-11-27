from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.hooks.gcs import GCSHook
import pandas as pd
import io
from datetime import datetime

# GCS에서 파일 읽기 함수
def read_csv_from_gcs(bucket_name, file_name, **kwargs):
    # GCS 연결
    gcs_hook = GCSHook(gcp_conn_id="구글 클라우드 커넥션 ID")
    client = gcs_hook.get_conn()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    
    # 파일 내용 다운로드
    content = blob.download_as_bytes()
    
    # Pandas로 읽기
    df = pd.read_csv(io.BytesIO(content))
    print("CSV 파일 내용:")
    print(df)

# DAG 정의
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}

with DAG(
    dag_id="test_gcs_read_dag",
    default_args=default_args,
    description="GCS에서 테스트 파일 읽기",
    schedule=None,  # 수정된 부분: schedule_interval -> schedule
    start_date=datetime(2024, 11, 19),
    catchup=False,
) as dag:

    # Task 정의
    read_csv_task = PythonOperator(
        task_id="read_csv_from_gcs",
        python_callable=read_csv_from_gcs,
        op_kwargs={
            "bucket_name": "whatdo_bucket",
            "file_name": "test_copied/test_file.csv",
        },
    )

    read_csv_task

