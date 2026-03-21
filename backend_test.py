#!/usr/bin/env python3
import requests
import sys


class EGETrainerAPITester:
    def __init__(self, base_url="http://127.0.0.1:8001"):
        self.base_url = base_url.rstrip('/')
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        url = f"{self.base_url}{endpoint}"
        headers = headers or {'Content-Type': 'application/json'}
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return True, response.json()
                except Exception:
                    return True, response.text

            print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
            print(f"   Response: {response.text[:300]}")
            self.failed_tests.append(f"{name}: Expected {expected_status}, got {response.status_code}")
            return False, {}
        except requests.exceptions.Timeout:
            print("❌ Failed - Timeout")
            self.failed_tests.append(f"{name}: Timeout")
            return False, {}
        except Exception as exc:
            print(f"❌ Failed - Error: {exc}")
            self.failed_tests.append(f"{name}: {exc}")
            return False, {}

    def run_all_tests(self):
        print("🚀 Starting EGE Trainer API Tests")
        print("=" * 50)

        self.run_test("Health Check", "GET", "/api/health", 200)
        self.run_test("Get Profile", "GET", "/api/profile", 200)
        self.run_test("List Theory", "GET", "/api/theory", 200)
        self.run_test("Get Exercises Task 1", "GET", "/api/exercises/1", 200)
        self.run_test("Get Progress", "GET", "/api/progress", 200)
        self.run_test("Get Roadmap", "GET", "/api/roadmap", 200)
        self.run_test("Get Weekly Review", "GET", "/api/weekly-review", 200)
        self.run_test("Get Mock Exam Status", "GET", "/api/mock-exam", 200)
        self.run_test(
            "Save Draft",
            "PUT",
            "/api/drafts/test-scope",
            200,
            {
                "draft_type": "practice",
                "task_number": 2,
                "exercise_id": "demo_exercise",
                "payload": {"code": "print(123)"},
            },
        )
        self.run_test("Get Draft", "GET", "/api/drafts/test-scope", 200)
        self.run_test("Delete Draft", "DELETE", "/api/drafts/test-scope", 200)
        self.run_test("Reset Progress Endpoint", "POST", "/api/profile/reset", 200, {})

        print("\n" + "=" * 50)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        if self.failed_tests:
            print("\n❌ Failed Tests:")
            for fail in self.failed_tests:
                print(f"   - {fail}")
        else:
            print("\n🎉 All tests passed!")
        return self.tests_passed == self.tests_run


def main():
    tester = EGETrainerAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
