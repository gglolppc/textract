from fastapi import Request

def get_client_ip(request: Request) -> str:
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        # может быть список IP через запятую: "реальный_ip, прокси_ip"
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.client.host
    return ip