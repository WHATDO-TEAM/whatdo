import streamlit as st
import requests
from typing import List, Dict

FASTAPI_URL = "http://10.178.0.27:8000"

class MenuRecommendationUI:
    def __init__(self):
        self._init_session_state()

    def _init_session_state(self):
        """세션 상태 초기화"""
        defaults = {
            'selected_items': {},
            'show_recommendations': False,
            'selection_complete': False,
            'selected_menu': [],
            'current_recommendations': []
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def get_recommendations(self, room_name: str, visitor_cnt: int) -> List[str]:
        """추천 메뉴 가져오기"""
        try:
            response = requests.post(
                f"{FASTAPI_URL}/get_recommendations",
                json={"room_name": room_name, "visitor_cnt": visitor_cnt},
                timeout=10
            )
            response.raise_for_status()
            return response.json().get("recommendations", [])
        except requests.exceptions.RequestException as e:
            st.error(f"추천 시스템 오류: {str(e)}")
            return []

    def save_selection(self, room_name: str, visitor_cnt: int,
                      selected_menu: List[str], recommendations: List[str]) -> None:
        """선택된 메뉴 저장"""
        try:
            payload = {
                "room_name": room_name,
                "visitor_cnt": visitor_cnt,
                "selected_menu": selected_menu,
                "recommendations": recommendations
            }
            response = requests.post(
                f"{FASTAPI_URL}/save_selection",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            st.success("선택이 성공적으로 저장되었습니다!")
        except requests.exceptions.RequestException as e:
            st.error(f"저장 중 오류 발생: {str(e)}")

    def run(self):
        """UI 실행"""
        st.title("방 번호 데이터 및 추천 시스템")

        with st.form("recommendation_form"):
            room_name = st.text_input("방 번호를 입력하세요 (예: 2507)")
            visitor_cnt = st.number_input("방문객 수를 입력하세요", min_value=1, value=1)
            submitted = st.form_submit_button("데이터 조회 및 추천")

            if submitted:
                if not room_name:
                    st.warning("방 번호를 입력해주세요.")
                else:
                    st.session_state.show_recommendations = True
                    st.session_state.selection_complete = False
                    recommendations = self.get_recommendations(room_name, visitor_cnt)
                    st.session_state.current_recommendations = recommendations

        if st.session_state.show_recommendations:
            self.show_recommendations(room_name, visitor_cnt)

        if st.session_state.selection_complete:
            st.success("선택이 완료되었습니다!")
            st.write("선택하신 메뉴:")
            for item in st.session_state.selected_menu:
                st.write(f"✓ {item}")

    def show_recommendations(self, room_name: str, visitor_cnt: int):
        """추천 메뉴 표시"""
        recommendations = st.session_state.current_recommendations

        if not recommendations:
            st.info("추천 가능한 메뉴가 없습니다.")
            return

        st.subheader("이 방에 추천하는 메뉴:")

        selected_items = {}
        for idx, item in enumerate(recommendations):
            selected_items[f"checkbox_{idx}"] = st.checkbox(
                item,
                key=f"menu_checkbox_{idx}"
            )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("선택 완료"):
                selected = [
                    item for idx, item in enumerate(recommendations)
                    if selected_items[f"checkbox_{idx}"]
                ]

                if not selected:
                    st.warning("하나 이상의 메뉴를 선택해주세요.")
                    return

                self.save_selection(room_name, visitor_cnt, selected, recommendations)
                st.session_state.selected_menu = selected
                st.session_state.show_recommendations = False
                st.session_state.selection_complete = True
                st.experimental_rerun()

        with col2:
            if st.button("추천 닫기"):
                st.session_state.show_recommendations = False
                st.session_state.selection_complete = False
                st.info("추천을 취소합니다.")
                st.experimental_rerun()

if __name__ == "__main__":
    app = MenuRecommendationUI()
    app.run()
