# 3D Designs

3Dプリント用モデル、CAD、設計コードをまとめるリポジトリです。モデルごとにフォルダーを分けて管理します。

## モデル

| モデル | 内容 | 設計形式 |
| --- | --- | --- |
| [Filament Drybox](filament-drybox/) | Bambu Labのスプールを1巻収納する、小型脚・回転式ふた・シリカゲル筒付きケース | build123d / STEP / STL |

## フォルダー構成

```text
3d-designs/
├─ README.md
└─ filament-drybox/
   ├─ README.md          # モデルの概要と使い方
   ├─ README.txt         # 詳細寸法・組み立て説明
   ├─ filament_case.py   # 編集可能な設計コード
   ├─ requirements.txt
   ├─ validation.json
   ├─ cad/              # STEPデータ
   ├─ stl/              # 造形用データ
   └─ images/           # プレビュー画像
```

新しいモデルは、このリポジトリ直下に名前の付いたフォルダーを追加します。寸法や造形条件、必要な部品、検証状況は各モデルのREADMEに記録します。

## 編集と履歴

モデルごとの説明に従って設計コードを実行し、更新したCAD・STLとコードをまとめてコミットします。Pythonの仮想環境と作業用ファイルは管理対象外です。

既存の収納ケースの履歴を引き継いでいます。`design-v2` タグは、モデル別フォルダーに整理する前の省スペース・自立型ケースを保存した時点を指します。
