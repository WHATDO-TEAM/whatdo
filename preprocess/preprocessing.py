import pandas as pd
import json
import re
# 파일 경로
file_path = './csv_Take.csv'

# 데이터 로드
df = pd.read_csv(file_path, low_memory=False)

# JSON 데이터를 파싱하여 컬럼 확장
def parse_json_content(content):
    try:
        # Attempt to load JSON content
        data = json.loads(content.replace("'", "\""))
        if isinstance(data, dict):
            return data  # Return the dictionary if parsed successfully
        elif isinstance(data, list) and all(isinstance(item, dict) for item in data):
            # Combine list of dictionaries into one dictionary (if appropriate)
            combined_data = {}
            for item in data:
                combined_data.update(item)  # Merge dictionaries
            return combined_data
    except (json.JSONDecodeError, TypeError):
        # Return None if parsing fails
        return None

# 'contents' 열의 JSON 데이터를 컬럼으로 확장
if 'contents' in df.columns:
    expanded_df = df['contents'].apply(parse_json_content).apply(pd.Series)
    # 원본 데이터와 확장된 컬럼 병합
    df_with_expanded_content = pd.concat([df.drop(columns=['contents']), expanded_df], axis=1)
else:
    print("The 'contents' column is missing in the dataset.")
    df_with_expanded_content = df






columns = [
    'id', 'col1', 'col2', 'col3', 'status', 'date1', 'date2', 'col4', 'date3', 'col5', 'col6', 'col7', 'col8', 'col9', 
    'col10', 'col11', 'col12', 'col13', 'date4', 'date5', 'date6', 'col14', 'col15', 'col16', 'col17', 'itemName', 
    'col18', 'col19', 'col20', 'col21', 'col22', 'col23', 'col24', 'col25', 'col26'
]

df = pd.DataFrame(data, columns=columns)

# 키워드 리스트와 매핑
keywords = [
    "Chicken Karaage & Fried  Dishes (치킨 가라아게 & 모둠 튀김)", "Beef Truffle Zappaghetti(소고기 트러플 짜파게티)",
    "Mini Burger Set (미니버거 세트) 음료 선택 필수", "Bluemoon Draft Beer (블루문 생맥주)", "Miller Draft Beer (밀러 생맥주)"
    # 나머지 키워드들
]

keyword_dict = {
    "Chicken Karaage & Fried  Dishes (치킨 가라아게 & 모둠 튀김)": "Chicken Karaage & Fried Dishes",
    "Beef Truffle Zappaghetti(소고기 트러플 짜파게티)": "Beef Truffle Zappaghetti",
    "Mini Burger Set (미니버거 세트) 음료 선택 필수": "Mini Burger Set",
    "Bluemoon Draft Beer (블루문 생맥주)": "Beer",
    "Miller Draft Beer (밀러 생맥주)": "Beer"
    # 나머지 매핑들
}

# 키워드 리스트를 패턴으로 변환
escaped_keywords = [re.escape(keyword) for keyword in keywords]
pattern = '|'.join(escaped_keywords)

# itemName 열에서 키워드에 해당하는 데이터 필터링
filtered_df = df[df['itemName'].str.contains(pattern, na=False, case=False)]

# 필터링된 데이터의 itemName 값을 매핑된 값으로 치환
filtered_df['itemName'] = filtered_df['itemName'].replace(keyword_dict)

# 결과 확인
print(filtered_df)

# CSV 파일로 저장
output_file_path = './Expanded_Contents_Data.csv'
df_with_expanded_content.to_csv(output_file_path, index=False)
print(f"Expanded data saved to {output_file_path}")