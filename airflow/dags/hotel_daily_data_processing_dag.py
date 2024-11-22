from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.providers.google.cloud.transfers.gcs_to_gcs import GCSToGCSOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook
from google.cloud import storage
from datetime import datetime, timedelta
import pandas as pd
import json
import re
import io

# 기본 설정
SOURCE_BUCKET = "회사 스토리지 이름"
TARGET_BUCKET = "백업 스토리지 이름"
ML_BUCKET = "ML 스토리지 이름"
SOURCE_PATH = "회사 스토리지 경로/csv_호텔명.csv"
PROCESSED_PATH = "/로컬경로/호텔명_processed_{ds_nodash}.csv"
MYSQL_CONN_ID = "DB 커넥션 이름"

# 키워드 리스트 및 매핑 딕셔너리
keywords = [ 
    "Chicken Karaage & Fried  Dishes (치킨 가라아게 & 모둠 튀김)", "Beef Truffle Zappaghetti(소고기 트러플 짜파게티)",
    "Mini Burger Set (미니버거 세트) 음료 선택 필수", "Bluemoon Draft Beer (블루문 생맥주)", "Miller Draft Beer (밀러 생맥주)",
    "Pig Hocks Set (순살 족발 세트)", "Beef Brisket Kimchi Pilaf(차돌 깍두기 볶음밥)", "Zero Coke (제로 콜라)",
    "Margherita Pizza(마르게리따 피자)", "Shine Musket Ade (샤인머스켓 에이드)", "Hamburg Steak (함박 스테이크)",
    "Truffle mushrooms Pizza(트러플 버섯 피자)", "Tteokbokki(떡볶이)", "Truffle Creamy Gnocchi Pasta(트러플 크림 뇨끼)",
    "Americano (아메리카노) 요청사항에 HOT/ICE 부탁드립니다.", "Lemon Ade (레몬 에이드)", "Coke (코카콜라)",
    "Seafood Oil Casareccia Pasta (씨푸드 오일 파스타)", "Prosciutto Rucola Pizza (프로슈토 루꼴라 피자)", 
    "Abalone Porridge + Side  Dishes (전복죽 + 반찬)", "Starlight Chungha (별빛 청하)", "LA Galbi Set (LA 갈비 세트)", 
    "Zero Sprite(제로 스프라이트)", "Grilled Camembert Cheese(까망베르 치즈 구이)", "Grapefruit Ade (자몽 에이드)",
    "Pancake Plate(팬케이크 플레이트)", "Sprite (스프라이트)", "Chicken Burger(치킨버거)", "Margherita Pizza(마르게리따타피자)",
    "Prosciutto Rucola Pizza(프로슈토 루꼴라 피자)", "Americano (아메리카노)", "Hwayo25 Soju (화요 25)", 
    "Mini Burger set", "Korea Traditional Pancakes (모둠 전)", "ILPUM Jinro Soju (일품 진로 소주)",
    "Abalone Porridge  (전복죽)", "Mini Burger Set (미니버거 세트)", "Creamy Pasta (크림 파스타)", 
    "Melon prosciutto(메론 프로슈토)", "Shine musket(샤인머스켓 에이드)", "Abalone Porridge + side (전복죽 + 반찬)",
    "Chicken Karaage & Fries Plate(치킨 가라아게 & 모둠튀김)", "Seafood Oil Casareccia Pasta(씨푸드 오일 까사레치아 파스타)", 
    "miller Draft beer  (밀러 맥주)", "Pig Hocks set(순살 족발세트)", "Beer (캘리)", "Coca cola(콜라)", 
    "Melon Prosciutto (메론 프로슈토)", "Seafood Oil Casareccia Pasta(씨푸트 오일 까사레치아 파스타)", 
    "LA Galbi set(LA 갈비 세트)", "bluemoon Draft beer  (블루문 맥주)", "Hamburg Steak(함박 스테이크)", 
    "Sprite(스프라이트)", "Soju (새로)", "Scones(스콘)", "Coca cola(코카콜라)", "Sprite(스프라이트, 제로 택 1)",
    "Korea Traditional Pancake(모둠전)", "ILpum Jinro Soju (일품 진로 소주)", "Zero cola (제로 콜라)", 
    "Chicken Karaage & Fried  Plate", "Seafood Oil Casareccia Pasta", "Starlight Chung Ha(달빛 청하)", 
    "아메리카노", "Hwayo25 soju(화요 25 소주)", "Grapefruit Ade(자몽 에이드)", "Draft beer(bluemoon, 생맥주)", 
    "Prosciutto Rucola Pizza", "LA Galbi set", "Pig Hocks set (순살 족발 세트)", "Draft beer(bluemoon,  miller 택 1)" 
    ]
