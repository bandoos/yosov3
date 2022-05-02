from locust import HttpUser, task, between


class SimplePredict(HttpUser):
    wait_time = between(0.1, 1)

    @task
    def predict_req(self):
        files = {'file': open("../images/apple.jpg", 'rb')}
        self.client.post("/predict?model=yolov3-tiny&confidence=0.5",
                         files=files)
