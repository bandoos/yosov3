from locust import HttpUser, task


class SimpleHomeGet(HttpUser):

    @task
    def get_home(self):
        self.client.get("/")
