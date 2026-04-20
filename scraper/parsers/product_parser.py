#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商品数据解析器
"""
import re
from typing import Dict, Any
from loguru import logger


class ProductParser:
    """标准化商品解析器"""
    
    @staticmethod
    def parse_price(price_str: str) -> float:
        """智能解析价格字符串"""
        if not price_str:
            return 0.0
        
        price_str = str(price_str).strip()
        price_str = re.sub(r"[￥¥元,]", "", price_str)
        
        match = re.search(r"(\d+\.?\d*)", price_str)
        if match:
            return float(match.group(1))
        return 0.0
    
    @staticmethod
    def parse_sales(sales_str: str) -> int:
        """解析销量"""
        if not sales_str:
            return 0
        
        sales_str = str(sales_str)
        multiplier = 1
        
        if "万" in sales_str:
            multiplier = 10000
            sales_str = sales_str.replace("万", "")
        elif "+" in sales_str:
            sales_str = sales_str.replace("+", "")
        
        match = re.search(r"(\d+\.?\d*)", sales_str)
        if match:
            return int(float(match.group(1)) * multiplier)
        return 0
    
    @staticmethod
    def normalize_product(raw: Dict[str, Any]) -> Dict[str, Any]:
        """商品数据标准化 - 遵循DATA_SCHEMA标准"""
        return {
            "product_id": str(raw.get("product_id", raw.get("id", ""))),
            "platform": raw.get("platform", ""),
            "category": {
                "level_1": raw.get("category_1", ""),
                "level_2": raw.get("category_2", ""),
                "level_3": raw.get("category_3", "")
            },
            "product_info": {
                "title": raw.get("title", "").strip(),
                "subtitle": raw.get("subtitle", ""),
                "description": raw.get("description", ""),
                "main_image": raw.get("image", raw.get("main_image", "")),
                "detail_images": raw.get("images", []),
                "attributes": {
                    "brand": raw.get("brand", ""),
                    "model": raw.get("model", ""),
                    "specifications": raw.get("specs", "")
                }
            },
            "price": {
                "current_price": ProductParser.parse_price(raw.get("price", "")),
                "original_price": ProductParser.parse_price(raw.get("original_price", "")),
                "price_history": []
            },
            "sales": {
                "monthly_sales": ProductParser.parse_sales(raw.get("sales", "")),
                "total_sales": 0,
                "sales_trend": "",
                "inventory": ""
            },
            "seller": {
                "id": str(raw.get("seller_id", "")),
                "name": raw.get("seller_name", ""),
                "rating": raw.get("rating", 0.0),
                "fans": 0,
                "location": raw.get("location", ""),
                "is_verified": raw.get("is_verified", False),
                "response_rate": "",
                "ship_speed": ""
            },
            "service": {
                "supports_7day_return": raw.get("7day_return", False),
                "supports_cod": False,
                "free_shipping": raw.get("free_shipping", False),
                "warranty": ""
            },
            "crawl_time": __import__("time").time()
        }
    
    @staticmethod
    def extract_wholesale(info_str: str) -> Dict[str, Any]:
        """提取批发供货信息"""
        result = {
            "min_order": 1,
            "price_tiers": [],
            "supports_dropship": False,
            "dropship_price": 0.0,
            "sample_available": False,
            "customization": False
        }
        
        if "一件代发" in str(info_str) or "代发" in str(info_str):
            result["supports_dropship"] = True
        
        if "拿样" in str(info_str) or "样品" in str(info_str):
            result["sample_available"] = True
        
        return result
