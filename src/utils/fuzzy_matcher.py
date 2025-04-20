import re
from rapidfuzz import process, fuzz
from typing import List, Dict
import jieba
from models.orders import Item, Product

def normalize(text: str) -> str:
    """
    Normalize the text by removing special characters, keeping only Chinese characters, English letters, and digits.
    """
    if not text:
        return ""
    return re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9]", "", text)


def tokenize(text):
    # 將中文詞切開後再 join 成 token string
    return " ".join(jieba.cut_for_search(text or ""))


def match_items(items: List[Item], products: List[Product], customer_name=None, order_date=None, threshold: float = 0.5):
    matched_results = []

    for item in items:
        item_name = item.item_name.strip()
        original_input = item.original_input.strip()
        quantity = float(item.quantity or 0)
        unit = (item.unit or "").strip()

        best_score = 0
        best_match = None

        tokenized_item = " ".join(jieba.cut(item_name))

        for product in products:
            product_name_raw = product.product_name.strip()
            aliases = product_name_raw.split("/")  # 支援別名

            for alias in aliases:
                alias = alias.strip()

                # --- Strategy 1: 完全匹配 ---
                if alias == item_name:
                    best_score = 1.0
                    best_match = product
                    break

                # --- Strategy 2: 子字串匹配 ---
                if item_name in alias or alias in item_name:
                    score = 0.95
                    if score > best_score:
                        best_score = score
                        best_match = product
                    continue

                # --- Strategy 3: 分詞模糊匹配 ---
                tokenized_alias = " ".join(jieba.cut(alias))
                score = fuzz.token_sort_ratio(tokenized_item, tokenized_alias) / 100

                if score > best_score:
                    best_score = score
                    best_match = product

        if not best_match or best_score < threshold:
            continue

        price = float(best_match.unit_price or 0)
        subtotal = quantity * price

        result = {
            "product_id": best_match.id,
            "matched_name": best_match.product_name,
            "original_input": original_input,
            "quantity": quantity,
            "unit_price": price,
            "subtotal": subtotal,
            "match_score": round(best_score, 4)
        }

        matched_results.append(result)

    total_amount = sum(item["subtotal"] for item in matched_results)

    return {
        "customer_name": customer_name,
        "order_date": order_date,
        "items": matched_results,
        "total_amount": round(total_amount, 2),
        "tax": 0,
        "status": "completed"
    }