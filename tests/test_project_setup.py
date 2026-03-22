"""프로젝트 초기 설정 테스트 - TDD Red Phase"""
import os


class TestProjectStructure:
    """프로젝트 구조가 올바르게 설정되었는지 확인"""

    def test_src_directory_exists(self):
        """src 디렉토리가 존재해야 함"""
        assert os.path.isdir("src")

    def test_tests_directory_exists(self):
        """tests 디렉토리가 존재해야 함"""
        assert os.path.isdir("tests")

    def test_src_is_python_package(self):
        """src가 Python 패키지여야 함 (__init__.py 존재)"""
        assert os.path.isfile("src/__init__.py")

    def test_requirements_file_exists(self):
        """requirements.txt 파일이 존재해야 함"""
        assert os.path.isfile("requirements.txt")

    def test_requirements_contains_dependencies(self):
        """requirements.txt에 필수 의존성이 포함되어야 함"""
        with open("requirements.txt", "r") as f:
            content = f.read()

        required_packages = [
            "google-generativeai",
            "chromadb",
            "pytest",
        ]

        for package in required_packages:
            assert package in content, f"{package}가 requirements.txt에 없음"
