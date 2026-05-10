"""
arXiv論文収集機能のテスト
collecting.py のテストと検証
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../scripts'))

from collecting import fetch_arxiv_papers


class TestFetchArxivPapers:
    """fetch_arxiv_papers関数のテスト"""
    
    def test_fetch_with_default_max_results(self):
        """デフォルトmax_results=5で論文を取得することをテスト"""
        # モック用のXMLレスポンス
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
        
        with patch('collecting.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = mock_xml
            mock_get.return_value = mock_response
            
            papers = fetch_arxiv_papers('silica clathrate')
            assert isinstance(papers, list)
            assert len(papers) == 1
            mock_get.assert_called_once()
            assert 'max_results=5' in mock_get.call_args[0][0]
    
    def test_fetch_with_custom_max_results(self):
        """カスタムmax_resultsで論文を取得することをテスト"""
        mock_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <id>http://arxiv.org/abs/2026.12345v1</id>
                <title>Silica Clathrate</title>
                <summary>Summary</summary>
                <published>2026-05-06T10:00:00Z</published>
                <author><name>Author A</name></author>
            </entry>
        </feed>'''
        
        with patch('collecting.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = mock_xml
            mock_get.return_value = mock_response
            
            papers = fetch_arxiv_papers('test', max_results=10)
            assert 'max_results=10' in mock_get.call_args[0][0]
    
    def test_paper_data_structure(self):
        """返された論文データの構造が正しいことをテスト"""
        mock_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <id>http://arxiv.org/abs/2026.99999v1</id>
                <title>Test Paper Title</title>
                <summary>Test abstract content</summary>
                <published>2026-05-06T12:34:56Z</published>
                <author><name>John Smith</name></author>
                <author><name>Jane Doe</name></author>
            </entry>
        </feed>'''
        
        with patch('collecting.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = mock_xml
            mock_get.return_value = mock_response
            
            papers = fetch_arxiv_papers('query')
            paper = papers[0]
            
            # 必須フィールドの確認
            assert 'title' in paper
            assert 'authors' in paper
            assert 'abstract' in paper
            assert 'published_date' in paper
            assert 'url' in paper
            assert 'source' in paper
            assert paper['source'] == 'arXiv'
    
    def test_paper_title_extracted_correctly(self):
        """論文タイトルが正しく抽出されることをテスト"""
        mock_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <id>http://arxiv.org/abs/2026.11111v1</id>
                <title>Silica Clathrate Formation in Nanoporous Materials</title>
                <summary>Abstract</summary>
                <published>2026-05-06T10:00:00Z</published>
                <author><name>Author</name></author>
            </entry>
        </feed>'''
        
        with patch('collecting.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = mock_xml
            mock_get.return_value = mock_response
            
            papers = fetch_arxiv_papers('query')
            assert papers[0]['title'] == 'Silica Clathrate Formation in Nanoporous Materials'
    
    def test_paper_abstract_extracted_correctly(self):
        """論文アブストラクトが正しく抽出されることをテスト"""
        mock_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <id>http://arxiv.org/abs/2026.22222v1</id>
                <title>Title</title>
                <summary>This is the detailed abstract content of the paper.</summary>
                <published>2026-05-06T10:00:00Z</published>
                <author><name>Author</name></author>
            </entry>
        </feed>'''
        
        with patch('collecting.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = mock_xml
            mock_get.return_value = mock_response
            
            papers = fetch_arxiv_papers('query')
            assert papers[0]['abstract'] == 'This is the detailed abstract content of the paper.'
    
    def test_paper_url_extracted_correctly(self):
        """論文URLが正しく抽出されることをテスト"""
        mock_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <id>http://arxiv.org/abs/2026.33333v1</id>
                <title>Title</title>
                <summary>Abstract</summary>
                <published>2026-05-06T10:00:00Z</published>
                <author><name>Author</name></author>
            </entry>
        </feed>'''
        
        with patch('collecting.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = mock_xml
            mock_get.return_value = mock_response
            
            papers = fetch_arxiv_papers('query')
            assert papers[0]['url'] == 'http://arxiv.org/abs/2026.33333v1'
    
    def test_paper_published_date_extracted_correctly(self):
        """論文公開日が正しく抽出されることをテスト"""
        mock_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <id>http://arxiv.org/abs/2026.44444v1</id>
                <title>Title</title>
                <summary>Abstract</summary>
                <published>2026-05-06T14:30:45Z</published>
                <author><name>Author</name></author>
            </entry>
        </feed>'''
        
        with patch('collecting.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = mock_xml
            mock_get.return_value = mock_response
            
            papers = fetch_arxiv_papers('query')
            assert papers[0]['published_date'] == '2026-05-06T14:30:45Z'
    
    def test_paper_authors_extracted_correctly(self):
        """複数の著者が正しく抽出されることをテスト"""
        mock_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <id>http://arxiv.org/abs/2026.55555v1</id>
                <title>Title</title>
                <summary>Abstract</summary>
                <published>2026-05-06T10:00:00Z</published>
                <author><name>John Doe</name></author>
                <author><name>Jane Smith</name></author>
                <author><name>Bob Johnson</name></author>
            </entry>
        </feed>'''
        
        with patch('collecting.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = mock_xml
            mock_get.return_value = mock_response
            
            papers = fetch_arxiv_papers('query')
            assert isinstance(papers[0]['authors'], list)
            assert len(papers[0]['authors']) == 3
            assert 'John Doe' in papers[0]['authors']
            assert 'Jane Smith' in papers[0]['authors']
            assert 'Bob Johnson' in papers[0]['authors']
    
    def test_multiple_papers_extracted(self):
        """複数の論文が正しく抽出されることをテスト"""
        mock_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <id>http://arxiv.org/abs/2026.66666v1</id>
                <title>Paper 1</title>
                <summary>Abstract 1</summary>
                <published>2026-05-06T10:00:00Z</published>
                <author><name>Author 1</name></author>
            </entry>
            <entry>
                <id>http://arxiv.org/abs/2026.77777v1</id>
                <title>Paper 2</title>
                <summary>Abstract 2</summary>
                <published>2026-05-06T11:00:00Z</published>
                <author><name>Author 2</name></author>
            </entry>
        </feed>'''
        
        with patch('collecting.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = mock_xml
            mock_get.return_value = mock_response
            
            papers = fetch_arxiv_papers('query', max_results=2)
            assert len(papers) == 2
            assert papers[0]['title'] == 'Paper 1'
            assert papers[1]['title'] == 'Paper 2'
    
    def test_empty_author_list_handling(self):
        """著者がない場合は空リストになることをテスト"""
        mock_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <id>http://arxiv.org/abs/2026.88888v1</id>
                <title>Title</title>
                <summary>Abstract</summary>
                <published>2026-05-06T10:00:00Z</published>
            </entry>
        </feed>'''
        
        with patch('collecting.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = mock_xml
            mock_get.return_value = mock_response
            
            papers = fetch_arxiv_papers('query')
            assert isinstance(papers[0]['authors'], list)
    
    def test_empty_published_date_handling(self):
        """published_dateが空の場合はNoneになることをテスト"""
        mock_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <id>http://arxiv.org/abs/2026.99999v1</id>
                <title>Title</title>
                <summary>Abstract</summary>
                <published></published>
                <author><name>Author</name></author>
            </entry>
        </feed>'''
        
        with patch('collecting.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = mock_xml
            mock_get.return_value = mock_response
            
            papers = fetch_arxiv_papers('query')
            assert papers[0]['published_date'] is None
    
    def test_network_error_handling(self):
        """ネットワークエラー時に例外が発生することをテスト"""
        with patch('collecting.requests.get') as mock_get:
            mock_get.side_effect = ConnectionError("Network error")
            
            with pytest.raises(ConnectionError):
                fetch_arxiv_papers('query')
    
    def test_no_results_returns_empty_list(self):
        """検索結果がない場合は空リストを返すことをテスト"""
        mock_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
        </feed>'''
        
        with patch('collecting.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = mock_xml
            mock_get.return_value = mock_response
            
            papers = fetch_arxiv_papers('nonexistent_keyword')
            assert papers == []
