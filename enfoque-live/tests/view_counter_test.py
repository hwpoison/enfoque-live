import requests
import time
import random
import string
import concurrent.futures

def test_load_status_route():
    base_url = "http://localhost/status/"  # replace with your app's base URL
    num_requests = 1000  # adjust the number of requests to simulate load
    concurrency = 10  # adjust the concurrency level

    def make_request(token):
        url = f"{base_url}{token}"
        response = requests.get(url)
        assert response.status_code in [200, 503]

    def generate_random_token(length=10):
        letters_and_digits = string.ascii_letters + string.digits
        result_str = ''.join(random.choice(letters_and_digits) for i in range(length))
        return result_str

    def make_request_concurrent(token):
        make_request(token)

    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(make_request_concurrent, generate_random_token()) for _ in range(num_requests)]
        for future in concurrent.futures.as_completed(futures):
            future.result()
    end_time = time.time()

    print(f"Completed {num_requests} requests in {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    test_load_status_route()