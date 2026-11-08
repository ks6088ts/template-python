# 開発ガイド

環境構築、変更とテストの繰り返し、検証失敗からの復旧を扱います。
モジュールの責務や設計判断は
[エンジニアリングガイド](architecture/README.ja.md)を参照してください。
以下のコマンドはすべてリポジトリのルートで実行します。

## 最初に一度だけ準備する { #set-up-once }

| ツール | 必要になる場面 |
| --- | --- |
| [uv 0.13.x](https://docs.astral.sh/uv/getting-started/installation/) | 常に必要。`pyproject.toml` で `>=0.13.1,<0.14` を要求 |
| Python 3.12〜3.15 | uv が必要に応じて導入。`.python-version` で 3.14 を選択 |
| GNU Make | リポジトリの標準コマンド |
| Docker と起動済みのデーモン | コンテナ検証、`secret-scan`、`security-scan` のみ |

```shell
make install-deps-dev
uv run --locked template-python --help
make test
```

`.venv` は `uv` が管理します。依存関係を別途 `pip install` でインストールしないで
ください。仮想環境の有効化も不要です。Ruff、mypy、actionlint、zizmor、pip-audit は
`uv.lock` からインストールされるため、グローバルなツールは不要です。

Git フックを一度インストールします。

```shell
make install-hooks
make hooks-check
```

フックはファイルの整形確認、秘密鍵とシークレットの検出（gitleaks）、
`uv lock --check`、Ruff、mypy、actionlint、zizmor を実行します。Python ツールは
`uv run --locked` 経由で動くため、フックと CI のバージョンは常に一致します。
フックはテストを実行しないので、push 前に `make ci-test` を実行してください。

## 日々の開発 { #everyday-development }

1. [変更箇所の早見表](architecture/README.ja.md#where-to-change-code)で、
   対象モジュールと対応するテストを確認します。
2. 期待する出力と失敗時の動作を、対象を絞ったテストで定義します。
3. その契約を満たす最小限の変更を実装します。
4. 対象テスト、整形、変更した領域の検証を順に実行します。
5. 動作を変更した場合は、関連する英語と日本語のドキュメントを更新します。

挨拶や CLI を変更する場合は、次のコマンドから始めます。

```shell
uv run --locked pytest --no-cov tests/test_core.py tests/test_cli.py
make fix
make ci-test
```

`--no-cov` は、対象を絞った確認のためだけに使います。一部のテストだけで
パッケージ全体のカバレッジ基準を測ると、誤った失敗になるためです。
`make test` と `make ci-test` は全テストを分岐カバレッジ付きで実行し、
**95%** 以上を要求します（テンプレート自体は 100%）。pytest は strict モードで動き、
警告をエラーとして扱います。通すためだけに基準を下げたり、警告を広く無視したり
しないでください。

テストは一時的な作業ディレクトリで、`PROJECT_*` 変数を取り除いた状態で実行されます
（`tests/conftest.py` を参照）。手元のシェルや `.env` は結果に影響しません。

### 変更内容ごとの検証 { #checks-by-change-type }

| 変更した領域 | 素早い確認 | 提出前 |
| --- | --- | --- |
| Python の動作やテスト | 対象テストを `--no-cov` 付きで実行、`make fix`、`make type-check` | `make ci-test` |
| 依存関係やパッケージ情報 | `uv lock`、`make package-check` | `make ci-test`、`make audit`、`make test-lowest` |
| Markdown や `mkdocs.yml` | `make docs-serve` | `make ci-test-docs` |
| GitHub ワークフローや Dependabot | `uv run --locked actionlint`、`uv run --locked zizmor --offline .` | `make ci-test` |
| Dockerfile や Compose | `make docker-build docker-run` | `make ci-test-docker`。Compose を変更した場合は `docker compose up --build` も実行 |

複数の領域にまたがる場合は、該当する検証をすべて実行します。

| コマンド | 内容 |
| --- | --- |
| `make help` | 利用できる Make ターゲットを表示 |
| `make fix` | Ruff の自動修正と整形を適用。変更内容は確認する |
| `make lint` | strict な mypy、Ruff（セキュリティルールを含む）、actionlint、zizmor を実行 |
| `make test` | 分岐カバレッジ付きで pytest を実行 |
| `make test-lowest` | Python 3.12 と、宣言した直接依存の下限バージョンでテスト |
| `make package-check` | wheel と sdist をビルドし、インストール後の CLI、モジュール実行、`--version` を確認 |
| `make ci-test` | 開発用依存関係を同期し、整形、Lint、テスト、パッケージ検証を実行 |
| `make audit` | ロック済みの全依存関係を pip-audit で監査（ハッシュ検証、pip 不使用） |
| `make secret-scan` | gitleaks で Git 履歴全体をスキャン（Docker） |
| `make security-scan` | Trivy で脆弱な依存関係、設定ミス、シークレットをスキャン（Docker） |
| `make ci-test-security` | `audit`、`secret-scan`、`security-scan` を実行 |

CI は Python 3.14 で全検証とドキュメントのビルドを行い、3.12・3.13・3.15 の互換性
テスト、下限依存のジョブ、フックを別ジョブで実行します。セキュリティスキャンは
プルリクエストと毎週実行されます。詳細は
[セキュリティとサプライチェーン](architecture/README.ja.md#security-and-supply-chain)
を参照してください。

## 設定 { #configuration }

CLI は既定値だけで動作します。ローカルで値を変更する場合のみ、
`.env.template` を `.env` にコピーします。

```shell
cp .env.template .env
```

| 変数 | 既定値 | 指定できる値と効果 |
| --- | --- | --- |
| `PROJECT_NAME` | `template-python` | デバッグ用の起動ログに表示する文字列。挨拶文は変わりません |
| `PROJECT_LOG_LEVEL` | `INFO` | `DEBUG`、`INFO`、`WARNING`、`ERROR`、`CRITICAL` |
| `PROJECT_LOG_FORMAT` | `text` | 人が読む `text`、または 1 行 1 JSON オブジェクトの `json`（ログ収集基盤やコンテナ向け） |

優先順位は、環境変数、`.env`、既定値の順です。
変数名の大文字と小文字は区別しませんが、**値**は上記の選択肢と完全に一致させてください。
`.env` は作業ディレクトリから読み込まれ、未知の `PROJECT_*` 項目はエラーになります。
別のアプリケーションの `.env` は再利用しないでください。ローカル設定やシークレットは
バージョン管理に含めないでください。

```shell
PROJECT_LOG_LEVEL=DEBUG uv run --locked template-python hello --name Ada
PROJECT_LOG_FORMAT=json uv run --locked template-python --verbose hello
uv run --locked template-python config
```

`config` は有効な設定を JSON で出力します。認証情報は `pydantic.SecretStr` で宣言
してください。値は `**********` と表示されます。

| グローバルオプション | 効果 |
| --- | --- |
| `--verbose`、`-v` | 設定の検証後にデバッグログを選択。不正な設定を有効にはしません |
| `--version`、`-V` | `template-python <version>` を表示して終了。設定が不正でも動作します |
| `--help` | ヘルプを表示。コマンドなしで実行した場合もヘルプを表示（終了コード 2） |

グローバルオプションはコマンドより前に指定します（`template-python --verbose hello`）。
コマンドの出力は標準出力へ、ログと検証エラーは標準エラー出力へ書き込まれます。
空白だけの `--name` や不正な設定は、終了コード **2** で終了します。

## 依存関係 { #dependencies }

- 依存関係の宣言は `pyproject.toml` で変更し、`uv lock` を実行してから、
  マニフェストと `uv.lock` の両方をコミットします。ロックファイルの解決結果は
  手作業で編集しないでください。
- 下限バージョンを正しく保ちます。`make test-lowest` は直接依存の下限バージョンを
  インストールし、成功する必要があります。
- `make update` は、意図的に依存関係を広く更新する場合だけ使います。
  現在のバージョンを同期するのではなく、`uv lock --upgrade` を実行します。
  実行後は `make audit` を実行してください。
- 実行時の依存関係は `project.dependencies` に置き、開発、テスト、ドキュメント、
  Notebook 用のツールは既存のグループに置きます。
- Dependabot は Python パッケージ、GitHub Actions、pre-commit フック、Docker の
  ベースイメージ、Dev Container の feature について、7 日間のクールダウン後に
  グループ化した更新を毎週作成します。`Makefile` のツールイメージと
  Dev Container の uv バージョンは手動で固定しています。uv を上げる場合は
  `[tool.uv] required-version` と合わせて更新してください。

## ドキュメント { #documentation }

```shell
make docs-serve
```

MkDocs が表示するアドレス（通常は `http://127.0.0.1:8000`）を開きます。
`Ctrl+C` でプレビューを止めてから、次のコマンドで検証します。

```shell
make ci-test-docs
```

ビルドは strict モードで実行され、英語と日本語のページを Git の管理対象外である
`site/` に出力します。`page.md` と `page.ja.md` は一緒に編集します。他のページから
リンクされる見出しには `## 見出し { #heading }` のように明示的な ID を付け、
両言語でアンカーを共有します。新しいページは日本語のナビゲーション名も含めて
`mkdocs.yml` に追加し、ドキュメント間のリンクには相対パスを使います。導入手順は
README、作業手順はこのガイド、設計理由はエンジニアリングガイドに置きます。

## トラブルシューティング { #troubleshooting }

検証を無効化したり、複数のツールを同時に変更したりせず、最初に失敗したコマンドから
修正します。

| 症状 | 確認すること / 次の対応 |
| --- | --- |
| `uv: command not found` | uv 0.13.x をインストールし、`PATH` に含まれることを `uv --version` で確認 |
| `Required uv version ... does not match` | `[tool.uv] required-version` の範囲に uv を合わせる（例: `uv self update`） |
| Python のバージョンが合わない | サポート対象のインタープリターを指定。例: `uv sync --locked --group dev --python 3.13` |
| ロックファイルの更新が必要と表示される | 意図した依存関係の変更なら `uv lock` を実行して両方を確認。そうでなければ `--locked` を外さず差異の原因を調べる |
| `make audit` が脆弱性を報告する | パッケージを更新（`uv lock --upgrade-package <name>`）して再実行。ID を無視する場合は理由を記録する |
| `make test-lowest` が失敗する | `pyproject.toml` の下限を動作する最初のバージョンへ上げてから `uv lock` |
| `Invalid configuration` / 終了コード 2 | `PROJECT_*` 変数と作業ディレクトリの `.env` を確認し、指定できる値を使う |
| 一部のテストでカバレッジ基準を満たせない | その場合は `--no-cov` を使い、正式なカバレッジ判定は `make test` で行う |
| Docker デーモンに接続できない | Docker を起動してから再実行。コンテナとスキャンのターゲット以外では不要 |
| 新しいページが表示されない、またはリンク切れになる | `mkdocs.yml`、両言語のファイル、見出し ID、リンク先を確認して再ビルド |

問い合わせる際は、実行したコマンド、最初のエラー、OS、Python と uv のバージョン、
関連する変更を記載してください。シークレットや非公開の設定は伏せてください。
