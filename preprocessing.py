import pandas as pd
import json

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

# CSV 파일로 저장
output_file_path = './Expanded_Contents_Data.csv'
df_with_expanded_content.to_csv(output_file_path, index=False)
print(f"Expanded data saved to {output_file_path}")