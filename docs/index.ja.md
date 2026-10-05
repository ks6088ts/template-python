# template-python

このリポジトリは、Python プロジェクトのためのテンプレートリポジトリです。

## 依存方向のチェック

開発依存をインストールして、アーキテクチャのチェックを実行します。

```shell
make install-deps-dev
make import-lint
```

[import-linter](https://import-linter.readthedocs.io/) は `pyproject.toml` の
layers 契約を使い、次の依存方向を検証します。

```text
scripts (applications) -> template_python (library)
```

`scripts/` 以下をアプリケーション層、`template_python` をライブラリ層として扱います。
アプリケーションからライブラリへの依存は許可します。
ライブラリ内のどのモジュールからも、`scripts` とその子モジュールへの
直接・間接の依存は禁止します。この境界は、どちらのディレクトリに新しく追加した
モジュールにも適用されます。

`if TYPE_CHECKING:` 内の import も対象です。
ライブラリ内部のモジュール間には依存方向の制約を設けません。

`make lint` と `make ci-test` にもこのチェックが含まれ、違反すると既存の
Python 3.13 の CI 品質ゲートが失敗します。契約の対象は `scripts` と
`template_python` の両方で、tests・外部ライブラリへの依存には追加の制約を設けません。
Git hook とデプロイワークフローは変更しません。
