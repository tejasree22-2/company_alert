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
# 🔹 FILTER COMPANIES (ADMIN)
# -------------------------------
@mcp.tool()
def filter_companies(city: str, category: str):
    """
    Filter companies by city and category (admin only)
    """
    try:
        response = session.get(
            f"{BASE_URL}/filter-companies",
            params={"city": city, "category": category}
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json().get("message", "Failed to filter companies")}

    except Exception as e:
        return {"error": str(e)}


# -------------------------------
# 🔹 GET ALL USERS (ADMIN)
# -------------------------------
@mcp.tool()
def get_all_users():
    """
    Get all registered users (admin only)
    """
    try:
        response = session.get(f"{BASE_URL}/get-all-users")

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json().get("message", "Failed to fetch users")}

    except Exception as e:
        return {"error": str(e)}


# -------------------------------
# 🔹 GET ALL COMPANIES (ADMIN)
# -------------------------------
@mcp.tool()
def get_all_companies():
    """
    Get all companies (admin only)
    """
    try:
        response = session.get(f"{BASE_URL}/get-all-companies")

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json().get("message", "Failed to fetch companies")}

    except Exception as e:
        return {"error": str(e)}


# -------------------------------
# 🔹 GET ALL SUBSCRIPTIONS (ADMIN)
# -------------------------------
@mcp.tool()
def get_all_subscriptions():
    """
    Get all subscriptions (admin only)
    """
    try:
        response = session.get(f"{BASE_URL}/get-all-subscriptions")

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json().get("message", "Failed to fetch subscriptions")}

    except Exception as e:
        return {"error": str(e)}


# -------------------------------
# 🔹 DELETE COMPANY (ADMIN)
# -------------------------------
@mcp.tool()
def delete_company(company_name: str, city: str):
    """
    Delete a company by name and city (admin only)
    """
    try:
        response = session.post(
            f"{BASE_URL}/delete-company",
            json={"company_name": company_name, "city": city}
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json().get("message", "Failed to delete company")}

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
# 🔹 SUBSCRIBE (USER)
# -------------------------------
@mcp.tool()
def subscribe(city: str, category: str):
    """
    Subscribe the logged-in user to a city and category
    """
    try:
        response = session.post(
            f"{BASE_URL}/subscribe",
            json={"city": city, "category": category}
        )

        if response.status_code == 201:
            return response.json()
        else:
            return {"error": response.json().get("message", "Failed to subscribe")}

    except Exception as e:
        return {"error": str(e)}


# -------------------------------
# 🔹 UNSUBSCRIBE (USER)
# -------------------------------
@mcp.tool()
def unsubscribe(city: str, category: str):
    """
    Unsubscribe the logged-in user from a city and category
    """
    try:
        response = session.post(
            f"{BASE_URL}/unsubscribe",
            json={"city": city, "category": category}
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json().get("message", "Failed to unsubscribe")}

    except Exception as e:
        return {"error": str(e)}


# -------------------------------
# 🔹 PAUSE / UNPAUSE SUBSCRIPTION (USER)
# -------------------------------
@mcp.tool()
def pause_subscription(city: str, category: str, pause: bool):
    """
    Pause or unpause a subscription by city and category. Set pause=true to pause, pause=false to unpause.
    """
    try:
        response = session.post(
            f"{BASE_URL}/pause-subscription",
            json={"city": city, "category": category, "pause": pause}
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json().get("message", "Failed to update subscription")}

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
        response = session.get(
            f"{BASE_URL}/find-users",
            params={"city": city, "category": category}
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json().get("message", "Failed to fetch users")}

    except Exception as e:
        return {"error": str(e)}   
    
    
# -------------------------------
# 🚀 RUN MCP SERVER
# -------------------------------
if __name__ == "__main__":
    print("🚀 MCP Server Running...", flush=True)
    mcp.run()
