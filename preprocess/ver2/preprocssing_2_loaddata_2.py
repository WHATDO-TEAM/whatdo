import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# MariaDB 연결 설정
DB_CONFIG = {
    'user': '유저아이디',
    'password': '유저비밀번호',
    'host': '디비아이피',
    'port': '디비포트',
    'database_name': '데이터베이스이름'
}
encoded_password = quote_plus(DB_CONFIG['password'])
connection_string = (
    f"mysql+pymysql://{DB_CONFIG['user']}:{encoded_password}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database_name']}"
)
engine = create_engine(connection_string, echo=True)

# 데이터 로드
file_path = './filtered_and_mapped_data.csv'
df = pd.read_csv(file_path, low_memory=False)

# rooms, customers, items 데이터프레임 생성 및 ID 매핑
rooms_df = df[['room_name', 'room_building_seq', 'room_floor_seq']].drop_duplicates().reset_index(drop=True)
rooms_df['room_id'] = rooms_df.index + 1

customers_df = df[['customer_name']].drop_duplicates().reset_index(drop=True)
customers_df['customer_id'] = customers_df.index + 1

items_df = df[['itemName', 'price']].drop_duplicates().reset_index(drop=True)
items_df.columns = ['item_name', 'price']
items_df['item_id'] = items_df.index + 1

# room_name과 customer_name을 기준으로 room_id, customer_id 매핑
df = df.merge(rooms_df[['room_name', 'room_id']], on='room_name', how='left') \
       .merge(customers_df[['customer_name', 'customer_id']], on='customer_name', how='left') \
       .merge(items_df[['item_name', 'item_id']], left_on='itemName', right_on='item_name', how='left')

# 필수 컬럼 및 외래 키 컬럼 기본값 설정
required_columns = {
    'order_id': range(1, len(df) + 1),
    'room_id': -1,  
    'customer_id': -1,  
    'order_price': 0.0,  
    'status': 'unknown',
    'reg_date': pd.to_datetime('1970-01-01'),
    'check_date': pd.NaT,
    'refuse_date': pd.NaT,
    'complete_date': pd.NaT,
    'room_building_seq': 'N/A',
    'room_floor_seq': 'N/A',
    'visitor_cnt': 0,
    'visit_adult_cnt': 0,
    'visit_child_cnt': 0,
    'visit_baby_cnt': 0,
    'check_in': pd.NaT,
    'check_out': pd.NaT,
    'check_out_expected': pd.NaT,
    'price': 0.0,
    'count': 1,
    'result_price': lambda df: df['price'].fillna(0).astype(float) * df.get('count', 1)
}

# 필요한 컬럼 생성 및 기본값 할당
for col, default_value in required_columns.items():
    if col not in df.columns:
        df[col] = default_value(df) if callable(default_value) else default_value
    else:
        if col in ['price', 'result_price', 'order_price']:
            df[col] = df[col].fillna(0).astype(float)
        elif col == 'count':
            df[col] = df[col].fillna(1).astype(int)

# 정규화된 테이블을 위한 데이터프레임 생성
orders_df = df[['order_seq', 'room_id', 'customer_id', 'order_price', 'status', 'reg_date', 
                'check_date', 'refuse_date', 'complete_date', 'room_building_seq', 'room_floor_seq', 
                'visitor_cnt', 'visit_adult_cnt', 'visit_child_cnt', 'visit_baby_cnt', 
                'check_in', 'check_out', 'check_out_expected']].drop_duplicates()

order_items_df = df[['order_seq', 'item_id', 'count', 'price', 'result_price']].dropna(subset=['order_seq', 'item_id'])

options_df = df[['item_id', 'optionList']].dropna().drop_duplicates().rename(columns={'optionList': 'option_list'})

order_details_df = df[['order_seq', 'waitingPeriod', 'delayPeriod', 'completePeriod', 
                       'freeCount', 'couponSeq', 'perNightCount', 'isAutoPayPerNight', 
                       'itemMemo']].rename(columns={'waitingPeriod': 'waiting_period', 
                                                     'delayPeriod': 'delay_period', 
                                                     'completePeriod': 'complete_period', 
                                                     'freeCount': 'free_count', 
                                                     'couponSeq': 'coupon_seq', 
                                                     'perNightCount': 'per_night_count', 
                                                     'isAutoPayPerNight': 'is_auto_pay_per_night', 
                                                     'itemMemo': 'item_memo'})

# 데이터베이스에 테이블 삽입
with engine.connect() as connection:
    rooms_df.to_sql('rooms', con=connection, if_exists='replace', index=False)
    customers_df.to_sql('customers', con=connection, if_exists='replace', index=False)
    items_df.to_sql('items', con=connection, if_exists='replace', index=False)
    orders_df.to_sql('orders', con=connection, if_exists='replace', index=False)
    order_items_df.to_sql('order_items', con=connection, if_exists='replace', index=False)
    options_df.to_sql('options', con=connection, if_exists='replace', index=False)
    order_details_df.to_sql('order_details', con=connection, if_exists='replace', index=False)

print("데이터가 성공적으로 정규화 및 적재되었습니다.")