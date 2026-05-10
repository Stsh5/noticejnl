#!/usr/bin/env python
"""
テスト実行スクリプト
依存ライブラリのインストールとテスト実行を行う
"""
import subprocess
import sys

def install_dependencies():
    """依存ライブラリをインストール"""
    packages = [
        'requests',
        'pytest',
        'pytest-mock',
        'python-dateutil'
    ]
    
    print("=" * 60)
    print("依存ライブラリをインストール中...")
    print("=" * 60)
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', package])
            print(f"✓ {package} をインストール")
        except subprocess.CalledProcessError as e:
            print(f"✗ {package} のインストールに失敗: {e}")
            return False
    
    return True

def run_tests():
    """テストを実行"""
    print("\n" + "=" * 60)
    print("テストを実行中...")
    print("=" * 60 + "\n")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', 'tests/test_collecting.py', '-v'],
            cwd='D:\\working\\dev-noticejnl'
        )
        return result.returncode == 0
    except Exception as e:
        print(f"テスト実行エラー: {e}")
        return False

if __name__ == '__main__':
    if not install_dependencies():
        print("\n依存ライブラリのインストールに失敗しました")
        sys.exit(1)
    
    if not run_tests():
        print("\nテスト実行に失敗しました")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✓ すべてのテストが完了しました")
    print("=" * 60)
