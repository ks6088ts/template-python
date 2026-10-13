# template-python

Python 3.12+ 向けの、型付きパッケージ兼 CLI テンプレートです。まずサンプルを
動かし、その後は目的に合うガイドだけを読んでください。コンテナ、Notebook、
デプロイは任意であり、開発を始めるための前提ではありません。

## まず動かす

[uv 0.12.19](https://docs.astral.sh/uv/getting-started/installation/)、
Python 3.12+、GNU Make を用意し、リポジトリのルートで実行します。

```shell
make install-deps-dev
uv run --locked template-python hello --name Ada
make test
```

CLI の出力は次のとおりです。

```text
Hello, Ada!
```

`.env` の作成や仮想環境の有効化は不要です。CI の全検証は Python 3.13 で行い、
3.12 と 3.14 でも互換性テストを実行します。

## 目的から探す

| やりたいこと | 読むガイド |
| --- | --- |
| 開発環境を用意し、コードを変更・検証する | [開発ガイド](development.ja.md) |
| 変更するモジュールや設計方針を判断する | [アーキテクチャとエンジニアリング](architecture/README.ja.md) |
| 環境変数を設定し、CLI のエラーを理解する | [設定リファレンス](development.ja.md#configuration) |
| コマンドの失敗から復旧する | [トラブルシューティング](development.ja.md#troubleshooting) |
| テンプレートを改名し、不要な機能を外す | [テンプレートの導入](architecture/README.ja.md#adopting-the-template) |
| ドキュメントをプレビュー・検証する | [ドキュメントの開発](development.ja.md#documentation) |

## 覚えることはこの4つ

- 再利用する処理はコアへ、設定・ログ・表示・終了コードは CLI へ置きます。
- コマンドの正本は `Makefile` です。ツールのオプションを覚える代わりに
  `make help` を使います。
- 依存関係の宣言は `pyproject.toml`、解決済みバージョンは `uv.lock` が管理します。
- 英語と日本語のページを揃えます。詳細な手順を README に重複させず、
  該当するガイドへリンクします。
