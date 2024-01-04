import datetime
import aiohttp
from aiohttp import ClientError
from eth_account import Account
from eth_account.messages import encode_defunct, SignableMessage
import pyuseragents


class Web3Go:
    def __init__(self, key: str, proxy: str = None) -> None:
        self.proxy = proxy
        self.key = key
        self.address = Account.from_key(key).address
        self.auth_token = None
        if self.proxy is not None:
            self.proxy_ip = self.proxy.split('@')[1]
        else: self.proxy_ip = 'No Proxy'

    async def __aenter__(self, *args):
        user_agent = pyuseragents.random()
        headers = {
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7',
                'Connection': 'keep-alive',
                'Origin': 'https://reiki.web3go.xyz',
                'Referer': 'https://reiki.web3go.xyz/taskboard',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': user_agent,
                'X-App-Channel': 'DIN',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
        }
        self.session = aiohttp.ClientSession(headers=headers)
        return self

    async def __aexit__(self, *args):
        await self.session.close()

    @staticmethod
    def sign(encoded_msg: SignableMessage, key: str):
        return Account.sign_message(encoded_msg, key)

    @staticmethod
    def get_signed_code(msg, key: str) -> str:
        return Web3Go.sign(encode_defunct(text=msg), key).signature.hex()

    async def web3_nonce(self):
        url = "https://reiki.web3go.xyz/api/account/web3/web3_nonce"
        payload = {"address": self.address}

        try:
            response = await self.session.post(url, json=payload, proxy=self.proxy)
            response.raise_for_status()
            return await response.json()
        except ClientError as e:
            print(f"Error in web3_nonce request: {e}")
            return {}


    async def web_challenge(self):
        url = 'https://reiki.web3go.xyz/api/account/web3/web3_challenge'
        params = await self.web3_nonce()

        if not params:
            print("Error getting web3_nonce data.")
            return

        address = params["address"]
        nonce = params["nonce"]
        challenge = params['challenge']

        msg = f"reiki.web3go.xyz wants you to sign in with your Ethereum account:\n{address}\n\n{challenge}\n\nURI: https://reiki.web3go.xyz\nVersion: 1\nChain ID: 56\nNonce: {nonce}\nIssued At: {Web3Go.get_utc_timestamp()}"

        json_data = {
            'address': address,
            'nonce': nonce,
            'challenge': '{"msg":"' + msg.replace('\n', '\\n') + '"}',
            'signature': Web3Go.get_signed_code(msg, self.key),
        }

        try:
            response = await self.session.post(url, json=json_data, proxy=self.proxy)
            response.raise_for_status()
            response_json = await response.json()
            auth_token = response_json['extra']['token']
            if auth_token:
                self.set_authorization_header(auth_token)
        except ClientError as e:
            print(f"Error in web_challenge request: {e}")


    def set_authorization_header(self, auth_token):
            self.auth_token = auth_token
            self.session.headers["Authorization"] = f"Bearer {auth_token}"

    async def claim(self):
        await self.web_challenge()

        url = 'https://reiki.web3go.xyz/api/checkin'
        params = {'day': Web3Go.get_current_date()}

        try:
            response = await self.session.put(url, params=params, proxy=self.proxy)
            response.raise_for_status()
            return await response.text()
        except ClientError as e:
            print(f"Error in claim request: {e}")
            return ""
            
    async def get_streak_days(self):
        await self.web_challenge()
        url = 'https://reiki.web3go.xyz/api/checkin/streakdays'
        params = {'day': Web3Go.get_current_date()}
        response = await self.session.get(url, params=params, proxy=self.proxy)
        return await response.text()
        
    async def get_info_about(self):
        url = 'https://reiki.web3go.xyz/api/GoldLeaf/me'
        if self.auth_token is None:
            await self.web_challenge()
        response = await self.session.get(url, proxy=self.proxy)
        response_data = await response.text()
        return response_data
        
    @staticmethod
    def get_current_date():
        return datetime.datetime.now().strftime("%Y-%m-%d")

    @staticmethod
    def get_utc_timestamp():
        return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
