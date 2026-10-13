# アーキテクチャとエンジニアリングガイド

## 設計

このリポジトリは、1つのインストール可能なパッケージと薄いアプリケーション
境界で構成します。

```text
CLI（Typer、設定、ログ） -> コアロジック
```

`src/template_python/core.py` は、環境変数、ログ、CLIの副作用を持たない決定的な
処理を担当します。`cli.py` が設定とログを構成し、コアを呼び出します。再利用
可能な処理は目的が明確なモジュールへ置き、インフラ要素は境界に留めます。

`utils` や `common`、基底クラス階層、サービスロケータ、DIフレームワークは
避けます。複数の具体的な利用箇所で同じ安定した要求が確認できてから共通化します。

## Source of truth

| 対象 | Source |
| --- | --- |
| メタデータ、依存関係、ツール設定 | `pyproject.toml` |
| 解決済み依存関係 | `uv.lock` |
| ローカルとCIのコマンド | `Makefile` |
| 対応Python | `pyproject.toml` と `test.yaml` |
| コンテナ動作 | `Dockerfile` と `compose.yml` |
| ドキュメント構成 | `mkdocs.yml` |

`uv.lock` をコミットし、コマンドは `--locked` を使用します。
`pyproject.toml` と `uv.lock` は同時に更新します。

## ランタイムのルール

- パッケージのimport時にログ設定や環境変数読み込みを行いません。
- コア関数は値を返すか具体的な例外を送出し、CLIが表示と終了コードへ変換します。
- `ProjectSettings` が `PROJECT_*` と任意の `.env` を一元管理します。
- root loggerの設定はCLI callbackで一度だけ行います。
- CLIは `[project.scripts]` で公開し、`python -m template_python` も維持します。

## 品質ゲート

```shell
make ci-test
make ci-test-docs
```

Ruff、mypy strict、actionlint、zizmor、branch coverage付きpytest、wheel/sdistの
smoke testを実行します。各対応Pythonでは互換性テストを行います。Git hookは
`make hooks-check` で別途検証します。

同じ責務のツールを追加する場合は既存ツールを置き換えるか、測定可能な不足を
文書化してください。

## 配布

- Pull Requestと対象ブランチでPythonとコンテナを検証します。
- `main` からGitHub Pagesへ英日ドキュメントを公開します。
- `v*` tagからDocker HubとGHCRへmulti-platform imageを公開します。
- GHCR imageにはpush済みdigestに対するprovenanceを付与します。
- Azure Static Web Appsは手動デプロイを維持します。

Actionはcommit SHAで固定し、Workflowは最小権限、checkout credential無効化、
timeoutを使用します。自動キャンセルはrelease以外に限定します。

## 任意アセット

Notebook、ドキュメント、コンテナ、registry、Azure、Dev Containerは独立した
サンプルです。別のアプリケーション動作を作らず、インストール済みパッケージを
利用します。削除時は依存関係、コマンド、Workflow、説明も同時に削除します。

多言語出力がMkDocs 1のplugin ecosystemに依存する間、MkDocsは2未満に固定します。

## 変更チェックリスト

1. コアを決定的に保ち、アプリケーション要素を境界へ置く。
2. 出力、エラー、CLI終了コード、設定のテストを追加する。
3. `pyproject.toml` と `uv.lock` を同時に更新する。
4. CIからMake targetを再利用する。
5. 英語と日本語のドキュメントを同時に更新する。
6. `make ci-test` と `make ci-test-docs` を実行する。
7. コンテナ変更時はDocker検証を実行する。
8. release前に配布物と依存グラフを確認する。
