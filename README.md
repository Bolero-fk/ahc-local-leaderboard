# ahc-local-leaderboard
AtCoderのAHC（AtCoder Heuristic Contest）で使用するためのツールです。  
自分の提出スコアを元に、相対順位表をローカル環境で作成・管理できます。

## How to Install
（準備中: 追記予定）

## Usage
### setup
`ahc-local-leaderboard`は、AHCで配布されるローカル版ツールの使用を前提としています。
1. AHCの公式ツールが展開されたディレクトリに移動します。
2. 以下のコマンドを実行して、相対順位表用のディレクトリを作成します：
```bash
local-leaderboard setup
```
この手順により、`ahc-local-leaderboard`で必要となるファイルやディレクトリが準備されます。

### submit
`submit`コマンドを使うことで、自分の提出結果をローカル順位表に登録できます。
```bash
local-leaderboard submit
```

このコマンドでは、以下の処理が行われます：
- **入力と出力のファイル**  
  - `in`ディレクトリのファイルを入力として使用。
  - `out`ディレクトリのファイルを出力として使用。  
  
  ※ **ファイル名は一致させる必要があります**。例えば、`in/0000.txt` に対応する出力ファイルは `out/0000.txt` である必要があります。

- **点数計算**  
  AHCツールに含まれるビジュアライザを使用してスコアを計算。

提出処理が終了すると、以下のように提出結果が表示されます：

<div align="center">
<img src="./images/submit.png" alt="Submission Details">
</div>


詳しい見方については、[view](#view)のセクションを参考にしてください。

### view
`view`コマンドを使うことで、過去の提出結果を表示できます。
```bash
local-leaderboard view
```

以下は実行結果の例です：
<div align="center">
<img src="./images/view.png" alt="View Details">
</div>

| 項目名 | 説明|
|:-:|-|
| **Id**| 各提出に割り振られた一意の識別番号です。|
|**Rank**|相対スコアに基づく順位を表します。|
|**Submission Time**|提出の日時を表します。|
|**Total Absolute Score**|提出全体の絶対スコアの合計値です。<br>（括弧内の数字は、点数計算が失敗したテストケースの総数を表します）|
|**Total Relative Score**|提出全体の相対スコアの合計値です（最も高いスコアが10^9になります）。|

---
#### view option(--details \<id\>, latest)
`view`コマンドを以下のように使用すると、特定の提出結果や最新の提出結果を詳細表示できます：
```bash
local-leaderboard view --detail <id>
```
もしくは
```bash
local-leaderboard view --detail latest
```

以下は実行結果の例です：
<div align="center">
<img src="./images/view_detail_id.png" alt="View Id Details">
</div>


- **概略**\
  上部は概略を表しています。

- **詳細結果**\
  下部は詳細を表しています。各テストケースのスコアや相対スコアの情報が表示されます。以下はその詳細結果の見方です：

| 項目名| 説明|
| :-: | - |
| **Test Case**|テストケースの名前です。|
|**Absolute Score**|各テストケースの絶対スコアです。<br>Noneになっているテストケースは点数計算が失敗したことを表しています。|
|**Score Diff**|現在のトップスコアとの差分を表します。<br>Noneになっているテストケースは点数計算が失敗したことを表しています。|
|**Relative Score**|各テストケースの相対スコアです（最も高いスコアが`10^9`となります）。|

---
#### view option(--details top)
`view`コマンドを以下のように使用すると、現在のトップスコアの各テストケースごとの詳細が表示されます。

```bash
local-leaderboard view --detail top
```

以下は実行結果の例です：
<div align="center">
<img src="./images/view_detail_top.png" alt="View Top Details">
</div>

| 項目名| 説明|
| :-: | - |
| **Test Case**|テストケースの名前です。|
|**Absolute Score**|各テストケースの絶対スコアです。|
|**Id**|このスコアが取得された提出IDを表します。|


## License
This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
