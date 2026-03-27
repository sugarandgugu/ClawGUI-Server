#!/usr/bin/env python3
"""测试 MobileWorld Server API 的脚本"""

import requests
import json
import base64
from pathlib import Path

BASE_URL = "http://localhost:7000"
DEVICE = "emulator-5554"


def test_health():
    """测试健康检查"""
    print("\n=== 测试 /health ===")
    resp = requests.get(f"{BASE_URL}/health")
    print(f"Status: {resp.status_code}")
    print(f"Response: {json.dumps(resp.json(), indent=2)}")
    return resp.json().get("ok", False)


def test_init():
    """测试初始化控制器"""
    print("\n=== 测试 /init ===")
    resp = requests.get(f"{BASE_URL}/init", params={"device": DEVICE})
    print(f"Status: {resp.status_code}")
    print(f"Response: {json.dumps(resp.json(), indent=2)}")
    return resp.status_code == 200


def test_task_init():
    """测试任务初始化"""
    print("\n=== 测试 /task/init ===")
    task_name = "ChromeSearchBeijingWeatherTask"

    resp = requests.post(
        f"{BASE_URL}/task/init",
        json={"task_name": task_name, "req_device": DEVICE}
    )
    print(f"Status: {resp.status_code}")
    print(f"Response: {json.dumps(resp.json(), indent=2)}")
    if resp.status_code == 200:
        print(f"✓ 任务 '{task_name}' 初始化成功")
    else:
        print(f"✗ 任务 '{task_name}' 初始化失败")
    return resp.status_code == 200


def test_screenshot():
    """测试截图"""
    print("\n=== 测试 /screenshot ===")
    resp = requests.get(
        f"{BASE_URL}/screenshot",
        params={"device": DEVICE, "prefix": "test_screenshot", "return_b64": False},
    )
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(f"Screenshot path: {data.get('path')}")
    return resp.status_code == 200


def test_screenshot_b64():
    """测试截图 (base64)"""
    print("\n=== 测试 /screenshot (base64) ===")
    resp = requests.get(
        f"{BASE_URL}/screenshot",
        params={"device": DEVICE, "prefix": "test_b64", "return_b64": True},
    )
    print(f"Status: {resp.status_code}")
    data = resp.json()
    if "b64_png" in data:
        print(f"Screenshot path: {data.get('path')}")
        print(f"Base64 length: {len(data.get('b64_png', ''))} chars")
        img_data = base64.b64decode(data["b64_png"])
        save_path = Path("test_screenshot.png")
        save_path.write_bytes(img_data)
        print(f"Saved to: {save_path}")
    return resp.status_code == 200


def main():
    print("=" * 60)
    print("MobileWorld Server API 测试")
    print(f"Target: {BASE_URL}")
    print(f"Device: {DEVICE}")
    print("=" * 60)

    results = {}

    results["health"] = test_health()
    results["init"] = test_init()
    results["task_init"] = test_task_init()
    results["screenshot"] = test_screenshot()
    results["screenshot_b64"] = test_screenshot_b64()

    # 总结
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {name}: {status}")
    print(f"\n总计: {passed}/{total} 通过")


if __name__ == "__main__":
    main()
