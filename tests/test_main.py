"""메인 실행 파일 테스트"""
import pytest
from unittest.mock import patch, MagicMock
import sys
import os


class TestMainModule:
    """main.py 모듈 테스트"""

    def test_main_module_exists(self):
        """main.py 파일이 존재하는지 테스트"""
        import main
        assert main is not None

    def test_main_has_run_demo_function(self):
        """run_demo 함수가 있는지 테스트"""
        import main
        assert hasattr(main, 'run_demo')
        assert callable(main.run_demo)


class TestRunDemo:
    """run_demo 함수 테스트"""

    @patch('main.RecommendationService')
    @patch('main.DataInitializer')
    @patch('builtins.input', side_effect=['노트북 추천해줘', 'quit'])
    @patch('builtins.print')
    def test_run_demo_processes_user_input(
        self, mock_print, mock_input, mock_init_cls, mock_service_cls
    ):
        """사용자 입력을 받아 추천 결과를 출력하는지 테스트"""
        import main

        # Mock 설정
        mock_service = MagicMock()
        mock_service_cls.return_value = mock_service
        mock_service.recommend.return_value = "LG 그램을 추천합니다."

        mock_initializer = MagicMock()
        mock_init_cls.return_value = mock_initializer

        # When: 데모 실행 (quit으로 종료)
        main.run_demo(api_key="test-key")

        # Then: 추천 서비스가 호출됨
        mock_service.recommend.assert_called_once_with("노트북 추천해줘")
