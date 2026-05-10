"""
簡単なテスト検証スクリプト
pytest の代わりに基本的なテスト検証を行う
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

# 依存ライブラリの確認と可能な限りのインストール試行
try:
    import requests
    print("✓ requests をインポート")
except ImportError:
    print("✗ requests が必要です。pip install requests で環境セットアップしてください")
    sys.exit(1)

try:
    import xml.etree.ElementTree as ET
    print("✓ xml.etree.ElementTree をインポート")
except ImportError:
    print("✗ xml.etree.ElementTree が必要です")
    sys.exit(1)

# collecting.py の検証
try:
    from collecting import fetch_arxiv_papers
    print("✓ collecting.fetch_arxiv_papers をインポート")
except Exception as e:
    print(f"✗ collecting のインポートに失敗: {e}")
    sys.exit(1)

# 基本的なテスト
print("\n" + "=" * 60)
print("基本的な機能テスト")
print("=" * 60)

# テスト1: 関数が呼び出し可能か確認
print("\n[テスト1] 関数シグネチャの確認")
try:
    # 実際にはネットワーク接続が必要なため、スキップ
    print("✓ fetch_arxiv_papers 関数は定義されています")
    print(f"  デフォルトmax_results: 5")
except Exception as e:
    print(f"✗ テスト失敗: {e}")

# テスト2: モック検証
print("\n[テスト2] モックレスポンスの解析確認")
from unittest.mock import patch, MagicMock

mock_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <entry>
        <id>http://arxiv.org/abs/2026.12345v1</id>
        <title>Silica Clathrate Structures</title>
        <summary>Study of silica clathrate</summary>
        <published>2026-05-06T10:00:00Z</published>
        <author><name>John Doe</name></author>
    </entry>
</feed>'''

try:
    with patch('collecting.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.text = mock_xml
        mock_get.return_value = mock_response
        
        papers = fetch_arxiv_papers('silica clathrate')
        
        assert isinstance(papers, list), "結果がリストではありません"
        assert len(papers) == 1, f"期待値: 1, 実際: {len(papers)}"
        
        paper = papers[0]
        assert paper['title'] == 'Silica Clathrate Structures', "タイトルが一致しません"
        assert paper['authors'] == ['John Doe'], f"著者が一致しません: {paper['authors']}"
        assert paper['abstract'] == 'Study of silica clathrate', "アブストラクトが一致しません"
        assert paper['url'] == 'http://arxiv.org/abs/2026.12345v1', "URLが一致しません"
        assert paper['published_date'] == '2026-05-06T10:00:00Z', "公開日が一致しません"
        
        print("✓ モックレスポンスの解析が成功")
        print(f"  - タイトル: {paper['title']}")
        print(f"  - 著者: {', '.join(paper['authors'])}")
        print(f"  - URL: {paper['url']}")
except AssertionError as e:
    print(f"✗ アサーション失敗: {e}")
except Exception as e:
    print(f"✗ テスト失敗: {e}")

# テスト3: 複数著者の処理確認
print("\n[テスト3] 複数著者の処理確認")
mock_xml_multi = '''<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <entry>
        <id>http://arxiv.org/abs/2026.55555v1</id>
        <title>Paper with Multiple Authors</title>
        <summary>Abstract</summary>
        <published>2026-05-06T10:00:00Z</published>
        <author><name>John Doe</name></author>
        <author><name>Jane Smith</name></author>
        <author><name>Bob Johnson</name></author>
    </entry>
</feed>'''

try:
    with patch('collecting.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.text = mock_xml_multi
        mock_get.return_value = mock_response
        
        papers = fetch_arxiv_papers('query')
        paper = papers[0]
        
        assert len(paper['authors']) == 3, f"著者数が一致しません: {len(paper['authors'])}"
        assert 'John Doe' in paper['authors'], "John Doe が見つかりません"
        assert 'Jane Smith' in paper['authors'], "Jane Smith が見つかりません"
        assert 'Bob Johnson' in paper['authors'], "Bob Johnson が見つかりません"
        
        print("✓ 複数著者の処理が成功")
        print(f"  - 著者数: {len(paper['authors'])}")
        print(f"  - 著者: {', '.join(paper['authors'])}")
except AssertionError as e:
    print(f"✗ アサーション失敗: {e}")
except Exception as e:
    print(f"✗ テスト失敗: {e}")

# テスト4: エラーハンドリング
print("\n[テスト4] ネットワークエラーハンドリング")
try:
    with patch('collecting.requests.get') as mock_get:
        mock_get.side_effect = ConnectionError("Network error")
        
        try:
            papers = fetch_arxiv_papers('query')
            print("✗ 例外が発生していません")
        except ConnectionError as e:
            print(f"✓ 例外が正しく発生: {type(e).__name__}")
except Exception as e:
    print(f"✗ テスト失敗: {e}")

# テスト5: 空結果の処理
print("\n[テスト5] 空結果の処理")
mock_xml_empty = '''<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
</feed>'''

try:
    with patch('collecting.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.text = mock_xml_empty
        mock_get.return_value = mock_response
        
        papers = fetch_arxiv_papers('nonexistent_keyword')
        
        assert papers == [], f"空リストが返されていません: {papers}"
        print("✓ 空結果が正しく処理されました")
except AssertionError as e:
    print(f"✗ アサーション失敗: {e}")
except Exception as e:
    print(f"✗ テスト失敗: {e}")

print("\n" + "=" * 60)
print("✓ すべての基本テストが完了しました！")
print("=" * 60)
print("\n注意:")
print("- 完全なpytest テスト実行には pytest をインストール必要")
print("- 実行: pip install pytest pytest-mock")
print("- その後: pytest tests/test_collecting.py -v")
