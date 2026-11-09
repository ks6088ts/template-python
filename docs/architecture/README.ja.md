# アーキテクチャとエンジニアリングガイド

コードの配置、依存関係の追加、配布用アセットの変更を判断するときに使います。
実行手順やトラブルシューティングは[開発ガイド](../development.ja.md)を参照してください。

## 標準の設計 { #default-design }

このリポジトリは、インストール可能なパッケージ 1 つと、薄いアプリケーション境界 1 つで
構成されています。

```text
CLI（Typer、設定、ログ） -> コアの処理（値と具体的な例外）
```

`src/template_python/core.py` には、環境、ログ、CLI の副作用を持たない決定的な処理を
置きます。`cli.py` は Typer のコールバックで設定を一度だけ読み込み、ログを構成し、
設定を Click のコンテキスト（`ctx.obj`）に格納してコマンドへ渡し、コアを呼び出します。
`__init__.py` は CLI を import せずに再利用可能な処理と `__version__` を公開し、
`__main__.py` はガード付きのエントリーポイントに限定します。

これにより、ライブラリの利用者は関数を呼ぶだけのために Typer、環境変数の読み込み、
プロセス全体のログ設定を理解する必要がなくなります。

## 変更箇所の早見表 { #where-to-change-code }

| 変更内容 | 主な変更箇所 | テストする契約 |
| --- | --- | --- |
| 再利用する処理 | `src/template_python/core.py` または責務を絞った新しいモジュール | 値、正規化、具体的な例外。`tests/test_core.py` または対応する新しいテスト |
| コマンド、オプション、利用者向けエラー | `src/template_python/cli.py` | 標準出力、標準エラー出力、終了コード。`tests/test_cli.py` |
| 環境設定 | `src/template_python/settings.py` と `.env.template` | 既定値、有効な値、優先順位、拒否。`tests/test_settings.py` |
| ログ設定 | `src/template_python/log.py` | レベルと形式の検証、出力されるレコード。`tests/test_log.py` |
| 公開ライブラリ API | `src/template_python/__init__.py` | CLI を初期化せずに公開 API を import して呼べること |
| ビルドや依存関係の変更 | `pyproject.toml` と `uv.lock` | `make package-check` でインストール後の wheel、`make test-lowest` で下限を確認 |

## 認知負荷を小さく保つ { #keep-the-cognitive-cost-small }

既定の方針は意図的に選んでいます。将来の可能性ではなく、具体的な要件があるときに
変更してください。

| 判断 | 既定の方針 | 見直す条件 |
| --- | --- | --- |
| 新しい処理の置き場所 | 責務を絞ったモジュールに、名前付きの関数として置く | 具体的な外部 I/O の要件があり、アプリケーションのアダプターが必要になった |
| コードを共通化するか | 局所に置き、責務が分かる名前を付ける | 複数の実際の呼び出し元で、同じ安定した動作が必要になった |
| クラスやフレームワークを追加するか | 関数と明示的な引数を優先する | 状態やライフサイクルの管理が必要で、単純な組み合わせでは足りない |
| 依存関係やツールを追加するか | 標準ライブラリと既存のツールを使う | 明確で測定できる不足があり、実行時と保守のコストに見合う |
| 任意のアセットを追加するか | 使わないなら置かない、または削除する | 実際の配布や開発の要件で必要になった |

- 汎用的な `utils` / `common`、基底クラスの階層、サービスロケーター、
  先回りした DI フレームワークは避けます。
- 標準ライブラリと同じ名前のモジュールは作りません（ログ設定は `logging.py` ではなく
  `log.py` に置いています）。
- 入力、出力、責務が分かる名前を使います。小さな処理を理解するために、
  何層もたどる必要がないようにします。
- 値を返すか、具体的な例外を送出します。失敗を成功に見える既定値に変えたり、
  エラーを広く握りつぶしたり、シークレットをログに出したりしないでください。
- 各作業の正式な手順は 1 か所にまとめます。複数のドキュメントやワークフローに
  コマンドをコピーせず、リンクします。

自明でない判断は、問題、最も単純な代替案、選んだトレードオフ、検証方法を
プルリクエストの説明に記載します。別の設計ドキュメントは、その理由を変更後も
長く残す必要がある場合にだけ作成します。

## 技術選定 { #technology-choices }

広く使われ、継続的に保守され、インターフェースが安定したツールを選んでいます。
バージョンは現在のメジャー（0.x のツールはマイナー）までに制限し、`uv.lock` で
解決します。

