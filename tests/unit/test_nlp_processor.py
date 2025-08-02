import pytest
from src.nlp_processor import NaturalLanguageProcessor


class TestNLPProcessor:
    """Test natural language processing"""
    
    @pytest.fixture
    def nlp(self):
        return NaturalLanguageProcessor()
    
    def test_product_commands(self, nlp):
        """Test product-related commands"""
        commands = [
            ("전체 상품 목록 보여줘", "get_products"),
            ("상품 목록", "get_products"),
            ("show all products", "get_products")
        ]
        
        for command, expected_action in commands:
            result = nlp.process(command)
            assert result is not None
            assert result['action'] == expected_action
            
    def test_order_commands(self, nlp):
        """Test order-related commands"""
        commands = [
            ("오늘 주문 내역", "get_orders"),
            ("신규 주문 보여줘", "get_orders"),
            ("today's orders", "get_orders")
        ]
        
        for command, expected_action in commands:
            result = nlp.process(command)
            assert result is not None
            assert result['action'] == expected_action
            
    def test_inventory_commands(self, nlp):
        """Test inventory commands"""
        result = nlp.process("재고 부족 상품 확인")
        assert result is not None
        assert result['action'] == 'check_inventory'
        assert result['params']['threshold'] == 10
        
        result = nlp.process("재고 5개 이하 상품")
        assert result is not None
        assert result['params']['threshold'] == 5
        
    def test_unknown_command(self, nlp):
        """Test unknown command handling"""
        result = nlp.process("알 수 없는 명령어")
        assert result is None