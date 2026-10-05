# アーキテクチャ・開発ガイド

## プロジェクト概要

`template-python` は Python 3.10 以上を対象とする再利用可能なテンプレートです。
小さなライブラリと CLI の例、環境変数ベースの設定、構造化ログ、テスト、
ドキュメント、コンテナ、固定された CI/CD ワークフローを提供します。

ローカルと CI で同じコマンドを使い、少数の明示的なルールを自動検証することを
基本方針とします。

| 領域 | Source of truth |
| --- | --- |
| パッケージ情報・ツール設定 | `pyproject.toml` |
| 解決済み依存関係 | `uv.lock` |
| 開発・CI コマンド | `Makefile` |
| Python 互換性・品質ゲート | `.github/workflows/test.yaml` |
| ドキュメントの導線・多言語化 | `mkdocs.yml` |

## ディレクトリの責務

| パス | 責務 |
| --- | --- |
| `template_python/` | 再利用可能なライブラリ。アプリケーションへ依存しない |
| `template_python/settings/` | 型付きの環境変数・`.env` 設定 |
| `scripts/` | ライブラリを組み立てるアプリケーション入口 |
| `tests/` | 単体テスト・振る舞いのテスト |
| `docs/` | MkDocs の英語・日本語ソース |
| `notebooks/` | 任意利用の対話的な例 |
| `.github/workflows/` | テスト、文書、コンテナ、リリースの自動化 |

最初に `pyproject.toml` と `Makefile` を確認し、続けて
`scripts/template.py`、`template_python/core.py`、
`template_python/settings/project.py`、対応するテストの順に読むと全体を把握できます。

## 依存方向

意図する依存方向は次のとおりです。

```text
scripts (applications) -> template_python (library)
```

アプリケーションはライブラリを import して組み立てられます。ライブラリから
`scripts` への直接・間接の依存は禁止し、`TYPE_CHECKING` 内の import も対象です。
`pyproject.toml` の import-linter 契約が、既存および新規モジュールにこの境界を
強制します。安定した内部レイヤーが必要になるまでは、ライブラリ内部の依存方向を
過剰に制約しません。

## 実行時モデル

- `scripts/template.py` は Typer CLI の例であり、アプリケーションの composition
  root です。
- `template_python/core.py` は CLI に依存しないライブラリの振る舞いを持ちます。
- `ProjectSettings` は環境変数と `.env` から `PROJECT_*` を読み取ります。最初の
  取得後に設定を意図的に変更するテストや長時間プロセスでは
  `get_project_settings.cache_clear()` を呼びます。
- `get_logger()` はプロジェクトの名前付き logger ごとに handler を 1 つだけ持ち、
  呼び出しごとに現在の指定レベルを反映し、root logger 経由の二重出力を防ぎます。
- Docker image は既定で `python -m template_python.core` を実行します。Compose は
  コンテナ例として単純な HTTP server に command を上書きします。

## 設計原則

1. **依存方向を明示する。** アプリケーションがライブラリを組み立て、再利用可能な
   コードから entry point へ逆依存させません。
2. **ローカルと CI で同じコマンドを使う。** 検査は Make target に追加し、CI に
   shell 処理を重複させず、その target を呼び出します。
3. **設定を境界に置く。** 外部設定は型付き settings で読み、可能な限り値として
   core の振る舞いへ渡します。
4. **繰り返し呼び出しても安全にする。** logger や settings の factory は handler
   などの process-global state を意図せず蓄積させません。
5. **決定的なツール実行を優先する。** `uv.lock` を commit し、`uv --locked` を使い、
   third-party GitHub Actions は commit SHA で固定します。
6. **観測可能な契約をテストする。** 実装詳細だけでなく、振る舞い、依存規則、
   サポートする Python version を検証します。
7. **テンプレートを置換しやすく保つ。** 生成先で必要になるまでは、固有の
   infrastructure や domain abstraction を持ち込みません。
8. **失敗を明示する。** 品質、型、アーキテクチャ、文書、security の検査は、
   成功に見える fallback を返さず失敗として表面化させます。

## 開発フロー

```shell
make install-deps-dev
make fix
make ci-test
make ci-test-docs
```

`make ci-test` は CI 用依存を導入し、format、mypy strict、import-linter、Ruff、ty、
Pyrefly、actionlint、zizmor、pytest を実行します。CI では Python 3.13 が全品質
ゲートを実行し、Python 3.10 から 3.14 が互換性テストを実行します。
`make hooks-check` は設定済みの prek hook を検証します。

Docker daemon を利用できる場合は `make docker-build`、`make docker-run`、
`make ci-test-docker` を使います。Trivy は現在、検出内容を報告しますが、severity
による失敗条件は設定していません。

## デリバリーモデル

- push と pull request で Python 互換性・品質 workflow を実行します。
- `main` への push で MkDocs site を公開します。
- `v*` tag で Docker Hub と GitHub Container Registry に multi-platform image を
  公開します。
- Azure Static Web Apps は push trigger を明示的に有効化しない限り手動実行です。
- Dependabot は uv、GitHub Actions、pre-commit、Docker の依存を毎週確認します。

release workflow は配送手段であり、test workflow の代替ではありません。変更時は
最小権限と不変な action pin を維持します。

## 変更時のチェックリスト

1. 再利用可能な振る舞いは `template_python/`、組み立ては `scripts/` に置く。
2. 観測可能な振る舞いに対して焦点を絞ったテストを追加・更新する。
3. 依存変更では `pyproject.toml` と再生成した `uv.lock` を同時に更新する。
4. 再利用する検査は `Makefile` に追加してから、その target を CI に接続する。
5. 利用者向けの振る舞いや開発規約を変えたら英語・日本語文書を更新する。
6. `make ci-test` と `make ci-test-docs` を実行し、コンテナ変更では Docker 検査も
   実行する。

## 既知の制約

- これは本番 service ではなく template です。CLI、notebook、HTTP server、
  container command は置換・拡張するための例です。
- application/library 境界以外に、ライブラリ内部の layer 契約はありません。
- ドキュメントは MkDocs plugin に依存するため、文書 engine の移行時には多言語出力を
  維持する必要があります。
- コンテナの脆弱性検査は、明示的な blocking policy を採用するまでは情報提供です。
