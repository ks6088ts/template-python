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
template_python.core -> template_python.loggers -> template_python.settings
```

上位層から下位層への依存は許可します。途中の層を飛ばす依存
（`core` から `settings` への直接参照）も許可します。
下位層から上位層への依存は、直接・他のモジュールを経由する間接参照の両方を禁止します。
`settings.project` などの子モジュールや `if TYPE_CHECKING:` 内の import も対象です。

`make lint` と `make ci-test` にもこのチェックが含まれ、違反すると既存の
Python 3.13 の CI 品質ゲートが失敗します。契約の対象は `template_python` 内で、
scripts・tests・外部ライブラリへの依存には追加の制約を設けません。
Git hook とデプロイワークフローは変更しません。

契約は exhaustive ではないため、新しいトップレベルモジュールを追加しても
層の指定は必須ではありません。ただし、そのモジュールを経由する既存層間の逆依存は
引き続き検出します。新しい層にも制約を設ける場合は、`pyproject.toml` の
`tool.importlinter.contracts` を上位から下位の順序で更新してください。
