import json 
from pathlib import Path

from locust import HttpUser, task, between

payload = json.loads(
    Path(__file__).with_name("good_example.json")
    .read_text(encoding = 'utf-8-sig')
)

class BankServiceUser(HttpUser):
    wait_time = between(0.05, 0.2)

    @task(8)
    def predict(self):
        self.client.post("/v1/predict", json=payload, timeout=15)


    @task(2)
    def health(self):
        self.client.get("/health", timeout=5)
            

                
                
