# アーキテクチャとエンジニアリングガイド

コードの置き場所、依存関係の追加、配布アセットの変更を判断するときに使います。
実行手順とトラブル対応は[開発ガイド](../development.ja.md)を参照してください。

## 既定の設計

1つのインストール可能なパッケージと、薄いアプリケーション境界で構成します。

```text
CLI（Typer、設定、ログ） -> コアロジック（値と具体的な例外）
```

`src/template_python/core.py` は、環境変数、ログ、CLI の副作用を持たない決定的な
処理を担当します。`cli.py` が設定を読み、ログを構成してコアを呼び出します。
`__init__.py` は CLI を import せず再利用可能な処理を公開し、
`__main__.py` は起動だけを担当します。

この分離により、ライブラリの利用者は関数を呼ぶだけなら、Typer、環境変数の
読み込み、プロセス全体のログ設定を理解する必要がありません。

<a id="where-to-change-code"></a>

## 変更箇所の早見表

| 変更したいこと | 主な変更先 | テストする契約 |
| --- | --- | --- |
| 再利用可能な処理 | `src/template_python/core.py` または目的の明確な新モジュール | `tests/test_core.py` または対応する新テストで、値・正規化・具体的な例外を確認 |
| コマンド・オプション・利用者向けエラー | `src/template_python/cli.py` | `tests/test_cli.py` で stdout・stderr・終了コードを確認 |
| 環境変数による設定 | `src/template_python/settings.py` と `.env.template` | `tests/test_settings.py` で既定値・許容値・拒否を確認 |
| ログ設定 | `src/template_python/logging.py` | `tests/test_logging.py` でレベル検証・出力を確認 |
| ライブラリの公開 API | `src/template_python/__init__.py` | CLI を初期化せず公開 API を import・実行できることを確認 |
| ビルド・依存関係 | `pyproject.toml` と `uv.lock` | `make package-check` でインストール済み wheel の動作を確認 |

## 認知負荷を小さく保つ

既定の方針には理由があります。将来必要かもしれないものではなく、具体的な要求に
応じて変更します。

| 判断 | まず選ぶもの | 見直す条件 |
| --- | --- | --- |
| 新しい処理の置き場所 | 目的の明確なモジュールの名前付き関数 | 外部 I/O の具体的な要求によりアプリケーション側の adapter が必要 |
| 共通化するか | 責務が分かる名前で局所的に実装 | 複数の実際の利用箇所で同じ安定した振る舞いが必要 |
| class・framework を追加するか | 関数と明示的な引数 | 状態や lifecycle の所有者が必要で、単純な組み合わせでは不足 |
| 依存関係・ツールを追加するか | 標準ライブラリと既存ツール | 実行時・保守時のコストに見合う、測定可能な不足がある |
| 任意アセットを使うか | 未使用のままにするか削除 | 実際の配布・開発要件で必要 |

- `utils`・`common` の寄せ集め、基底クラス階層、サービスロケータ、
  将来を想像した DI framework は避けます。
- 入出力と責務を表す名前を使います。小さな処理を理解するために、何層ものコードを
  追う必要がない構造にします。
- 値を返すか、具体的な例外を送出します。失敗を成功に見える既定値へ置き換えたり、
  広く握りつぶしたり、秘密情報をログへ出したりしません。
- 手順の正本を1つにします。複数の文書や Workflow へコマンドをコピーせず、
  参照・再利用します。

自明ではない判断は、問題、最も単純な代替案、選んだトレードオフ、検証方法を
PR の説明に残します。別の設計文書は、その変更後も理由を参照する必要があるとき
だけ作ります。

## 情報の正本

| 対象 | 正本 |
| --- | --- |
| メタデータ、依存関係、ツール設定 | `pyproject.toml` |
| 解決済み依存バージョン | `uv.lock` |
| ローカルと CI のコマンド | `Makefile` |
| 最低 Python・テスト対象バージョン | `pyproject.toml`・`.github/workflows/test.yaml` |
| 設定の schema・設定例 | `src/template_python/settings.py`・`.env.template` |
| コンテナ動作 | `Dockerfile` と `compose.yml` |
| ドキュメント構成 | `mkdocs.yml` |

宣言と、その宣言から生成するものは一緒に更新します。依存関係は
`pyproject.toml` で変更し、`uv lock` で lock を再生成します。
CI は同じ検証を独自に実装せず、Make target を呼びます。

## ランタイムのルール

- パッケージの import 時にログ設定や環境変数読み込みを行いません。
- コアは Typer や設定に依存せず、CLI が値と例外を表示・終了コードへ変換します。
- `ProjectSettings` が `PROJECT_*` と任意の `.env` を一元管理します。
  別の dotenv loader を追加しません。
