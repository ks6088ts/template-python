# template-python

`template-python` は、Python 3.12+ 向けの最小限のパッケージ兼 CLI
テンプレートです。

```shell
make install-deps-dev
make ci-test
uv run template-python hello --name Ada
```

`src/` layout、インストール可能な Typer CLI、`PROJECT_*` 設定を検証する
Pydantic Settings、フォーマットとLintを担うRuff、strictな型検査を担うmypy、
契約テストを担うpytestを採用しています。

Docker/Compose、英日MkDocs、Jupyter Notebook、Dev Container、Docker Hubと
GHCRへの公開、Azure Static Web Appsへのデプロイは任意アセットです。同じ
パッケージとコマンドを利用しますが、不要なら個別に削除できます。

パッケージ境界、依存関係、配布Workflowを変更する前に
[アーキテクチャとエンジニアリングガイド](architecture/README.ja.md)を
参照してください。
