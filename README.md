# Europe PMC論文検索 MCP サービス

生物学論文検索のための Claude Desktop MCP サービス

</div>

## 概要

このリポジトリは、[Europe PMC](https://europepmc.org/) APIを利用して生物学論文を検索・分析するためのModel Context Protocol (MCP) サーバーを提供します。Claude Desktopと統合することで、以下のような特徴を持つ強力な論文検索アシスタントとして機能します：

- **日本語での生物学論文検索**: 専門的な生物学の質問を日本語で入力し、関連する英語論文を検索・分析
- **高度な検索クエリ構築**: Claudeが質問内容を分析し、最適な検索クエリを自動生成
- **包括的な結果分析**: 単なる論文リストではなく、関連研究の統合された分析を提供
- **参考文献リスト生成**: 引用された論文の完全な情報を含む参考文献リストを生成

## 必要条件

- [Claude Desktop](https://claude.ai/download) (開発者機能有効)
- [Miniforge](https://github.com/conda-forge/miniforge) または Miniconda/Anaconda

## インストール手順

### 1. リポジトリのクローン

```bash
git clone https://github.com/yourusername/biopaper-mcp-search.git
cd biopaper-mcp-search
```

### 2. Miniforge による環境構築

```bash
# バイオ論文検索用の新しい環境を作成
conda create -n biopaper-mcp python=3.10
conda activate biopaper-mcp

# 必要なパッケージをインストール
pip install mcp httpx pydantic
```

### 3. 動作確認（オプション）

デバッグモードでサーバーの動作を確認できます：

```bash
python biopaper_server.py debug
```

正常に動作すれば、テスト検索が実行され、Europe PMC からの検索結果が表示されます。

## Claude Desktop への統合

環境が正しく設定されていることを確認し、次のコマンドでサーバーをインストールします：

```bash
conda activate biopaper-mcp
mcp install biopaper_server.py --name "EPMCSearch"
```

Claude Desktop の設定ファイルを直接編集します：

1. Claude Desktop を起動します
2. メニューバー（macOSの場合）から「Claude」→「Settings」→「Developer」→「Edit Config」を選択します
3. 表示された `claude_desktop_config.json` に以下のような設定を追加あるいは変更します（パスは環境に合わせて調整してください）：

```json
{
  "mcpServers": {
    "EPMCSearch": {
      "command": "/path/to/your/anaconda3/envs/biopaper-mcp/bin/python",
      "args": [
        "/path/to/your/biopaper-mcp-search/biopaper_server.py"
      ],
      "env": {
        "PATH": "/path/to/your/anaconda3/envs/biopaper-mcp/bin:${PATH}"
      }
    }
  }
}
```

例：

```json
{
  "mcpServers": {
    "EPMCSearch": {
      "command": "/Users/username/anaconda3/envs/biopaper-mcp/bin/python",
      "args": [
        "/Users/username/projects/biopaper-mcp-search/biopaper_server.py"
      ],
      "env": {
        "PATH": "/Users/username/anaconda3/envs/biopaper-mcp/bin:${PATH}"
      }
    }
  }
}
```

4. 設定を保存し、Claude Desktop を再起動します

## 使用方法

1. Claude Desktop を起動します
2. 新しい会話を開始し、入力ボックス下の"Attach from MCP"から「EPMCSearch」を選択します
3. 生物学に関する質問を日本語で入力します

例えば：

```
環境メタゲノムデータからウイルスゲノムを同定・再構築するための最新のバイオインフォマティクスアプローチとその検証方法について教えてください。
```

または：

```
微生物間の遺伝子水平伝播がマイクロバイオーム機能に与える影響を実験的に証明した例とその方法論について知りたいです。
```

Claudeは自動的に：
1. 質問を分析して適切な検索クエリを構築
2. Europe PMC APIで関連論文を検索
3. 検索結果を統合・分析
4. 包括的な回答と参考文献リストを生成

## トラブルシューティング

### サーバーが表示されない

- Claude Desktop で開発者モードが有効になっているか確認してください
- 設定ファイルのパスが正しいか確認してください
- Miniforge 環境に必要なパッケージがすべてインストールされているか確認してください

### 検索結果がない

- より一般的な用語や別の表現で質問してみてください
- 検索対象を特定の年代に絞るなど、質問を具体化してみてください

### エラーが発生する場合

- Miniforge 環境が正しく設定されているか確認してください
- httpx や pydantic などの依存ライブラリが正しくインストールされているか確認してください

## カスタマイズ

`biopaper_server.py` を編集することで、サーバーの動作をカスタマイズできます：

- 検索パラメータの調整
- 追加のフィルタリングロジックの実装
- 別の学術データベースの統合

## ライセンス

MIT

## 参考

- [Europe PMC](https://europepmc.org/) - 無料で公開されている生命科学文献データベース
- [Model Context Protocol](https://modelcontextprotocol.io/) - LLMとのコンテキスト共有のための標準プロトコル
- [Claude](https://claude.ai/) - このプロジェクトで使用されているAIアシスタント