- root logger の設定は CLI callback で一度だけ行い、ライブラリは名前付き
  logger を取得するだけにします。
- CLI は `[project.scripts]` で公開し、`python -m template_python` も維持します。

## 品質ゲート

[変更内容に応じた検証](../development.ja.md#checks-by-change-type)を選びます。
Python の品質ゲートは、整形、型、Lint、Workflow のルール、全テストを確認し、
branch coverage **95% 以上**を要求します。wheel と sdist をビルドした後、
wheel の CLI とモジュール起動を隔離環境で確認します。
sdist のインストール試験は行いません。

内部構造ではなく、失敗時を含む観測可能な契約をテストします。互換性を壊す必要が
明示されていない限り、stdout、stderr、終了コード、import 時の動作を保ちます。

## 配布

- Pull Request と対象ブランチで Python とコンテナを検証します。
- `main` から GitHub Pages へ英日ドキュメントを公開します。
- `v*` tag から Docker Hub と GHCR へ multi-platform image を公開します。
- GHCR release には push 済み digest に対応する provenance を付与します。
- Azure Static Web Apps は手動デプロイを維持します。

Release Workflow は、tag が `v` と `pyproject.toml` の version を連結した値に
一致することを確認してから公開します。Docker Hub には
`DOCKERHUB_USERNAME` と `DOCKERHUB_TOKEN` の secret が必要です。
GHCR は Workflow の GitHub token を使います。手動のサイト公開には
`AZURE_STATIC_WEB_APPS_API_TOKEN` が必要です。これらの認証情報はローカル開発に
不要です。PyPI への公開は設定されていません。

外部 Action は commit SHA で固定します。Workflow は明示的な最小権限、
checkout credential の無効化、timeout を使い、自動キャンセルは後続実行で
置き換えられる release 以外の処理に限定します。

<a id="adopting-the-template"></a>

## テンプレートの導入

新しいプロジェクトを作ったときに一度行い、公開を有効にする前に確認します。

1. `pyproject.toml` の配布名、説明、version、URL、console script を設定し、
   ライセンスが適切か確認します。
2. import 名を変えるなら `src/template_python/` を改名し、import、テストの参照、
   script の参照先、モジュール起動コマンド、coverage などのツール設定も揃えます。
   型付きパッケージの `py.typed` は維持します。
3. 設定の既定値、`.env.template`、Notebook の例、Makefile の配布物検証コマンドと
   image の既定値、Dockerfile の起動先と label、Compose、Dev Container 名、
   docs の URL、Workflow の image 名、README の badge を更新します。
   配布名はハイフン、Python の import 名はアンダースコアを使います。
4. 次の表に従い不要なアセットを外し、実行できない CI の参照を残しません。
5. `uv lock` を実行し、残したアセットを検証します。ソースの直接 import だけでなく、
   改名後のインストール済み CLI を確認します。
6. 残した配布 Workflow にだけ、リポジトリの公開設定と secret を用意します。
   release tag とパッケージ version を一致させます。

### 任意アセット

Notebook、docs、コンテナ、registry、Azure、Dev Container は独立したサンプルです。
別のアプリケーション動作を作らず、インストール済みパッケージを利用します。

| 外すアセット | 同時に削除・更新するもの |
| --- | --- |
| Notebook | `notebooks/`、`notebook` 依存グループ、`jupyterlab` Make target |
| ドキュメントサイト | `docs/`、`mkdocs.yml`、`docs` グループと Make target、両サイト公開 Workflow、`test.yaml` の docs コマンド |
| コンテナ | Dockerfile、Compose、`.dockerignore`、Docker の Make target・変数、コンテナ検証・公開 Workflow |
| registry 公開だけ | 不要な job または container-release Workflow。必要ならローカルのコンテナ検証は残す |
| 手動のサイト公開だけ | `azure-static-web-app.yaml` とデプロイの説明 |
| Dev Container | `.devcontainer/` と環境構築の説明 |

依存グループを変更したら lock を再生成し、badge、リンク、ガイドの項目も同じ変更で
整理します。認証情報を要求する未使用の Workflow を残さないでください。

多言語出力が MkDocs 1 の plugin ecosystem に依存する間、MkDocs は 2 未満に
固定します。

## 変更チェックリスト

- [ ] 変更の目的が1つで、上記のモジュール境界を守っている。
- [ ] 期待する値と失敗をテストし、互換性を変える場合は明示している。
- [ ] 依存宣言、lock、影響する配布アセットが一致している。
- [ ] コマンドは既存 Make target を再利用し、新ツールは実際の不足を補っている。
- [ ] 影響する英日ドキュメントを更新し、手順を重複させていない。
- [ ] 変更した各領域の検証が成功し、必要なインストール済みパッケージの確認も行った。
