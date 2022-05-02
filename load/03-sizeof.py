from locust import HttpUser, task, between


class SizeofUser(HttpUser):
    wait_time = between(0.1, 1)

    @task
    def req(self):
        files = {'file': open("../images/apple.jpg", 'rb')}
        self.client.post("/sizeof", files=files)
