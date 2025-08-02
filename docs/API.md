# Cafe24 API Documentation

## Overview

The Cafe24 Automation System provides a comprehensive API wrapper for the Cafe24 e-commerce platform, with additional features like natural language processing, caching, and automated workflows.

## Core Components

### 1. Cafe24System

The main entry point for all operations.

```python
from src.cafe24_system import Cafe24System

# Initialize system
system = Cafe24System()

# Execute natural language command
result = system.execute("오늘 주문 목록 보여줘")

# Direct API calls
products = system.get_products(limit=100)
orders = system.get_orders(start_date="2024-01-01")
```

### 2. API Client

Low-level API wrapper with automatic retry and token management.

```python
from src.api_client import Cafe24APIClient

client = Cafe24APIClient(config)

# Product operations
products = client.get_products(limit=100, offset=0)
product = client.get_product(product_no=123)
client.update_product(product_no=123, data={'price': '20000'})

# Order operations
orders = client.get_orders(start_date='2024-01-01', end_date='2024-01-31')
order = client.get_order(order_id='20240101-0000001')
client.update_order_status(order_id='20240101-0000001', status='N20')
```

### 3. Natural Language Processor

Process Korean and English commands.

```python
from src.nlp_processor import NaturalLanguageProcessor

nlp = NaturalLanguageProcessor()
intent = nlp.process("재고 부족 상품 확인해줘")
# Returns: {'action': 'check_inventory', 'params': {'threshold': 10}}
```

## API Methods

### Products

#### Get Products
```python
products = system.get_products(
    limit=100,              # Number of products to retrieve
    offset=0,               # Pagination offset
    category=None,          # Filter by category
    display='T',            # Display status (T/F)
    selling='T',            # Selling status (T/F)
    product_name=None       # Search by name
)
```

#### Update Product
```python
result = system.update_products([
    {
        'product_no': 123,
        'data': {
            'price': '25000',
            'display': 'T',
            'selling': 'T'
        }
    }
])
```

### Orders

#### Get Orders
```python
orders = system.get_orders(
    start_date='2024-01-01',   # Start date (YYYY-MM-DD)
    end_date='2024-01-31',     # End date (YYYY-MM-DD)
    status='N00',              # Order status
    limit=100,                 # Number of orders
    embed='items,buyer'        # Embedded data
)
```

### Inventory

#### Check Inventory
```python
inventory = system.check_inventory(
    threshold=10    # Low stock threshold
)

# Returns:
{
    'low_stock': [...],      # Products below threshold
    'out_of_stock': [...],   # Products with 0 inventory
    'total_products': 150,
    'threshold': 10
}
```

### Reports

#### Generate Reports
```python
# Daily report
daily_report = system.generate_report('daily')

# Inventory report
inventory_report = system.generate_report('inventory')

# Sales report
sales_report = system.generate_report('sales')
```

## Natural Language Commands

### Korean Commands

- **Products**: "전체 상품 목록", "상품 보여줘", "카테고리:의류 상품"
- **Orders**: "오늘 주문 내역", "이번주 신규 주문", "어제 주문 목록"
- **Inventory**: "재고 부족 상품", "품절 상품 확인", "재고 5개 이하"
- **Reports**: "일일 리포트 생성", "재고 보고서", "매출 통계"

### English Commands

- **Products**: "show all products", "list products", "search products"
- **Orders**: "today's orders", "new orders this week", "yesterday orders"
- **Inventory**: "check low stock", "out of stock items", "inventory check"
- **Reports**: "generate daily report", "inventory report", "sales statistics"

## Error Handling

All API calls include automatic retry logic and comprehensive error handling:

```python
try:
    result = system.execute("잘못된 명령어")
except Exception as e:
    print(f"Error: {e}")
```

## Caching

The system includes intelligent caching to minimize API calls:

```python
# First call - fetches from API
products = system.get_products()  # Takes 2 seconds

# Second call - returns from cache
products = system.get_products()  # Takes 0.001 seconds
```

Cache TTL is configurable via environment variables (default: 3600 seconds).

## Rate Limiting

The API client respects Cafe24's rate limits:
- Automatic retry with exponential backoff
- Configurable retry count and delays
- Proper error handling for 429 responses