import time
from requests import get, post
from time import sleep
from logging import getLogger

class Reese84Cookie:
    def __init__(
        self, 
        api_key: str,
        base_url: str,
        logger = getLogger("reese84_cookie")
    ) -> None:
        self.api_key, self.base_url, self.logger = \
            api_key, base_url, logger
        pass

    def create_task(self, **kwargs) -> str:
        task_payload = self.create_task_imperva_v2(**kwargs)
        task_request: dict = post(
            f"{self.base_url}/imperva-v2",
            headers={"X-API-Key": self.api_key},
            json=task_payload,
        ).json()
        if task_request.get('task_id'):
            self.logger.debug(f"Task created -> {task_request}")
            return task_request.get('task_id')
        raise Exception(f"[FailedToCreateTask] Server response -> {task_request}")

    def create_task_imperva_v2(
        self,
        url: str,
        proxy: str = None,
    ) -> str:
        return {
            "task_type": "imperva",
            "task_mode": "normal",
            "url": url,
            "proxy": proxy,
        }

    def get_task_result(self, task_id: str) -> str:
        get_task_result_request = get(
            f"{self.base_url}/imperva-v2/{task_id}",
            headers={"X-API-Key": self.api_key},
        ).json()
        task_status = get_task_result_request["task_status"]
        while task_status == "queued" or task_status == "running":
            self.logger.debug(f"Task is still processing -> {get_task_result_request}")
            sleep(2)
            get_task_result_request = get(
                f"{self.base_url}/imperva-v2/{task_id}",
                headers={"X-API-Key": self.api_key},
            ).json()
            task_status = get_task_result_request["task_status"]
        self.logger.debug(f"Task is done -> {get_task_result_request}")
        if get_task_result_request["task_status"] == "finished":
            # return get_task_result_request['solution']['gRecaptchaResponse']
            return get_task_result_request["token"]
        raise Exception(f"[FailedToGetTaskResult] Server response -> {get_task_result_request}")

    def solve_captcha(self, **kwargs) -> str:
        task_id = self.create_task(**kwargs)
        sleep(0.65)
        return self.get_task_result(task_id)

if __name__ == '__main__':
    base_url = "https://imperva.ganhj.dev"
    api_key = "FLASH_API_XXXXXX" # Contact us to get temp. API key
    target_url = "https://ticketmaster.sg/epsf/eps-d?d=ticketmaster.sg" # Find the target url with "?d="
    proxy = "http://user:password@proxy.packetstream.io:31112"
    
    print(f"Target URL => {target_url}")
    start_time = time.time()
    reese84_solver = Reese84Cookie(base_url=base_url, api_key=api_key)
    reese84_token = reese84_solver.solve_captcha(url=target_url,proxy=proxy)
    print(f"reese84 => {reese84_token}")
    print(f"Time taken => {(time.time() - start_time):.3f}s")