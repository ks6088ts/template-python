# 開発ガイド

環境構築、変更とテストの繰り返し、検証失敗からの復旧を扱います。
モジュールの責務や設計判断は
[エンジニアリングガイド](architecture/README.ja.md)を参照してください。
以下のコマンドはすべてリポジトリのルートで実行します。

## 最初に一度だけ準備する

| ツール | 必要になる場面 |
| --- | --- |
| Python 3.12+ | パッケージとテスト。CI の全検証に合わせるなら 3.13 |
| [uv 0.12.19](https://docs.astral.sh/uv/getting-started/installation/) | ロック済み依存関係の管理とコマンド実行 |
| GNU Make | リポジトリの標準コマンド |
| [actionlint](https://github.com/rhysd/actionlint/blob/main/docs/install.md) | `make lint` と `make ci-test`。CI は 1.7.12 を使用 |
| Docker と起動済みの daemon | コンテナ関連のコマンドだけ |

```shell
make install-deps-dev
uv run --locked template-python --help
make test
```

`.venv` は uv が管理します。別の `pip install` でプロジェクトの依存関係を
導入したり、仮想環境を有効化したりする必要はありません。
`make install-deps-dev` が表示する actionlint の案内は、Python テストの実行を
妨げません。

Git hook を使う場合だけ、次を実行します。

```shell
make install-hooks
make hooks-check
```

Hook は YAML、空白、Ruff のルールを確認します。型検査、テスト、全品質ゲートの
代わりにはなりません。

## 日常の開発

1. [変更箇所の早見表](architecture/README.ja.md#where-to-change-code)で、
   変更するモジュールとテストを特定します。
2. 期待する出力と失敗時の振る舞いを、小さなテストで定義します。
3. その契約を満たす最も単純な変更を実装します。
4. 対象のテストを実行し、整形と変更範囲に合う検証を行います。
5. 振る舞いが変わる場合は、対応する英語と日本語の説明を更新します。

挨拶や CLI を変更する場合の例です。

```shell
uv run --locked pytest --no-cov tests/test_core.py tests/test_cli.py
make fix
make ci-test
```

`--no-cov` は対象を絞った反復作業だけに使います。一部のテストでパッケージ全体の
カバレッジを測ると、変更とは無関係な不足で失敗するためです。
`make test` と `make ci-test` は全テストと branch coverage を実行し、
**95% 以上**を要求します。一部のテストを通すために閾値を下げないでください。

<a id="checks-by-change-type"></a>

### 変更内容に応じた検証

| 変更対象 | 作業中の確認 | 提出前の検証 |
| --- | --- | --- |
| Python の処理・テスト | `--no-cov` 付きの対象テスト、`make fix`、`make type-check` | `make ci-test` |
| 依存関係・パッケージ情報 | `uv lock`、`make package-check` | `make ci-test`。影響する場合は docs・コンテナも検証 |
| Markdown・`mkdocs.yml` | `make docs-serve` | `make ci-test-docs` |
| GitHub Workflow | `actionlint` | `make ci-test` と、その Workflow が呼ぶ検証 |
| Dockerfile・Compose | `make docker-build docker-run` | `make ci-test-docker`。Compose 変更時は `docker compose up --build` も実行 |

複数の領域を変更したら、該当する検証をすべて行います。ドキュメントだけの変更で
Python やコンテナの品質ゲートを実行する必要はありません。

新しい手順を覚える代わりに、既存コマンドを使います。

| コマンド | 実行すること |
| --- | --- |
| `make help` | 利用できる Make target の一覧表示 |
| `make fix` | Ruff による自動修正と整形。自動変更の内容は確認する |
| `make lint` | mypy strict、Ruff、actionlint、オフラインの zizmor |
| `make test` | branch coverage 付きの pytest |
| `make package-check` | wheel と sdist をビルドし、wheel の CLI とモジュール起動を隔離環境で確認 |
| `make ci-test` | dev 依存関係の同期、整形確認、Lint、テスト、配布物検証 |

CI は Python 3.13 で全品質ゲートと docs ビルド、3.12 と 3.14 で互換性テスト、
別の job で hook の検証を行います。

<a id="configuration"></a>

## 設定リファレンス

CLI は既定値で動作します。ローカル設定を変更する場合だけ、
`.env.template` を `.env` にコピーします。

```shell
cp .env.template .env
```

| 環境変数 | 既定値 | 許容値・影響 |
| --- | --- | --- |
| `PROJECT_NAME` | `template-python` | 起動時の debug ログに使う文字列。挨拶の出力は変わらない |
| `PROJECT_LOG_LEVEL` | `INFO` | `DEBUG`、`INFO`、`WARNING`、`ERROR`、`CRITICAL` |

優先順位は、環境変数、`.env`、既定値の順です。変数名の大文字・小文字は区別
しませんが、ログレベルの**値**は上記の大文字表記にします。
`.env` は作業ディレクトリから読み、未知の項目は拒否します。別のアプリケーションの
`.env` を流用しないでください。ローカル設定や秘密情報はコミットしません。

```shell
PROJECT_LOG_LEVEL=DEBUG uv run --locked template-python hello --name Ada
uv run --locked template-python --verbose hello --name Ada
```

`--verbose` はグローバルオプションなので、`hello` の前に置きます。
設定を検証した後で debug ログを有効にするため、不正な設定を回避する用途には
使えません。正常な挨拶は stdout、ログと検証エラーは stderr に出力します。
空白だけの `--name` と不正な設定は、終了コード **2** で失敗します。

## 依存関係

- `pyproject.toml` の依存宣言を編集し、`uv lock` を実行して両方のファイルを
  コミットします。解決済みの lock エントリを手で編集しません。
- `make update` は全体の更新を意図した場合だけ使います。既存バージョンの同期では
  なく、`uv lock --upgrade` を実行するコマンドです。
- 実行時の依存関係は `project.dependencies`、開発・テスト・docs・Notebook の
  ツールは既存の各グループへ追加します。
- 既存コマンドは必要な依存グループを選んで同期します。docs と Notebook は
  `--no-dev` を使い、その後の dev コマンドで必要な dev グループが再び同期されます。

<a id="documentation"></a>

## ドキュメントの開発

```shell
make docs-serve
```

MkDocs が表示する URL（通常は `http://127.0.0.1:8000`）を開きます。
`Ctrl+C` でプレビューを終了し、次のコマンドで検証します。

```shell
make ci-test-docs
```

英語と日本語の出力は、Git 管理対象外の `site/` に生成されます。
`page.md` と `page.ja.md` は一緒に編集してください。ページを追加するときは
`mkdocs.yml` のナビゲーションと日本語のラベルも追加します。
ドキュメント同士は相対リンクにします。README は導入、このページは手順、
エンジニアリングガイドは設計理由を担当します。

<a id="troubleshooting"></a>

## トラブルシューティング

検証を無効にしたり、複数のツールを一度に変更したりせず、最初に失敗した
コマンドから原因を確認します。

| 症状 | 確認すること・次の行動 |
| --- | --- |
| `uv: command not found` | 指定バージョンの uv を導入し、`PATH` と `uv --version` を確認する |
| Python のバージョンが合わない | 例として `uv sync --locked --group dev --python 3.13` で対応 interpreter を選ぶ |
| Lint・CI で `actionlint: command not found` | actionlint を導入して `actionlint --version` を確認する。対象の確認には `make test` を使える |
| lock の更新が必要と表示される | 意図した依存変更なら `uv lock` で両方を更新する。それ以外は `--locked` を外さず宣言と lock のずれを調べる |
| `Invalid configuration`・終了コード 2 | `PROJECT_*` と作業ディレクトリの `.env` を確認し、大文字の許容ログレベルを使う |
| 対象テストだけの実行でカバレッジ不足 | 対象を絞る間は `--no-cov`、実際の品質ゲートには `make test` を使う |
| Docker daemon に接続できない | Docker を起動して再実行する。Python だけの作業ならコンテナ環境は不要 |
| ページが表示されない・リンクが切れている | `mkdocs.yml`、英日のファイル、リンク先を確認し、両言語を再ビルドする |

相談するときは、実行コマンド、最初のエラー、OS、Python・uv のバージョン、
関連する変更を添えます。秘密情報や非公開の設定は伏せてください。
