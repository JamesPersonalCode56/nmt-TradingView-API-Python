import requests

from ..utils import gen_auth_cookies


class PinePermManager:
    def __init__(self, session_id, signature, pine_id):
        if not session_id:
            raise ValueError("Please provide a SessionID")
        if not signature:
            raise ValueError("Please provide a Signature")
        if not pine_id:
            raise ValueError("Please provide a PineID")
        self.sessionId = session_id
        self.signature = signature
        self.pineId = pine_id

    def _headers(self):
        return {
            "origin": "https://www.tradingview.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "cookie": gen_auth_cookies(self.sessionId, self.signature),
        }

    def getUsers(self, limit=10, order="-created"):
        try:
            response = requests.post(
                f"https://www.tradingview.com/pine_perm/list_users/?limit={limit}&order_by={order}",
                data=f"pine_id={self.pineId.replace(';', '%3B')}",
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json().get("results", [])
        except requests.RequestException as exc:
            detail = None
            if exc.response is not None:
                try:
                    detail = exc.response.json().get("detail")
                except ValueError:
                    detail = None
            raise ValueError(detail or "Wrong credentials or pineId") from exc

    def addUser(self, username, expiration=None):
        try:
            payload = (
                f"pine_id={self.pineId.replace(';', '%3B')}&username_recip={username}"
            )
            if expiration is not None:
                payload += f"&expiration={expiration.isoformat()}"
            response = requests.post(
                "https://www.tradingview.com/pine_perm/add/",
                data=payload,
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json().get("status")
        except requests.RequestException as exc:
            detail = None
            if exc.response is not None:
                try:
                    detail = exc.response.json().get("detail")
                except ValueError:
                    detail = None
            raise ValueError(detail or "Wrong credentials or pineId") from exc

    def modifyExpiration(self, username, expiration=None):
        try:
            payload = (
                f"pine_id={self.pineId.replace(';', '%3B')}&username_recip={username}"
            )
            if expiration is not None:
                payload += f"&expiration={expiration.isoformat()}"
            response = requests.post(
                "https://www.tradingview.com/pine_perm/modify_user_expiration/",
                data=payload,
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json().get("status")
        except requests.RequestException as exc:
            detail = None
            if exc.response is not None:
                try:
                    detail = exc.response.json().get("detail")
                except ValueError:
                    detail = None
            raise ValueError(detail or "Wrong credentials or pineId") from exc

    def removeUser(self, username):
        try:
            payload = (
                f"pine_id={self.pineId.replace(';', '%3B')}&username_recip={username}"
            )
            response = requests.post(
                "https://www.tradingview.com/pine_perm/remove/",
                data=payload,
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json().get("status")
        except requests.RequestException as exc:
            detail = None
            if exc.response is not None:
                try:
                    detail = exc.response.json().get("detail")
                except ValueError:
                    detail = None
            raise ValueError(detail or "Wrong credentials or pineId") from exc
