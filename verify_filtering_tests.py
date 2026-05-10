"""
フィルタリング機能の簡易テスト検証スクリプト
"""
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

try:
    from collecting import is_recent, match_keywords, KEYWORDS
    print("✓ collecting モジュールをインポート")
except Exception as e:
    print(f"✗ collecting インポート失敗: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("フィルタリング機能の基本テスト")
print("=" * 60)

# テスト1: is_recent - 最近の論文
print("\n[テスト1] is_recent - 最近の論文")
try:
    now = datetime.utcnow()
    recent_date = (now - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    entry = MagicMock()
    entry.published = recent_date
    
    result = is_recent(entry, days=3)
    assert result is True, "最近の論文として判定されるべき"
    print("✓ 最近の論文を正しく判定")
except Exception as e:
    print(f"✗ テスト失敗: {e}")

# テスト2: is_recent - 古い論文
print("\n[テスト2] is_recent - 古い論文")
try:
    now = datetime.utcnow()
    old_date = (now - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    entry = MagicMock()
    entry.published = old_date
    
    result = is_recent(entry, days=3)
    assert result is False, "古い論文として判定されるべき"
    print("✓ 古い論文を正しく判定")
except Exception as e:
    print(f"✗ テスト失敗: {e}")

# テスト3: is_recent - カスタム日数
print("\n[テスト3] is_recent - カスタム日数")
try:
    now = datetime.utcnow()
    date_2_days_ago = (now - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    entry = MagicMock()
    entry.published = date_2_days_ago
    
    assert is_recent(entry, days=1) is False, "1日以内として判定されるべき"
    assert is_recent(entry, days=3) is True, "3日以内として判定されるべき"
    print("✓ カスタム日数でのフィルタリングが正常に動作")
except Exception as e:
    print(f"✗ テスト失敗: {e}")

# テスト4: match_keywords - タイトルに含まれる
print("\n[テスト4] match_keywords - タイトルに含まれる")
try:
    entry = MagicMock()
    entry.title = "Silica Clathrate Structures in Nanoporous Materials"
    entry.summary = "Study of porous structures"
    
    result = match_keywords(entry)
    assert result is True, "キーワードマッチするべき"
    print(f"✓ タイトルのキーワード検出成功")
    print(f"  - キーワード: {KEYWORDS}")
    print(f"  - タイトル: {entry.title}")
except Exception as e:
    print(f"✗ テスト失敗: {e}")

# テスト5: match_keywords - アブストラクトに含まれる
print("\n[テスト5] match_keywords - アブストラクトに含まれる")
try:
    entry = MagicMock()
    entry.title = "Nanoporous Materials Study"
    entry.summary = "This research focuses on clathrasil and its properties"
    
    result = match_keywords(entry)
    assert result is True, "キーワードマッチするべき"
    print("✓ アブストラクトのキーワード検出成功")
    print(f"  - キーワード: {KEYWORDS}")
    print(f"  - アブストラクト: {entry.summary}")
except Exception as e:
    print(f"✗ テスト失敗: {e}")

# テスト6: match_keywords - 大文字小文字区別なし
print("\n[テスト6] match_keywords - 大文字小文字区別なし")
try:
    entry = MagicMock()
    entry.title = "SILICA CLATHRATE structures"
    entry.summary = "Investigation of CLATHRASIL"
    
    result = match_keywords(entry)
    assert result is True, "大文字小文字区別なしでマッチするべき"
    print("✓ 大文字小文字区別なしでのマッチ成功")
except Exception as e:
    print(f"✗ テスト失敗: {e}")

# テスト7: match_keywords - キーワード未検出
print("\n[テスト7] match_keywords - キーワード未検出")
try:
    entry = MagicMock()
    entry.title = "Protein Folding Mechanisms"
    entry.summary = "A study on how proteins fold in cellular environments"
    
    result = match_keywords(entry)
    assert result is False, "キーワード未検出であるべき"
    print("✓ キーワード未検出を正しく判定")
except Exception as e:
    print(f"✗ テスト失敗: {e}")

# テスト8: 統合テスト - 最近かつキーワード一致
print("\n[テスト8] 統合テスト - 最近かつキーワード一致")
try:
    now = datetime.utcnow()
    recent_date = (now - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    entry = MagicMock()
    entry.published = recent_date
    entry.title = "Silica Clathrate Formation"
    entry.summary = "Study of structure"
    
    is_recent_result = is_recent(entry, days=3)
    match_keywords_result = match_keywords(entry)
    
    assert is_recent_result is True, "最近の論文であるべき"
    assert match_keywords_result is True, "キーワードマッチするべき"
    print("✓ 最近かつキーワード一致の論文を正しく判定")
except Exception as e:
    print(f"✗ テスト失敗: {e}")

# テスト9: 統合テスト - 最近だが キーワード不一致
print("\n[テスト9] 統合テスト - 最近だがキーワード不一致")
try:
    now = datetime.utcnow()
    recent_date = (now - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    entry = MagicMock()
    entry.published = recent_date
    entry.title = "Protein Studies"
    entry.summary = "Research on proteins"
    
    is_recent_result = is_recent(entry, days=3)
    match_keywords_result = match_keywords(entry)
    
    assert is_recent_result is True, "最近の論文であるべき"
    assert match_keywords_result is False, "キーワード不一致であるべき"
    print("✓ 最近だがキーワード不一致の論文を正しく判定")
except Exception as e:
    print(f"✗ テスト失敗: {e}")

print("\n" + "=" * 60)
print("✓ フィルタリング機能の基本テストが完了しました！")
print("=" * 60)

print("\n設定キーワード:")
for keyword in KEYWORDS:
    print(f"  - {keyword}")
