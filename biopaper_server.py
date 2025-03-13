# biopaper_server.py
import json
import asyncio
from typing import List, Dict, Optional, Any
import httpx
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP(
    "EPMCSearch",
    dependencies=["httpx", "pydantic"]
)

class Paper(BaseModel):
    """論文情報のモデル"""
    id: str
    title: str
    authors: str
    journal: Optional[str] = None
    publication_date: Optional[str] = None
    abstract: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    keywords: Optional[List[str]] = None
    pmid: Optional[str] = None
    citationCount: Optional[int] = None

@mcp.tool()
async def search_european_pmc(
    search_query: str, 
    max_results: int = 10, 
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Europe PMCを使用して生物学論文を検索。
    
    Parameters:
    ----------
    search_query : str
        EuropePMC APIに対する完全な検索クエリ。AND/OR演算子やフィールド指定（TITLE, ABSTRACT等）を含む。
        例: "(TITLE:\"virus\" OR TITLE:\"viral\") AND (ABSTRACT:\"metagenom*\") AND (FIRST_PDATE:[2020-01-01 TO 2025-12-31])"
    max_results : int
        返される論文の最大数
    
    Returns:
    -------
    Dict[str, Any]
        検索クエリと検索結果の論文リスト
    """
    # デバッグモード用のログ出力
    def log_info(message):
        if ctx:
            try:
                asyncio.create_task(ctx.info(message))
            except Exception as e:
                print(f"ログ出力エラー: {e}")
                print(f"INFO: {message}")
        else:
            print(f"INFO: {message}")
    
    log_info(f"Europe PMC検索実行: {search_query}")
    
    # Europe PMC APIを使って検索
    async with httpx.AsyncClient() as client:
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
        params = {
            "query": search_query,
            "format": "json",
            "resultType": "core",
            "pageSize": max_results + 10  # 余分に取得して後でフィルタリング
        }
        
        log_info(f"Europe PMC APIにリクエスト送信中...")
        response = await client.get(url, params=params)
        
        if response.status_code != 200:
            error_msg = f"APIエラー: {response.status_code}"
            log_info(error_msg)
            return {
                "search_query": search_query,
                "error": error_msg,
                "papers": []
            }
        
        data = response.json()
        results = data.get("resultList", {}).get("result", [])
        
        if not results:
            log_info("検索結果が見つかりませんでした。")
            return {
                "search_query": search_query,
                "message": "検索結果が見つかりませんでした。",
                "papers": []
            }
        
        # 結果を整形
        papers = []
        valid_papers_count = 0
        
        for i, paper in enumerate(results):
            # アブストラクトがない論文はスキップ
            abstract = paper.get("abstractText")
            if not abstract or len(abstract.strip()) < 50:  # 短すぎるアブストラクトも除外
                continue
                
            paper_info = {
                "id": paper.get("id", "N/A"),
                "title": paper.get("title", "タイトルなし"),
                "authors": paper.get("authorString", "著者情報なし"),
                "journal": paper.get("journalTitle", None),
                "publication_date": paper.get("firstPublicationDate", None),
                "abstract": abstract,
                "doi": paper.get("doi", None),
                "url": f"https://europepmc.org/article/{paper.get('source', 'MED')}/{paper.get('id', '')}" if paper.get('id') else None,
                "keywords": paper.get("keywordList", {}).get("keyword", []),
                "pmid": paper.get("pmid", None),
                "citationCount": paper.get("citationCount", 0)
            }
            
            papers.append(paper_info)
            valid_papers_count += 1
            
            # 十分な論文が集まったら終了
            if valid_papers_count >= max_results:
                break
        
        log_info(f"{len(papers)}件の論文が見つかりました。")
        return {
            "search_query": search_query,
            "papers": papers
        }

@mcp.prompt()
def search_biology_papers(topic: str) -> str:
    """
    生物学論文の検索プロンプトテンプレート
    """
    return f"""
あなたは生物学・医学研究のエキスパートです。以下のトピックに関連する最新の生物学研究論文を探し、解析してください。

ユーザーの質問: {topic}

以下のステップに従ってください:

1. 検索クエリの作成:
   - ユーザーの質問を分析し、Europe PMC APIで使用する適切な検索クエリを構築してください。
   - Europe PMC APIでは、以下の構文が使用できます:
     * フィールド指定: TITLE, ABSTRACT, AUTHOR, etc.
     * 論理演算子: AND, OR, NOT
     * 句の検索: "引用符で囲む"
     * 日付範囲: FIRST_PDATE:[YYYY-MM-DD TO YYYY-MM-DD]
     * 注意: ワイルドカード "*" は使用できません。完全な単語を使用してください。
     * 例: (TITLE:"virus" OR ABSTRACT:"viral") AND (ABSTRACT:"metagenome" OR ABSTRACT:"metagenomic") AND (FIRST_PDATE:[2020-01-01 TO 2025-12-31])
   - 検索を特定の論文タイプに制限するには: (SRC:MED OR SRC:PMC)を追加（査読済み論文）
   - 専門的で詳細な検索クエリを作成し、それが何をなぜ検索しているかを説明してください。

2. 論文検索の実行:
   - 作成した検索クエリを使用して、search_european_pmc ツールで検索を実行してください。
   - 検索結果から、アブストラクトが含まれる質の高い論文を分析してください。

3. 結果の統合と回答の作成:
   - 検索結果の論文を統合して分析し、ユーザーの質問に対する包括的な回答を作成してください。
   - 回答には以下を含めてください:
     * 主要な方法論とアプローチの比較
     * 主な研究成果と現在のコンセンサス
     * 実際の応用例
     * 今後の研究方向
     * 相反する見解や方法論がある場合は、それらを比較
   - 文中では論文を引用する際に著者名と年号（例：Smith et al., 2023）を使用してください。
   - 回答は科学的に正確で、専門的かつ理解しやすいものにしてください。

4. 検索方法の説明:
   - 使用した検索クエリとその構築理由を簡潔に説明してください。

5. 参考文献リスト:
   - 回答の最後に必ず「参考文献」セクションを作成し、引用したすべての論文の完全な情報を含めてください。
   - 各論文の情報は次の形式で記載してください：
     * 著者 (年). タイトル. ジャーナル名, 巻(号), ページ. DOI: xxx
   - DOIがある場合は必ず含めてください。
   - 引用番号や参照番号を付けると、本文からの参照が容易になります。

回答は、日本語で、科学的に正確で、最新の研究に基づいたものにしてください。
"""

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "debug":
        # デバッグモード - テスト用のコードを実行
        async def test_search():
            print("テスト検索を実行中...")
            
            test_query = '(TITLE:"virus" OR TITLE:"viral") AND (ABSTRACT:"metagenome") AND (FIRST_PDATE:[2020-01-01 TO 2025-12-31])'
            print(f"検索クエリ: {test_query}")
            
            # Contextなしで直接実行
            results = await search_european_pmc(test_query, 3)
            print(f"検索結果: {len(results['papers'])} 件")
            
            for i, paper in enumerate(results['papers']):
                print(f"\n論文 {i+1}:")
                print(f"タイトル: {paper['title']}")
                print(f"著者: {paper['authors']}")
                print(f"URL: {paper.get('url', 'なし')}")
                print(f"アブストラクト: {paper['abstract'][:100]}...")
                print("---")
        
        import asyncio
        asyncio.run(test_search())
    else:
        # 通常の実行
        mcp.run()