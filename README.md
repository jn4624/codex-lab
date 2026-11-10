# 고객관리 실습 DB

고객, 상품, 직원, 주문을 관리하는 SQLite 데이터베이스 실습 프로젝트입니다. SQLAlchemy 2.x 모델을 사용하며 DB 파일 `customer.db`는 `database.py`와 같은 폴더에 생성됩니다.

## 요구 사항

- Python 3.10 이상
- SQLAlchemy 2.x
- Faker

## 설치 및 실행

프로젝트 폴더(`codex-lab`)에서 실행합니다.

```bash
python -m pip install "SQLAlchemy>=2.0,<3.0" Faker
python database.py
python seed.py
```

`database.py`는 테이블을 생성합니다. `seed.py`는 한국어 더미 데이터를 입력하고 테이블별 건수를 출력합니다. 재실행할 때도 같은 데이터를 만들 수 있도록 random seed를 고정했습니다. 동일한 결과를 재현하려면 같은 Faker 버전을 사용하세요.

> `seed.py`를 실행하면 네 테이블의 기존 행을 삭제한 뒤 데이터를 다시 채웁니다.

## 데이터 규모와 생성 규칙

| 테이블 | 행 수 | 주요 생성 규칙 |
|---|---:|---|
| `customers` | 10,000 | Faker `ko_KR` 한국어 이름·전화번호·주소, VIP 500명 / 일반 7,000명 / 신규 2,500명 |
| `products` | 500 | 5개 카테고리, 가격 1,000~2,000,000원 |
| `employees` | 300 | 한국어 이름, 부서, 입사일 |
| `orders` | 100,000 | 고객·상품·담당 직원 FK, 수량 1~5, 최근 2년 날짜, 완료 90,000건 / 배송중 7,000건 / 취소 3,000건 |

주문 금액(`total_amount`)은 주문 시점 단가(`unit_price`)와 수량(`quantity`)의 곱입니다. 주문일 분포 기준은 2026-11-10으로 고정되어 있습니다. 주문 한 건에는 상품 하나가 연결됩니다.

## 테이블과 관계

- `customers` 1:N `orders`
- `products` 1:N `orders`
- `employees` 1:N `orders`

컬럼, PK/FK와 ERD는 [`erd.md`](erd.md)를 참고하세요. SQLite 연결에서 외래키 검사를 활성화합니다.

## 파일 구성

- `models.py`: `Customer`, `Product`, `Employee`, `Order` SQLAlchemy 모델
- `database.py`: SQLite 엔진, 세션 팩토리, 테이블 생성
- `seed.py`: 고정 seed 기반 대량 데이터 생성
- `erd.md`: 실제 DB 스키마의 Mermaid ERD
- `customer.db`: 생성되는 SQLite DB 파일
