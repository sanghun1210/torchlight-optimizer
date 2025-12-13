"""
크롤러 기본 유틸리티 및 베이스 클래스
"""
import time
import logging
from typing import Optional
from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BaseCrawler:
    """크롤러 베이스 클래스"""

    BASE_URL = "https://tlidb.com"

    def __init__(self, delay: float = 1.0):
        """
        Args:
            delay: 요청 간 대기 시간 (초)
        """
        self.delay = delay
        self.session = self._create_session()
        self.last_request_time = 0

    def _create_session(self) -> requests.Session:
        """재시도 로직이 포함된 세션 생성"""
        session = requests.Session()

        # 재시도 전략
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # User-Agent 설정
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

        return session

    def _rate_limit(self):
        """Rate limiting 적용"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.delay:
            sleep_time = self.delay - time_since_last_request
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        URL에서 페이지를 가져와 BeautifulSoup 객체 반환

        Args:
            url: 크롤링할 URL

        Returns:
            BeautifulSoup 객체 또는 None (실패 시)
        """
        self._rate_limit()

        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')
            return soup

        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None

    def get_absolute_url(self, relative_url: str) -> str:
        """상대 URL을 절대 URL로 변환"""
        if relative_url.startswith('http'):
            return relative_url
        # 슬래시가 없으면 추가
        if not relative_url.startswith('/'):
            relative_url = '/' + relative_url
        return f"{self.BASE_URL}{relative_url}"

    def extract_text(self, element, default: str = "") -> str:
        """엘리먼트에서 텍스트 추출"""
        if element is None:
            return default
        return element.get_text(strip=True)

    def extract_attribute(self, element, attr: str, default: str = "") -> str:
        """엘리먼트에서 속성 추출"""
        if element is None:
            return default
        return element.get(attr, default)

    def close(self):
        """세션 종료"""
        self.session.close()
        logger.info("Crawler session closed")

    def __enter__(self):
        """컨텍스트 매니저 진입"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.close()


class DataParser:
    """HTML 데이터 파싱 유틸리티"""

    @staticmethod
    def parse_stat_value(stat_text: str) -> Optional[float]:
        """
        스탯 텍스트에서 숫자 추출
        예: "+50 Armor" -> 50.0, "10%" -> 10.0
        """
        import re

        # 숫자 패턴 찾기
        match = re.search(r'[-+]?\d+\.?\d*', stat_text)
        if match:
            return float(match.group())
        return None

    @staticmethod
    def clean_description(text: str) -> str:
        """설명 텍스트 정리"""
        import re

        # 여러 공백을 하나로
        text = re.sub(r'\s+', ' ', text)
        # 앞뒤 공백 제거
        text = text.strip()
        return text

    @staticmethod
    def extract_image_url(img_element, base_url: str = "https://tlidb.com") -> Optional[str]:
        """이미지 URL 추출"""
        if img_element is None:
            return None

        src = img_element.get('src') or img_element.get('data-src')
        if src:
            if src.startswith('http'):
                return src
            return f"{base_url}{src}"
        return None

    @staticmethod
    def parse_tags(tags_text: str) -> list:
        """
        태그 텍스트를 리스트로 변환
        예: "AoE, DoT, Fire" -> ["AoE", "DoT", "Fire"]
        """
        if not tags_text:
            return []
        return [tag.strip() for tag in tags_text.split(',') if tag.strip()]


if __name__ == "__main__":
    # 테스트
    with BaseCrawler(delay=1.0) as crawler:
        soup = crawler.fetch_page("https://tlidb.com")
        if soup:
            title = soup.find('title')
            print(f"Page title: {crawler.extract_text(title)}")
