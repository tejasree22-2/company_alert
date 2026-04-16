from fastmcp import FastMCP
import requests

mcp = FastMCP("company-alert-mcp")

BASE_URL = "http://localhost:5000"
    
# 🔐 Persistent session (stores cookies after login)
session = requests.Session()
    
    
# -------------------------------
# 🔹 LOGIN TOOL
# -------------------------------
@mcp.tool()
def login(email: str, password: str):
    """
    Login user and store session cookie
    """
    try:
        response = session.post(
            f"{BASE_URL}/login",
            json={"email": email, "password": password}
        )
    
        data = response.json()
    
        if response.status_code == 200:
            return {"status": "success", "message": "Logged in successfully"}
        else:
            return {"status": "error", "message": data.get("message")}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
    
# -------------------------------
# 🔹 GET SUBSCRIPTIONS
# -------------------------------
@mcp.tool()
def get_subscriptions():
    """
    Get logged-in user's subscriptions
    """
    try:
        response = session.get(f"{BASE_URL}/get-subscriptions")
    
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": "Failed to fetch subscriptions",
                "details": response.text
            }
    
    except Exception as e:
        return {"error": str(e)}
    
    
# -------------------------------
# 🔹 ADD COMPANY (ADMIN)
# -------------------------------
@mcp.tool()
def add_company(company_name: str, city: str, category: str):
    """
    Add a new company (admin only)
    """
    try:
        data = {
            "company_name": company_name,
            "address": "Auto generated",
            "city": city,
            "category": category,
            "opening_date": None
        }
    
        response = session.post(
            f"{BASE_URL}/add-company",
            json=data
        )
    
        if response.status_code == 201:
            return response.json()
        else:
            return {
                "error": "Failed to add company",
                "details": response.text
            }
    
    except Exception as e:
        return {"error": str(e)}
    
    
# -------------------------------
# 🔹 FIND USERS (FILTER LOGIC)
# -------------------------------
@mcp.tool()
def find_users(city: str, category: str):
    """
    Find users by city & category
    """
    try:
        response = session.get(f"{BASE_URL}/get-subscriptions")
    
        if response.status_code != 200:
            return {"error": "Not authenticated or failed request"}
    
        data = response.json()
    
        result = []
        for d in data.get("subscriptions", []):
            if (
                d["city"].lower() == city.lower()
                and d["category"].lower() == category.lower()
                and d["is_paused"] == False
            ):
                result.append(d)
    
        return {"users": result}
    
    except Exception as e:
        return {"error": str(e)}
    
    
# -------------------------------
# 🚀 RUN MCP SERVER
# -------------------------------
if __name__ == "__main__":
    print("🚀 MCP Server Running...", flush=True)
    mcp.run()
