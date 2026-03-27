#!/usr/bin/env python3
"""测试 MobileWorld Server API 的脚本（真机版）- 测试 health + init + screenshot"""

import requests
import json
import base64
from pathlib import Path

# 服务器地址
BASE_URL = "http://localhost:6800"

# 真机设备名，通过 `adb devices` 命令查看你的设备 ID，替换下方的值
DEVICE = "YOUR_DEVICE_ID"

# 截图保存目录（当前脚本所在目录）
SAVE_DIR = Path(__file__).resolve().parent

def test_init():
    """先初始化设备（注册到 CONTROLLERS 字典中）"""
    print("\n=== 测试 /init ===")
    resp = requests.get(f"{BASE_URL}/init", params={"device": DEVICE})
    print(f"Status: {resp.status_code}")
    print(f"Response: {json.dumps(resp.json(), indent=2)}")
    return resp.status_code == 200


def test_health():
    """测试健康检查（需要先 init 注册设备）"""
    print("\n=== 测试 /health ===")                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
    resp = requests.get(f"{BASE_URL}/health")
    print(f"Status: {resp.status_code}")
    print(f"Response: {json.dumps(resp.json(), indent=2)}")
    return resp.json().get("ok", False)


def test_screenshot():
    """测试截图 (base64 模式，保存到本地)"""
    print("\n=== 测试 /screenshot ===")
    resp = requests.get(
        f"{BASE_URL}/screenshot",
        params={"device": DEVICE, "prefix": "test_screenshot", "return_b64": True},
    )
    print(f"Status: {resp.status_code}")
    data = resp.json()

    if resp.status_code == 200 and "b64_png" in data:
        print(f"Server screenshot path: {data.get('path')}")
        print(f"Base64 length: {len(data.get('b64_png', ''))} chars")
        # 解码并保存到本地
        img_data = base64.b64decode(data["b64_png"])
        save_path = SAVE_DIR / "test_screenshot.png"
        save_path.write_bytes(img_data)
        print(f"Screenshot saved to: {save_path}")
        print(f"File size: {save_path.stat().st_size / 1024:.1f} KB")
        return True
    else:
        print(f"Error: {data}")
        return False


def main():
    print("=" * 60)
    print("MobileWorld Server API 测试 (health + screenshot)")
    print(f"Target: {BASE_URL}")
    print(f"Device: {DEVICE}")
    print("=" * 60)

    results = {}

    # 1. 先初始化设备（注册真机到 Server）
    results["init"] = test_init()

    # 2. 健康检查（init 之后才有设备可查）
    results["health"] = test_health()

    # 3. 截图测试
    results["screenshot"] = test_screenshot()

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
