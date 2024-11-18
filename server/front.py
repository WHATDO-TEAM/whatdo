import streamlit as st
import requests
from collections import Counter

# FastAPI 서버 URL
fastapi_url = "http://10.178.0.27:8000"

def get_recommendations(room_name: str):
    """추천 아이템을 가져오는 함수"""
    try:
        response = requests.get(
            f"{fastapi_url}/get_recommendations",
            params={"room_name": str(room_name)}
        )
        return response.json().get("recommendations", [])
    except Exception as e:
        st.error(f"추천 시스템 오류: {str(e)}")
        return []

def save_to_elasticsearch(room_name: str, visitor_cnt: int, selected_items: list):
    """선택된 항목을 ElasticSearch에 저장하는 함수"""
    try:
        response = requests.post(
            f"{fastapi_url}/save_selection",
            json={
                "room_name": room_name,
                "visitor_cnt": visitor_cnt,
                "selected_items": selected_items
            }
        )
        if response.status_code == 200:
            return True
        else:
            st.error("데이터 저장 중 오류가 발생했습니다.")
            return False
    except Exception as e:
        st.error(f"저장 중 오류 발생: {str(e)}")
        return False

st.title("방 번호 데이터 및 추천 시스템")

# 세션 상태 초기화
if 'selected_items' not in st.session_state:
    st.session_state.selected_items = {}
if 'show_recommendations' not in st.session_state:
    st.session_state.show_recommendations = False
if 'selection_complete' not in st.session_state:
    st.session_state.selection_complete = False
if 'selected_menu' not in st.session_state:
    st.session_state.selected_menu = []

def complete_selection(selected, room_name, visitor_cnt):
    st.session_state.selected_menu = selected
    # ElasticSearch에 데이터 저장
    if save_to_elasticsearch(room_name, visitor_cnt, selected):
        st.session_state.show_recommendations = False
        st.session_state.selection_complete = True
        return True
    return False

# 입력 필드
room_name = st.text_input("방 번호를 입력하세요 (예: 2507)")
visitor_cnt = st.number_input("방문객 수를 입력하세요", min_value=1, value=1)

# 데이터 조회 및 추천 버튼
if st.button("데이터 조회 및 추천"):
    st.session_state.show_recommendations = True
    st.session_state.selection_complete = False

# 추천 메뉴 표시
if st.session_state.show_recommendations:
    if not room_name:
        st.warning("방 번호를 입력해주세요.")
    else:
        try:
            recommendations = get_recommendations(room_name)

            if recommendations:
                with st.container():
                    st.subheader("이 방에 추천하는 메뉴:")

                    # 체크박스 생성
                    selected_items = {}
                    for idx, item in enumerate(recommendations, 1):
                        key = f"checkbox_{idx}"
                        selected_items[key] = st.checkbox(
                            f"{item}",
                            key=key,
                        )

                    col1, col2 = st.columns(2)
                    with col1:
                        # 선택 완료 버튼
                        if st.button("선택 완료"):
                            selected = [
                                item for idx, item in enumerate(recommendations, 1)
                                if selected_items[f"checkbox_{idx}"]
                            ]

                            if selected:
                                if complete_selection(selected, room_name, visitor_cnt):
                                    st.success("선택이 저장되었습니다!")
                                    st.rerun()
                            else:
                                st.warning("선택된 메뉴가 없습니다. 하나 이상의 메뉴를 선택해주세요.")

                    with col2:
                        # 추천 닫기 버튼
                        if st.button("추천 닫기"):
                            st.session_state.show_recommendations = False
                            st.session_state.selection_complete = False
                            st.info("추천을 취소합니다.")
                            st.rerun()

            else:
                st.info("추천 가능한 메뉴가 없습니다.")

        except Exception as e:
            st.error(f"데이터 조회 중 오류가 발생했습니다: {str(e)}")

# 선택 완료 메시지 표시
if st.session_state.selection_complete:
    st.success("선택이 완료되었습니다!")
    st.write("선택하신 메뉴:")
    for item in st.session_state.selected_menu:
        st.write(f"✓ {item}")