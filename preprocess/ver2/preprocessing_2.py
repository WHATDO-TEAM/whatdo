import pandas as pd
import json
import re

# 파일 경로
file_path = '테이크'

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

# 키워드 리스트로 필터링
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

# 키워드 매핑
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

# 키워드 필터링 및 매핑 적용
def apply_keyword_mapping(df, keywords, keyword_dict):
    # 키워드 리스트를 패턴으로 변환
    escaped_keywords = [re.escape(keyword) for keyword in keywords]
    pattern = '|'.join(escaped_keywords)
    
    # 'itemName' 열에서 키워드에 해당하는 데이터 필터링
    filtered_df = df[df['itemName'].str.contains(pattern, na=False, case=False)]
    
    # 필터링된 데이터의 'itemName' 값을 매핑된 값으로 치환
    filtered_df['itemName'] = filtered_df['itemName'].replace(keyword_dict)
    return filtered_df

# 'itemName' 열이 존재하면 필터링 및 매핑 적용
if 'itemName' in df_with_expanded_content.columns:
    result_df = apply_keyword_mapping(df_with_expanded_content, keywords, keyword_dict)
else:
    print("The 'itemName' column is missing in the dataset.")
    result_df = df_with_expanded_content

# 결과 데이터 확인
print(result_df)

# 결과를 CSV로 저장 (선택 사항)
result_df.to_csv('filtered_and_mapped_data.csv', index=False)