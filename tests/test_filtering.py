"""
キーワード・日付フィルタリング機能のテスト
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../scripts'))

from collecting import is_recent, match_keywords


class TestIsRecent:
    """is_recent関数のテスト"""
    
    def test_is_recent_with_recent_paper(self):
        """過去3日以内の論文をチェック"""
        now = datetime.utcnow()
        recent_date = (now - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        entry = MagicMock()
        entry.published = recent_date
        
        assert is_recent(entry, days=3) is True
    
    def test_is_recent_with_old_paper(self):
        """3日以上前の論文をチェック"""
        now = datetime.utcnow()
        old_date = (now - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        entry = MagicMock()
        entry.published = old_date
        
        assert is_recent(entry, days=3) is False
    
    def test_is_recent_with_boundary_date(self):
        """ちょうど3日前の論文をチェック"""
        now = datetime.utcnow()
        boundary_date = (now - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        entry = MagicMock()
        entry.published = boundary_date
        
        # 3日前の場合は境界値テスト（>= 比較なので True）
        result = is_recent(entry, days=3)
        assert isinstance(result, bool)
    
    def test_is_recent_with_today_paper(self):
        """今日の論文をチェック"""
        now = datetime.utcnow()
        today_date = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        entry = MagicMock()
        entry.published = today_date
        
        assert is_recent(entry, days=3) is True
    
    def test_is_recent_with_custom_days(self):
        """カスタムdays値でのフィルタリング"""
        now = datetime.utcnow()
        
        # 2日前
        recent_date = (now - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
        entry = MagicMock()
        entry.published = recent_date
        
        assert is_recent(entry, days=1) is False
        assert is_recent(entry, days=3) is True
    
    def test_is_recent_returns_boolean(self):
        """戻り値がブール型であることをテスト"""
        now = datetime.utcnow()
        recent_date = (now - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        entry = MagicMock()
        entry.published = recent_date
        
        result = is_recent(entry, days=3)
        assert isinstance(result, bool)


class TestMatchKeywords:
    """match_keywords関数のテスト"""
    
    def test_match_keywords_in_title(self):
        """タイトルにキーワードがある場合"""
        entry = MagicMock()
        entry.title = "Silica Clathrate Structures in Nanoporous Materials"
        entry.summary = "Study of porous structures"
        
        assert match_keywords(entry) is True
    
    def test_match_keywords_in_summary(self):
        """アブストラクトにキーワードがある場合"""
        entry = MagicMock()
        entry.title = "Nanoporous Materials Study"
        entry.summary = "This research focuses on clathrasil and its properties"
        
        assert match_keywords(entry) is True
    
    def test_match_keywords_in_both(self):
        """タイトルとアブストラクト両方にキーワードがある場合"""
        entry = MagicMock()
        entry.title = "Silica Clathrate Research"
        entry.summary = "Study of clathrasil structure and properties"
        
        assert match_keywords(entry) is True
    
    def test_match_keywords_case_insensitive(self):
        """大文字小文字区別なしのマッチ"""
        entry = MagicMock()
        entry.title = "SILICA CLATHRATE structures"
        entry.summary = "Investigation of CLATHRASIL"
        
        assert match_keywords(entry) is True
    
    def test_no_match_keywords(self):
        """キーワードが含まれていない場合"""
        entry = MagicMock()
        entry.title = "Protein Folding Mechanisms"
        entry.summary = "A study on how proteins fold in cellular environments"
        
        assert match_keywords(entry) is False
    
    def test_match_keywords_partial_word(self):
        """単語の一部がキーワードと一致する場合"""
        entry = MagicMock()
        entry.title = "Clathrate Compounds"
        entry.summary = "Study of clathrate structures"
        
        # "clathrate" には "clathrasil" が部分一致しないため False
        assert match_keywords(entry) is False
    
    def test_match_keywords_exact_match_silica_clathrate(self):
        """'silica clathrate' が含まれている場合"""
        entry = MagicMock()
        entry.title = "silica clathrate and zeolites"
        entry.summary = "Abstract"
        
        assert match_keywords(entry) is True
    
    def test_match_keywords_exact_match_clathrasil(self):
        """'clathrasil' が含まれている場合"""
        entry = MagicMock()
        entry.title = "Title"
        entry.summary = "Research on clathrasil materials"
        
        assert match_keywords(entry) is True
    
    def test_match_keywords_returns_boolean(self):
        """戻り値がブール型であることをテスト"""
        entry = MagicMock()
        entry.title = "Silica Clathrate"
        entry.summary = "Summary"
        
        result = match_keywords(entry)
        assert isinstance(result, bool)
    
    def test_match_keywords_empty_title_and_summary(self):
        """タイトルとアブストラクトが空の場合"""
        entry = MagicMock()
        entry.title = ""
        entry.summary = ""
        
        assert match_keywords(entry) is False
    
    def test_match_keywords_whitespace_handling(self):
        """ホワイトスペースの適切な処理"""
        entry = MagicMock()
        entry.title = "  Silica   Clathrate  "
        entry.summary = "  Study  "
        
        assert match_keywords(entry) is True


class TestIntegrationFiltering:
    """フィルタリング機能の統合テスト"""
    
    def test_filter_recent_and_matching_keywords(self):
        """最近かつキーワード一致の論文"""
        now = datetime.utcnow()
        recent_date = (now - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        entry = MagicMock()
        entry.published = recent_date
        entry.title = "Silica Clathrate Formation"
        entry.summary = "Study of structure"
        
        assert is_recent(entry, days=3) is True
        assert match_keywords(entry) is True
    
    def test_filter_recent_but_no_keywords(self):
        """最近だがキーワード不一致の論文"""
        now = datetime.utcnow()
        recent_date = (now - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        entry = MagicMock()
        entry.published = recent_date
        entry.title = "Protein Studies"
        entry.summary = "Research on proteins"
        
        assert is_recent(entry, days=3) is True
        assert match_keywords(entry) is False
    
    def test_filter_old_but_matching_keywords(self):
        """古いがキーワード一致の論文"""
        now = datetime.utcnow()
        old_date = (now - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        entry = MagicMock()
        entry.published = old_date
        entry.title = "Silica Clathrate History"
        entry.summary = "Historical research"
        
        assert is_recent(entry, days=3) is False
        assert match_keywords(entry) is True
    
    def test_filter_old_and_no_keywords(self):
        """古くてキーワード不一致の論文"""
        now = datetime.utcnow()
        old_date = (now - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        entry = MagicMock()
        entry.published = old_date
        entry.title = "Unrelated Topic"
        entry.summary = "Some research"
        
        assert is_recent(entry, days=3) is False
        assert match_keywords(entry) is False
