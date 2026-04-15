from fastmcp import FastMCP
import requests

mcp = FastMCP("company-alert-mcp")

BASE_URL = "http://localhost:5000"

# 🔹 TOOL 1: Get subscriptions
@mcp.tool()
def get_subscriptions():
    try:
        response = requests.get(f"{BASE_URL}/mcp/subscriptions", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e), "status_code": getattr(response, "status_code", None), "body": getattr(response, "text", "")[:200]}


# 🔹 TOOL 2: Add company
@mcp.tool()
def add_company(company_name: str, city: str, category: str):
    data = {
        "company_name": company_name,
        "address": "Auto generated",
        "city": city,
        "category": category,
    }

    response = requests.post(f"{BASE_URL}/mcp/add-company", json=data)
    return response.json()


# 🔹 TOOL 3: Filter subscriptions
@mcp.tool()
def find_users(city: str, category: str):
    data = requests.get(f"{BASE_URL}/mcp/subscriptions").json()

    result = []
    for d in data.get("subscriptions", []):
        if (
            d["city"].lower() == city.lower()
            and d["category"].lower() == category.lower()
            and d["is_paused"] == False
        ):
            result.append(d)

    return result


if __name__ == "__main__":
    mcp.run()