| 関心事 | 選定 | 理由 |
| --- | --- | --- |
| 環境、ロック、ビルド | uv、`uv_build` | Python、仮想環境、ロック、ビルドを 1 つで扱い、ハッシュ付きで再現できる |
| CLI | Typer（Click ベース） | 型ヒント駆動で、成熟した Click の上に構築されている |
| 設定 | Pydantic Settings | 型付きで検証された環境変数と `.env` の読み込み |
| 整形と Lint | Ruff | フォーマッターと、bandit（`S`）のセキュリティルールを含む幅広いルール |
| 型 | mypy（strict）と Pydantic プラグイン | 基準となる型チェッカー |
| テスト | pytest（strict モード）、pytest-cov | 事実上の標準 |
| Git フック | prek（pre-commit 互換） | `.pre-commit-config.yaml` を読み、別の Python 環境が不要 |
| 依存関係の監査 | pip-audit | PyPA が保守。`uv audit` はまだ experimental |
| シークレットスキャン | gitleaks | フックと履歴全体のスキャン |
| ファイルとイメージのスキャン | Trivy（イメージのダイジェストを固定） | ロックファイル、Dockerfile、シークレット、OS パッケージ |
| ワークフローの解析 | actionlint、zizmor、CodeQL（`actions`） | 構文、セキュリティ、データフローの検査 |
| ドキュメント | MkDocs + Material | 安定していて広く使われている。Material は 2027-05-05 にサポートが終了する（それまでは重大な修正が提供される）。終了日までに、`mkdocs.yml` をそのまま読める後継の [Zensical](https://zensical.org/docs/compatibility/mkdocs/migration/) への移行を計画する |

## 正本の一覧 { #sources-of-truth }

| 関心事 | 正本 |
| --- | --- |
| メタデータ、依存関係、ツール設定 | `pyproject.toml` |
| 解決済みの依存関係とツールのバージョン | `uv.lock` |
| uv のバージョン範囲 | `pyproject.toml` の `[tool.uv] required-version`（CI の `setup-uv` も参照） |
| 既定の Python / サポートするバージョン | `.python-version` / `requires-python`、classifiers、`.github/workflows/test.yaml` |
| ローカルと CI のコマンド | `Makefile` |
| Git フック | `.pre-commit-config.yaml` |
| 設定スキーマ / 上書き例 | `src/template_python/settings.py` / `.env.template` |
| コンテナの動作 | `Dockerfile`、`.dockerignore`、`compose.yml` |
| 依存関係の更新方針 | `.github/dependabot.yaml` |
| ドキュメントのナビゲーション | `mkdocs.yml` |

宣言と、そこから生成されるアセットは一緒に更新します。依存関係の宣言は
`pyproject.toml` で変更し、`uv lock` で `uv.lock` を再生成します。CI は同じ検証を
別に実装せず、Make ターゲットを呼び出します。

## 実行時のルール { #runtime-rules }

- 公開パッケージは、ログ設定や環境変数の読み込みを行わずに import できる状態を
  保ちます。
- コアモジュールは Typer や設定に依存しません。CLI がコアの値と例外を、利用者向けの
  出力と終了コードに変換します。
- `PROJECT_*` 環境変数と任意の `.env` の読み込みは `ProjectSettings` が担当します。
  2 つ目の dotenv ローダーは追加しないでください。コマンドは設定を再度読み込まず、
  コンテキストから取得します。
- ルートロガーの設定は CLI のコールバックで一度だけ行います。ライブラリのモジュールは
  名前付きロガーを取得するだけにします。ログを収集する環境では
  `PROJECT_LOG_FORMAT=json` を使います。
- シークレットは `SecretStr` で宣言します。Typer の整形された例外表示ではローカル
  変数を表示しないため、トレースバックからシークレットが漏れません。
- コマンドは `[project.scripts]` で公開し、`python -m template_python` は補助的な
  実行方法として維持します。

## 品質ゲート { #quality-gate }

[変更内容ごとの検証](../development.ja.md#checks-by-change-type)に従います。
Python の検証では、整形、strict な型、拡張した Ruff のルール（bandit のセキュリティ
ルールを含む）、ワークフローのルール、全テストの分岐カバレッジ 95% 以上を確認します。
さらに wheel と sdist をビルドし、インストールした wheel の CLI、モジュール実行、
`--version` を隔離環境で実行します。sdist からのインストールは検証しません。

内部構造に結びついたテストではなく、失敗時を含む外から観測できる契約をテストします。
明示的に互換性を破る変更でない限り、標準出力、標準エラー出力、終了コード、
import 時の動作を維持します。

## セキュリティとサプライチェーン { #security-and-supply-chain }

| 層 | 対策 | 場所 |
| --- | --- | --- |
| ソースコード | Ruff の `S` ルール、CodeQL（`python`、`actions`、security-extended） | `make lint`、`codeql.yaml` |
| シークレット | gitleaks のフック、履歴全体のスキャン、Trivy のシークレットスキャナー、`detect-private-key` | フック、`make secret-scan`、`make security-scan` |
| 依存関係 | ロック済みの全パッケージを pip-audit で監査（ハッシュ検証）、Trivy による `uv.lock` のスキャン、クールダウン付きの Dependabot | `make audit`、`make security-scan`、`dependabot.yaml` |
| ワークフロー | Actions を SHA で固定、最小限の `permissions`、`persist-credentials: false`、公開用ワークフローではキャッシュを使わない、actionlint と zizmor | `.github/workflows/`、`make lint` |
| コンテナ | ベースイメージと uv イメージをダイジェストで固定、ハッシュ付きロックから `uv sync --locked`、非 root ユーザー、実行イメージに pip を含めない、hadolint、Trivy によるイメージのスキャン | `Dockerfile`、`make ci-test-docker` |
| リリース | タグとバージョンの一致確認、公開前のスキャン、SBOM と max モードのプロベナンス、GitHub の artifact attestation | `release.yaml` |
| 全体の健全性 | OpenSSF Scorecard を毎週公開 | `scorecard.yaml` |

`security.yaml` はプルリクエスト、`main`、毎週のスケジュールで
`make ci-test-security` を実行します。新しく公開された脆弱性は、コードを変更しなくても
CI の失敗として検出されます。

## 配布 { #delivery }

- プルリクエストと対象ブランチでは、Python、セキュリティ、CodeQL、コンテナの検証を
  実行します。
- `main` では、英語と日本語のドキュメントを GitHub Pages の成果物として公開します。
- `v*` タグでは `release.yaml` が動き、マルチプラットフォーム（`linux/amd64`、
  `linux/arm64`）のイメージを GHCR に公開します。
- Azure Static Web Apps へのデプロイは手動のままです。

リリースワークフローは、まずタグが `v` と `pyproject.toml` のバージョンを連結したものと
完全に一致することを確認します。次にイメージをビルドして Trivy でスキャンし、
SBOM とビルドプロベナンスを付けて push し、GitHub の artifact attestation を記録します。
タグは PEP 440 に従います。`v1.2.3` は `1.2.3`、`1.2`、`latest` を公開し、
`v1.3.0rc1` のようなプレリリースは `1.3.0rc1` だけを公開します。イメージは次のように
検証できます。

```shell
gh attestation verify oci://ghcr.io/ks6088ts/template-python:<version> --owner ks6088ts
```

GHCR はワークフローの `GITHUB_TOKEN` を使います。手動のサイトデプロイには
`AZURE_STATIC_WEB_APPS_API_TOKEN` が必要です。これらの認証情報はローカル開発には
不要です。PyPI と Docker Hub への公開は設定していません。

## テンプレートの導入 { #adopting-the-template }

1. 配布名とパッケージ名を変更します。`pyproject.toml`、`src/`、テスト、`Makefile`、
   `Dockerfile`、`compose.yml`、ワークフロー、`mkdocs.yml`、ドキュメントに含まれる
   `template-python` / `template_python` を置き換え、`uv lock` を実行します。
2. `pyproject.toml` の URL、`.github/CODEOWNERS`、`SECURITY.md`、バッジ、
   `mkdocs.yml` のオーナー名を置き換えます。
3. 設定のプレフィックス（`PROJECT_`）を決め、`.env.template` と設定リファレンスを
   更新します。
4. `hello` コマンドと `core.greeting` を実際の処理とテストに置き換えます。
   `--version` と `config` は残します。
5. 使わない任意のアセットは、依存関係、Make ターゲット、ワークフロー、リンクと一緒に
   削除します。対象は Notebook のグループと `notebooks/`、MkDocs と Pages/SWA の
   ワークフロー、Dev Container、`compose.yml` です。
6. リポジトリの設定で、private vulnerability reporting、Dependabot アラート、
   コードスキャン、`test`・`security`・`codeql`・`docker` のチェックを必須とする
   ブランチ保護を有効にします。
7. `make ci-test ci-test-docs ci-test-security ci-test-docker` を実行し、
   最初のリリースのタグを付けます。
