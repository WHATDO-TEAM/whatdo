from airflow import DAG
from airflow.decorators import task
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.providers.mysql.hooks.mysql import MySqlHook
from datetime import datetime
import csv
import io

# GCS 버킷 및 파일 정보
GCS_BUCKET_NAME = "스토리지 이름"
GCS_FILE_PATH = "test_copied/final_data.csv"

# MariaDB Connection 정보
MYSQL_CONN_ID = "db 커넥션 ID"

# MariaDB 테이블 이름
TABLE_NAME = "테이블이름"

default_args = {
    "start_date": datetime(2024, 11, 1),
    "retries": 0,
}

with DAG(
    dag_id="test_load_csv_to_mariadb_dag",
    default_args=default_args,
    schedule=None,  # 수동 실행
    catchup=False,
) as dag:

    @task
    def load_csv_to_mariadb_dag():
        # GCS에서 파일 읽기
        gcs_hook = GCSHook(gcp_conn_id="google_cloud_default")
        file_content = gcs_hook.download(bucket_name=GCS_BUCKET_NAME, object_name=GCS_FILE_PATH)

        # 파일 내용을 메모리에서 읽기
        file_stream = io.StringIO(file_content.decode('utf-8'))
        csv_reader = csv.reader(file_stream)

        # 첫 번째 행(헤더) 건너뛰기
        next(csv_reader)

        # MariaDB 연결
        mysql_hook = MySqlHook(mysql_conn_id=MYSQL_CONN_ID)
        connection = mysql_hook.get_conn()
        cursor = connection.cursor()

        try:

            cursor.execute(f"DELETE FROM {TABLE_NAME}")

            # CSV 데이터를 MariaDB에 삽입
            for row in csv_reader:
                query = f"""
                INSERT INTO {TABLE_NAME} (customer_seq, room_building_seq, room_floor_seq, room_name, item_names)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, row)

            # 커밋 후 성공 메시지
            connection.commit()
            print("Data insertion complete.")

        except Exception as e:
            print(f"Error while inserting data into MariaDB: {e}")
            connection.rollback()  # 문제 발생 시 롤백

        finally:
            # 리소스 정리
            cursor.close()
            connection.close()

    load_csv_to_mariadb_dag()