keyword_dict = { 
    # Chicken and Fried Dishes
    "Chicken Karaage & Fried  Dishes (치킨 가라아게 & 모둠 튀김)": "Chicken Karaage & Fried Dishes",
    "Chicken Karaage & Fries Plate(치킨 가라아게 & 모둠튀김)": "Chicken Karaage & Fried Dishes",
    "Chicken Karaage & Fried  Plate": "Chicken Karaage & Fried Dishes",

    # Beef and Other Main Dishes
    "Beef Truffle Zappaghetti(소고기 트러플 짜파게티)": "Beef Truffle Zappaghetti",
    "Beef Brisket Kimchi Pilaf(차돌 깍두기 볶음밥)": "Beef Brisket Kimchi Pilaf",
    "LA Galbi Set (LA 갈비 세트)": "LA Galbi Set",
    "LA Galbi set(LA 갈비 세트)": "LA Galbi Set",
    "LA Galbi set": "LA Galbi Set",
    
    # Pig Hocks
    "Pig Hocks Set (순살 족발 세트)": "Pig Hocks Set",
    "Pig Hocks set(순살 족발세트)": "Pig Hocks Set",
    "Pig Hocks set (순살 족발 세트)": "Pig Hocks Set",
    
    # Burger
    "Mini Burger Set (미니버거 세트) 음료 선택 필수": "Mini Burger Set",
    "Mini Burger set": "Mini Burger Set",
    "Mini Burger Set (미니버거 세트)": "Mini Burger Set",
    "Chicken Burger(치킨버거)": "Chicken Burger",
    
    # Pizza
    "Margherita Pizza(마르게리따 피자)": "Margherita Pizza",
    "Margherita Pizza(마르게리따타피자)": "Margherita Pizza",
    "Prosciutto Rucola Pizza (프로슈토 루꼴라 피자)": "Prosciutto Rucola Pizza",
    "Prosciutto Rucola Pizza(프로슈토 루꼴라 피자)": "Prosciutto Rucola Pizza",
    "Prosciutto Rucola Pizza": "Prosciutto Rucola Pizza",
    "Truffle mushrooms Pizza(트러플 버섯 피자)": "Truffle Mushrooms Pizza",

    # Pasta and Gnocchi
    "Seafood Oil Casareccia Pasta (씨푸드 오일 파스타)": "Seafood Oil Casareccia Pasta",
    "Seafood Oil Casareccia Pasta(씨푸드 오일 까사레치아 파스타)": "Seafood Oil Casareccia Pasta",
    "Seafood Oil Casareccia Pasta(씨푸트 오일 까사레치아 파스타)": "Seafood Oil Casareccia Pasta",
    "Seafood Oil Casareccia Pasta": "Seafood Oil Casareccia Pasta",
    "Truffle Creamy Gnocchi Pasta(트러플 크림 뇨끼)": "Creamy Pasta",
    "Creamy Pasta (크림 파스타)": "Creamy Pasta",

    # Porridge
    "Abalone Porridge + Side  Dishes (전복죽 + 반찬)": "Abalone Porridge",
    "Abalone Porridge + side (전복죽 + 반찬)": "Abalone Porridge",
    "Abalone Porridge  (전복죽)": "Abalone Porridge",

    # Pancakes
    "Pancake Plate(팬케이크 플레이트)": "Korean Traditional Pancakes",
    "Korea Traditional Pancakes (모둠 전)": "Korean Traditional Pancakes",
    "Korea Traditional Pancake(모둠전)": "Korean Traditional Pancakes",

    # Others
    "Melon prosciutto(메론 프로슈토)": "Melon Prosciutto",
    "Melon Prosciutto (메론 프로슈토)": "Melon Prosciutto",
    "Hamburg Steak (함박 스테이크)": "Hamburg Steak",
    "Hamburg Steak(함박 스테이크)": "Hamburg Steak",
    "Tteokbokki(떡볶이)": "Tteokbokki",
    "Grilled Camembert Cheese(까망베르 치즈 구이)": "Grilled Camembert Cheese",
    "Scones(스콘)": "Scones",

    # Soju
    "Hwayo25 Soju (화요 25)": "Soju",
    "Hwayo25 soju(화요 25 소주)": "Soju",
    "ILPUM Jinro Soju (일품 진로 소주)": "Soju",
    "ILpum Jinro Soju (일품 진로 소주)": "Soju",
    "Soju (새로)": "Soju",
    "Starlight Chungha (별빛 청하)": "Soju",
    "Starlight Chung Ha(달빛 청하)": "Soju",

    # Beer
    "Bluemoon Draft Beer (블루문 생맥주)": "Beer",
    "Draft beer(bluemoon, 생맥주)": "Beer",
    "Draft beer(bluemoon,  miller 택 1)": "Beer",
    "bluemoon Draft beer  (블루문 맥주)": "Beer",
    "Miller Draft Beer (밀러 생맥주)": "Beer",
    "miller Draft beer  (밀러 맥주)": "Beer",
    "Beer (캘리)": "Beer",
    "Kelly Beer": "Beer",

    # 탄산음료
    "Coke (코카콜라)": "탄산음료",
    "Coca cola(콜라)": "탄산음료",
    "Coca cola(코카콜라)": "탄산음료",
    "Zero Coke (제로 콜라)": "탄산음료",
    "Zero cola (제로 콜라)": "탄산음료",
    "Sprite (스프라이트)": "탄산음료",
    "Sprite(스프라이트)": "탄산음료",
    "Sprite(스프라이트, 제로 택 1)": "탄산음료",
    "Zero Sprite(제로 스프라이트)": "탄산음료",

    # 에이드류
    "Lemon Ade (레몬 에이드)": "에이드",
    "Grapefruit Ade (자몽 에이드)": "에이드",
    "Grapefruit Ade(자몽 에이드)": "에이드",
    "Shine Musket Ade (샤인머스켓 에이드)": "에이드",
    "Shine musket(샤인머스켓 에이드)": "에이드",

    # Coffee and Tea
    "Americano (아메리카노) 요청사항에 HOT/ICE 부탁드립니다.": "Americano",
    "Americano (아메리카노)": "Americano",
    "아메리카노": "Americano" 
    }

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

