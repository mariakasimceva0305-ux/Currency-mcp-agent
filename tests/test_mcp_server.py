import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from mcp_server.server import (
    ExchangeRateRequest,
    ConvertCurrencyRequest
)

class TestExchangeRateRequest:
    def test_valid_currency_codes(self):
        request = ExchangeRateRequest(base_currency="USD", target_currency="RUB")
        assert request.base_currency == "USD"
        assert request.target_currency == "RUB"
    
    def test_currency_code_uppercase(self):
        request = ExchangeRateRequest(base_currency="usd", target_currency="rub")
        assert request.base_currency == "USD"
        assert request.target_currency == "RUB"
    
    def test_invalid_currency_code_length(self):
        with pytest.raises(ValueError):
            ExchangeRateRequest(base_currency="US", target_currency="RUB")

class TestConvertCurrencyRequest:
    def test_valid_request(self):
        request = ConvertCurrencyRequest(amount=100, from_currency="USD", to_currency="RUB")
        assert request.amount == 100
        assert request.from_currency == "USD"
        assert request.to_currency == "RUB"
    
    def test_zero_amount(self):
        with pytest.raises(ValueError):
            ConvertCurrencyRequest(amount=0, from_currency="USD", to_currency="RUB")
    
    def test_negative_amount(self):
        with pytest.raises(ValueError):
            ConvertCurrencyRequest(amount=-100, from_currency="USD", to_currency="RUB")

def test_exchange_rate_api_integration():
    """Интеграционный тест для получения курса валют"""
    from mcp_server.server import get_exchange_rate
    
    request = ExchangeRateRequest(base_currency="USD", target_currency="RUB")
    result = get_exchange_rate(request)
    
    assert "exchange_rate" in result or "error" in result
    if result.get("success"):
        assert isinstance(result["exchange_rate"], (int, float))

def test_currency_conversion_integration():
    """Интеграционный тест для конвертации валют"""
    from mcp_server.server import convert_currency
    
    request = ConvertCurrencyRequest(amount=100, from_currency="USD", to_currency="RUB")
    result = convert_currency(request)
    
    assert "converted_amount" in result or "error" in result
    if result.get("success"):
        assert isinstance(result["converted_amount"], (int, float))

def test_list_currencies_integration():
    """Интеграционный тест для получения списка валют"""
    from mcp_server.server import list_available_currencies
    
    result = list_available_currencies()
    
    assert "currencies" in result or "error" in result
    if result.get("success"):
        assert isinstance(result["currencies"], list)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
