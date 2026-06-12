from __future__ import annotations

KIS_INDEX_CODES = {
    "KOSPI": "0001",
    "KOSDAQ": "1001",
    "KOSPI200": "2001",
}

# KIS 업종 master(`idxcode.mst`) 기준 주요 업종 코드.
# 파일 원문은 5자리지만 첫 자리는 시장구분값이고 API 입력 코드는 뒤 4자리다.
KIS_SECTOR_CODES = {
    "KOSPI_ELECTRONICS": "0013",  # 전기·전자: 반도체/전자 대표 proxy
    "KOSPI_TRANSPORT_EQUIPMENT": "0015",  # 운송장비·부품: 자동차 proxy
    "KOSPI_FINANCE": "0021",
    "KOSPI_CHEMICALS": "0008",
    "KOSPI_PHARMA": "0009",
    "KOSPI_CONSTRUCTION": "0018",
    "KOSDAQ_IT_SERVICE": "1033",
    "KOSPI200_INFORMATION_TECHNOLOGY": "2013",
    "KOSPI200_FINANCE": "2014",
}

KIS_SECTOR_NAMES = {
    "KOSPI_ELECTRONICS": "KOSPI 전기·전자",
    "KOSPI_TRANSPORT_EQUIPMENT": "KOSPI 운송장비·부품",
    "KOSPI_FINANCE": "KOSPI 금융",
    "KOSPI_CHEMICALS": "KOSPI 화학",
    "KOSPI_PHARMA": "KOSPI 제약",
    "KOSPI_CONSTRUCTION": "KOSPI 건설",
    "KOSDAQ_IT_SERVICE": "KOSDAQ IT 서비스",
    "KOSPI200_INFORMATION_TECHNOLOGY": "KOSPI200 정보기술",
    "KOSPI200_FINANCE": "KOSPI200 금융",
}

KIS_SECTOR_CODE_TO_NAME = {
    code: KIS_SECTOR_NAMES[key]
    for key, code in KIS_SECTOR_CODES.items()
}
