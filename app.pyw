from flask import Flask, request, jsonify
from curl_cffi import requests as cffi_requests

app = Flask(__name__)

@app.route("/", methods=["POST"])
def check_cookie():
    try:
        data = request.get_json() or {}
        cookie = data.get("cookie", "")
        if not cookie:
            return jsonify({"ok": False, "error": "missing_cookie"}), 400

        # Sử dụng curl_cffi để giả lập TLS fingerprint của trình duyệt, tránh bị Shopee chặn
        headers = {
            "cookie": cookie,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "referer": "https://shopee.vn/"
        }
        url = "https://shopee.vn/api/v4/order/get_order_list?list_type=3&offset=0&limit=5"

        resp = cffi_requests.get(url, headers=headers, impersonate="chrome120", timeout=15)

        if resp.status_code != 200:
            return jsonify({"ok": False, "error": f"HTTP {resp.status_code}"}), resp.status_code

        shopee_json = resp.json()

        # Trả dữ liệu về cho Google Apps Script xử lý
        return jsonify({
            "ok": True,
            "data": shopee_json.get("data", {}),
            "data_list": shopee_json.get("data", {}).get("order_list", [])
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
