"""
arXiv論文収集モジュール
arXivから論文情報を取得・フィルタリングする機能を提供します
"""
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from config_loader import load_config, get_filter_config, get_search_config

# デフォルトキーワード設定（config.json がない場合）
DEFAULT_KEYWORDS = ["silica clathrate", "clathrasil"]

# グローバル: 現在のキーワード設定
KEYWORDS = DEFAULT_KEYWORDS


def load_keywords_from_config(config=None):
    """
    config.json からキーワードを読み込み、グローバル KEYWORDS を更新
    
    Args:
        config (dict): config_loader.load_config() から取得した設定。
                      None の場合はファイルから読み込む
    
    Returns:
        list: 読み込んだキーワードリスト
    """
    global KEYWORDS
    try:
        if config is None:
            config = load_config()
        filter_config = get_filter_config(config)
        KEYWORDS = filter_config.get("keywords", DEFAULT_KEYWORDS)
        return KEYWORDS
    except Exception:
        # config.json 読み込みエラーの場合はデフォルト値を使用
        KEYWORDS = DEFAULT_KEYWORDS
        return KEYWORDS


def is_recent(entry, days=3):
    """
    論文が指定日数以内に公開されたかチェック
    
    Args:
        entry: arXiv entry オブジェクト（published属性を含む）
               または published_date 文字列を持つオブジェクト
        days (int): 何日以内とするか（デフォルト：3日）
    
    Returns:
        bool: 指定日数以内に公開された場合 True、そうでない場合 False
    """
    try:
        # entry が持つ published 属性を取得
        if hasattr(entry, 'published'):
            date_str = entry.published
        elif hasattr(entry, 'published_date'):
            date_str = entry.published_date
        else:
            raise AttributeError("Entry has no 'published' or 'published_date' attribute")
        
        published = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return published >= cutoff_date
    except (AttributeError, ValueError, TypeError) as e:
        raise ValueError(f"Failed to parse publication date: {e}")


def match_keywords(entry):
    """
    論文がキーワードと一致するかチェック
    
    Args:
        entry: arXiv entry オブジェクト（title, summary 属性を含む）
               または title, abstract フィールドを持つオブジェクト
    
    Returns:
        bool: キーワードと一致した場合 True、そうでない場合 False
    """
    try:
        # 異なる属性名に対応
        if hasattr(entry, 'title'):
            title = entry.title if entry.title else ""
        else:
            title = ""
        
        if hasattr(entry, 'summary'):
            summary = entry.summary if entry.summary else ""
        elif hasattr(entry, 'abstract'):
            summary = entry.abstract if entry.abstract else ""
        else:
            summary = ""
        
        # スペースを正規化（複数スペースを単一スペースに）
        text = (title + " " + summary).lower()
        text = " ".join(text.split())  # スペースを正規化
        return any(k.lower() in text for k in KEYWORDS)
    except (AttributeError, TypeError) as e:
        raise ValueError(f"Failed to match keywords: {e}")


def fetch_arxiv_papers(query=None, max_results=None, config=None):
    """
    arXivから論文を取得する
    
    Args:
        query (str): 検索クエリ（例："silica clathrate"）。
                    None の場合は config.json から読み込む
        max_results (int): 取得する最大論文数。
                          None の場合は config.json から読み込む（デフォルト：100）
        config (dict): config_loader.load_config() から取得した設定。
                      None の場合はファイルから読み込む
    
    Returns:
        list: 論文情報のリスト
        各論文は以下のフィールドを含む辞書：
        - title: 論文タイトル
        - authors: 著者リスト
        - abstract: アブストラクト
        - published_date: 公開日時
        - url: arXiv URL
        - source: ソース名（'arXiv'）
        - doi, keywords, journal, volume, issue, pages: その他の情報
    
    Raises:
        ConnectionError: arXiv API 接続エラー
        ValueError: XML 解析エラーまたはクエリが未設定
    """
    # config から query と max_results を読み込む
    if query is None or max_results is None:
        try:
            if config is None:
                config = load_config()
            search_config = get_search_config(config)
            if query is None:
                query = search_config.get("query")
            if max_results is None:
                max_results = search_config.get("max_results", 100)
        except Exception:
            # config.json が使用不可の場合
            if query is None:
                raise ValueError("query parameter is required when config.json is not available")
            if max_results is None:
                max_results = 5
    
    ARXIV_NS = '{http://www.w3.org/2005/Atom}'
    base_url = f'http://export.arxiv.org/api/query?search_query={query}&start=0&max_results={max_results}'
    
    try:
        response = requests.get(base_url)
        response.raise_for_status()
    except requests.RequestException as e:
        raise ConnectionError(f"Failed to connect to arXiv API: {e}")
    
    try:
        root = ET.fromstring(response.text)
    except ET.ParseError as e:
        raise ValueError(f"Failed to parse XML response: {e}")
    
    papers = []
    for entry in root.findall(f'{ARXIV_NS}entry'):
        # タイトルを取得
        title_elem = entry.find(f'{ARXIV_NS}title')
        title = title_elem.text if title_elem is not None else ''
        
        # アブストラクトを取得
        summary_elem = entry.find(f'{ARXIV_NS}summary')
        summary = summary_elem.text if summary_elem is not None else ''
        
        # URLを取得
        url_elem = entry.find(f'{ARXIV_NS}id')
        url = url_elem.text if url_elem is not None else ''
        
        # 公開日を取得
        published_elem = entry.find(f'{ARXIV_NS}published')
        published_date = None
        if published_elem is not None and published_elem.text and published_elem.text.strip():
            published_date = published_elem.text
        
        # 著者を取得
        authors = []
        for author in entry.findall(f'{ARXIV_NS}author'):
            name_elem = author.find(f'{ARXIV_NS}name')
            if name_elem is not None and name_elem.text:
                authors.append(name_elem.text)
        
        paper = {
            'title': title,
            'authors': authors,
            'abstract': summary,
            'published_date': published_date,
            'doi': None,
            'url': url,
            'source': 'arXiv',
            'keywords': [],
            'journal': None,
            'volume': None,
            'issue': None,
            'pages': None
        }
        papers.append(paper)
    
    return papers
