from locust import HttpUser, task, between

class HelloWorldUser(HttpUser):
    wait_time = between(2, 5)

    @task
    def hello_world(self):
        response = self.client.get("https://vps-4014146-x.dattaweb.com/test_download", verify=False)
        with open("nn.ts", "wb") as f:
            f.write(response.content)