import os
import requests
from typing import Dict, List
from fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("currency-exchange")

API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")
BASE_URL = "https://v6.exchangerate-api.com/v6"

class ExchangeRateRequest(BaseModel):
    base_currency: str = Field(..., description="Базовая валюта (например: USD)")
    target_currency: str = Field(..., description="Целевая валюта (например: RUB)")
    
    @field_validator('base_currency', 'target_currency')
    @classmethod
    def validate_currency_code(cls, v):
        if len(v) != 3:
            raise ValueError('Код валюты должен состоять из 3 букв')
        return v.upper()

class ConvertCurrencyRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Сумма для конвертации")
    from_currency: str = Field(..., description="Исходная валюта (например: USD)")
    to_currency: str = Field(..., description="Целевая валюта (например: RUB)")
    
    @field_validator('from_currency', 'to_currency')
    @classmethod
    def validate_currency_code(cls, v):
        if len(v) != 3:
            raise ValueError('Код валюты должен состоять из 3 букв')
        return v.upper()

def get_exchange_rate_data(base_currency: str) -> Dict:
    """Получает данные о курсах валют от API"""
    url = f"{BASE_URL}/{API_KEY}/latest/{base_currency}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("result") != "success":
            raise ValueError(f"API error: {data.get('error-type', 'Unknown error')}")
            
        return data
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Ошибка подключения к API: {str(e)}")
    except ValueError as e:
        raise ValueError(str(e))

@mcp.tool()
def get_exchange_rate(request: ExchangeRateRequest) -> Dict:
    """Получает текущий обменный курс между двумя валютами"""
    try:
        data = get_exchange_rate_data(request.base_currency)
        
        if request.target_currency not in data["conversion_rates"]:
            available = list(data["conversion_rates"].keys())[:10]
            return {
                "success": False,
                "error": f"Валюта {request.target_currency} не найдена",
                "available_currencies_sample": available,
                "timestamp": data["time_last_update_utc"]
            }
        
        rate = data["conversion_rates"][request.target_currency]
        
        return {
            "success": True,
            "base_currency": request.base_currency,
            "target_currency": request.target_currency,
            "exchange_rate": rate,
            "timestamp": data["time_last_update_utc"],
            "inverse_rate": 1 / rate if rate != 0 else 0
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "base_currency": request.base_currency,
            "target_currency": request.target_currency
        }

@mcp.tool()
def convert_currency(request: ConvertCurrencyRequest) -> Dict:
    """Конвертирует сумму из одной валюты в другую"""
    try:
        data = get_exchange_rate_data(request.from_currency)
        
        if request.to_currency not in data["conversion_rates"]:
            available = list(data["conversion_rates"].keys())[:10]
            return {
                "success": False,
                "error": f"Валюта {request.to_currency} не найдена",
                "available_currencies_sample": available
            }
        
        rate = data["conversion_rates"][request.to_currency]
        converted_amount = request.amount * rate
        
        return {
            "success": True,
            "original_amount": request.amount,
            "original_currency": request.from_currency,
            "converted_amount": round(converted_amount, 2),
            "target_currency": request.to_currency,
            "exchange_rate": rate,
            "timestamp": data["time_last_update_utc"],
            "formatted_result": f"{request.amount} {request.from_currency} = {round(converted_amount, 2)} {request.to_currency}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "original_amount": request.amount,
            "original_currency": request.from_currency,
            "target_currency": request.to_currency
        }

@mcp.tool()
def list_available_currencies() -> Dict:
    """Возвращает список всех доступных валют с кодами и названиями"""
    try:
        data = get_exchange_rate_data("USD")
        
        currency_names = {
            "USD": "US Dollar", "EUR": "Euro", "GBP": "British Pound",
            "JPY": "Japanese Yen", "CAD": "Canadian Dollar",
            "AUD": "Australian Dollar", "CHF": "Swiss Franc",
            "CNY": "Chinese Yuan", "RUB": "Russian Ruble",
            "INR": "Indian Rupee", "BRL": "Brazilian Real",
            "MXN": "Mexican Peso", "KRW": "South Korean Won",
            "SGD": "Singapore Dollar", "HKD": "Hong Kong Dollar",
            "NOK": "Norwegian Krone", "SEK": "Swedish Krona",
            "TRY": "Turkish Lira", "ZAR": "South African Rand"
        }
        
        currencies = []
        for code in data["conversion_rates"].keys():
            currencies.append({
                "code": code,
                "name": currency_names.get(code, code),
                "rate_to_usd": data["conversion_rates"][code]
            })
        
        currencies.sort(key=lambda x: x["code"])
        
        return {
            "success": True,
            "total_currencies": len(currencies),
            "currencies": currencies[:50],
            "timestamp": data["time_last_update_utc"],
            "base_currency": data["base_code"]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "currencies": []
        }

if __name__ == "__main__":
    mcp.run(transport=["stdio", "http"])