with DAG(
    dag_id="hotel_daily_data_processing_dag",
    default_args=default_args,
    schedule="0 10 * * *",  # 매일 오전 10시 실행
    start_date=datetime(2024, 11, 20),
    catchup=False,
) as dag:

    def check_new_file_branch(ds_nodash, **kwargs):
        """
        새로운 데이터 여부를 판단
        """
        client = storage.Client()
        source_blob = client.bucket(SOURCE_BUCKET).blob(SOURCE_PATH)
        latest_blob_path = f"test_copied/csv_take_{ds_nodash}.csv"
        latest_blob = client.bucket(TARGET_BUCKET).blob(latest_blob_path)

        # 복제된 파일이 없으면 새로운 데이터로 간주
        if not latest_blob.exists():
            return "copy_file_to_target"

        # 해시값 비교
        if source_blob.md5_hash != latest_blob.md5_hash:
            return "copy_file_to_target"

        # 동일하면 새로운 데이터가 아님
        return "no_new_data"


    def process_data(ds_nodash, **kwargs):
        """
        복제된 데이터를 읽어 Pandas로 처리
        """
        client = storage.Client()
        copied_file = f"test_copied/csv_take_{ds_nodash}.csv"
        bucket = client.bucket(TARGET_BUCKET)
        blob = bucket.blob(copied_file)

        file_content = blob.download_as_text()
        file_stream = io.StringIO(file_content)
        df = pd.read_csv(file_stream)

        def parse_json_content(content):
            try:
                data = json.loads(content.replace("'", "\""))
                if isinstance(data, dict):
                    return data
                elif isinstance(data, list) and all(isinstance(item, dict) for item in data):
                    combined_data = {}
                    for item in data:
                        combined_data.update(item)
                    return combined_data
            except (json.JSONDecodeError, TypeError):
                return None

        if 'contents' in df.columns:
            expanded_df = df['contents'].apply(parse_json_content).apply(pd.Series)
            df = pd.concat([df.drop(columns=['contents']), expanded_df], axis=1)

        def apply_keyword_mapping(df, keywords, keyword_dict):
            escaped_keywords = [re.escape(keyword) for keyword in keywords]
            pattern = '|'.join(escaped_keywords)
            filtered_df = df[df['itemName'].str.contains(pattern, na=False, case=False)]
            filtered_df['itemName'] = filtered_df['itemName'].replace(keyword_dict)
            return filtered_df

        if 'itemName' in df.columns:
            df = apply_keyword_mapping(df, keywords, keyword_dict)

        processed_file_path = PROCESSED_PATH.format(ds_nodash=ds_nodash)
        df.to_csv(processed_file_path, index=False)
        print(f"Processed data saved at {processed_file_path}")

    def upload_to_ml_bucket(ds_nodash, **kwargs):
        """
        전처리된 데이터를 ML 버킷으로 업로드
        """
        client = storage.Client()
        processed_file_path = PROCESSED_PATH.format(ds_nodash=ds_nodash)
        destination_blob = f"hotel_take/take_processed_{ds_nodash}.csv"

        # ML 버킷으로 업로드
        bucket = client.bucket(ML_BUCKET)
        blob = bucket.blob(destination_blob)

        with open(processed_file_path, "rb") as file:
            blob.upload_from_file(file)

        print(f"Processed data uploaded to {ML_BUCKET}/{destination_blob}")

    def load_to_mariadb(ds_nodash, **kwargs):
        """
        처리된 데이터를 MariaDB로 적재
        """
        mysql_hook = MySqlHook(mysql_conn_id=MYSQL_CONN_ID)
        engine = mysql_hook.get_sqlalchemy_engine()

        # 처리된 CSV 파일 읽기
        processed_file_path = PROCESSED_PATH.format(ds_nodash=ds_nodash)
        df = pd.read_csv(processed_file_path)
        
        # 정규화 데이터 생성

        # order_id 생성
        if 'order_id' not in df.columns:
            df['order_id'] = range(1, len(df) + 1)  # 주문 ID 생성
        
        # result_price 생성
        if 'result_price' not in df.columns:
                if 'price' in df.columns and 'count' in df.columns:
                    df['result_price'] = df['price'].fillna(0) * df['count'].fillna(1)
                else:
                    raise ValueError("Missing columns for 'result_price': 'price' and/or 'count'")

        rooms_df = df[['room_name', 'room_building_seq', 'room_floor_seq']].drop_duplicates().reset_index(drop=True)
        rooms_df['room_id'] = rooms_df.index + 1

        customers_df = df[['customer_name']].drop_duplicates().reset_index(drop=True)
        customers_df['customer_id'] = customers_df.index + 1

        items_df = df[['itemName', 'price']].drop_duplicates().reset_index(drop=True)
        items_df.columns = ['item_name', 'price']
        items_df['item_id'] = items_df.index + 1

        # 원본 데이터에 정규화된 ID 병합
        df = df.merge(rooms_df[['room_name', 'room_id']], on='room_name', how='left') \
               .merge(customers_df[['customer_name', 'customer_id']], on='customer_name', how='left') \
               .merge(items_df[['item_name', 'item_id']], left_on='itemName', right_on='item_name', how='left')

        # 정규화된 데이터를 MariaDB에 적재
        with engine.connect() as connection:
            rooms_df.to_sql('rooms', con=connection, if_exists='replace', index=False)
            customers_df.to_sql('customers', con=connection, if_exists='replace', index=False)
            items_df.to_sql('items', con=connection, if_exists='replace', index=False)

            orders_df = df[['order_id', 'room_id', 'customer_id', 'order_price', 'status', 'reg_date']].drop_duplicates()
            orders_df.to_sql('orders', con=connection, if_exists='replace', index=False)

            order_items_df = df[['order_id', 'item_id', 'count', 'price', 'result_price']].dropna(subset=['order_id', 'item_id'])
            order_items_df.to_sql('order_items', con=connection, if_exists='replace', index=False)

    check_new_file_branch_task = BranchPythonOperator(
        task_id="check_new_file_branch",
        python_callable=check_new_file_branch,
        op_kwargs={"ds_nodash": "{{ ds_nodash }}"},
    )

    no_new_data_task = PythonOperator(
        task_id="no_new_data",
        python_callable=lambda: print("No new data to process. DAG execution stopped."),
    )

    copy_file_to_target_task = GCSToGCSOperator(
        task_id="copy_file_to_target",
        source_bucket=SOURCE_BUCKET,
        source_object=SOURCE_PATH,
        destination_bucket=TARGET_BUCKET,
        destination_object="test_copied/csv_take_{{ ds_nodash }}.csv",
    )

    process_data_task = PythonOperator(
        task_id="process_data",
        python_callable=process_data,
        op_kwargs={"ds_nodash": "{{ ds_nodash }}"},
    )

    upload_to_ml_bucket_task = PythonOperator(
        task_id="upload_to_ml_bucket",
        python_callable=upload_to_ml_bucket,
        op_kwargs={"ds_nodash": "{{ ds_nodash }}"},
    )

    load_to_mariadb_task = PythonOperator(
        task_id="load_to_mariadb",
        python_callable=load_to_mariadb,
        op_kwargs={"ds_nodash": "{{ ds_nodash }}"},
    )

    check_new_file_branch_task >> [no_new_data_task, copy_file_to_target_task]
    copy_file_to_target_task >> process_data_task >> [upload_to_ml_bucket_task, load_to_mariadb_task]
