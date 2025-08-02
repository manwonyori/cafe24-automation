# Migration Guide from Old System

## Overview

This guide helps you migrate from the old Cafe24 system to the new GitHub-based architecture.

## Migration Steps

### 1. Backup Current Data

```bash
# From old system directory
cd C:\Users\8899y\Documents\카페24_프로젝트

# Backup important files
mkdir backup
cp oauth_token.json backup/
cp product_cache.json backup/
cp -r logs/ backup/
```

### 2. Transfer Configuration

```bash
# Copy to new system
cp backup/oauth_token.json C:\Users\8899y\Documents\cafe24-automation-system\config\
```

### 3. Update Environment Variables

Create `config/.env` in the new system:

```env
# Copy values from old system
CAFE24_MALL_ID=your_mall_id
CAFE24_CLIENT_ID=your_client_id
CAFE24_CLIENT_SECRET=your_client_secret

# New configuration
CAFE24_API_VERSION=2025-06-01
CAFE24_CACHE_ENABLED=true
CAFE24_LOG_LEVEL=INFO
```

### 4. Migrate Custom Code

If you have custom modifications:

1. **Natural Language Commands**: Add to `src/nlp_processor.py`
2. **API Extensions**: Add to `src/api_client.py`
3. **Custom Reports**: Add to `src/utils/report_generator.py`

### 5. Test Migration

```bash
cd cafe24-automation-system

# Install dependencies
pip install -r requirements.txt

# Run health check
python src/main.py --health-check

# Test with old commands
python src/main.py -c "오늘 주문 보여줘"
```

## What's New

### Improved Architecture
- Modular design with clear separation of concerns
- Dependency injection for better testability
- Comprehensive error handling

### Enhanced Features
- Docker support for consistent deployment
- CI/CD pipeline with GitHub Actions
- Better caching with Redis support
- Health monitoring and diagnostics

### Security Improvements
- Environment-based configuration
- Encrypted token storage options
- Docker secrets support
- No hardcoded credentials

### Developer Experience
- Unit and integration tests
- Comprehensive documentation
- Type hints throughout
- Black/flake8 code formatting

## Breaking Changes

### API Changes
```python
# Old
from cafe24_integrated_system import Cafe24IntegratedManager
manager = Cafe24IntegratedManager()

# New
from src.cafe24_system import Cafe24System
system = Cafe24System()
```

### Method Signatures
```python
# Old
manager.get_all_products(batch_callback=callback)

# New
system.get_products(limit=100, offset=0)
```

### Configuration
- Configuration now uses environment variables
- No more hardcoded paths
- Docker-first approach

## Compatibility Layer

For backward compatibility, create `compat.py`:

```python
# compat.py - Backward compatibility layer
from src.cafe24_system import Cafe24System

class Cafe24IntegratedManager:
    """Compatibility wrapper for old code"""
    
    def __init__(self, secure_mode=None):
        self.system = Cafe24System()
        self.mall_id = self.system.api_client.mall_id
        
    def get_all_products(self, batch_callback=None, use_cache=True):
        products = self.system.get_products()
        if batch_callback:
            batch_callback(products, 1)
        return products
        
    def check_low_stock(self, threshold=10):
        result = self.system.check_inventory(threshold)
        return result['low_stock']
```

## Troubleshooting

### Import Errors
```python
# Add to your scripts
import sys
sys.path.append('path/to/cafe24-automation-system')
```

### Token Issues
- Ensure `oauth_token.json` is in `config/` directory
- Check token expiration dates
- Verify API credentials in `.env`

### Cache Problems
- Clear old cache: `rm -rf cache/*`
- Disable cache temporarily: `CAFE24_CACHE_ENABLED=false`

## Support

For migration support:
1. Check existing issues on GitHub
2. Create new issue with migration tag
3. Include error logs and system info