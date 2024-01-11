# Power BIを使った自然言語処理データの可視化



## 概要

旅行情報サイト「トライシー」にて掲載された、過去6か月の記事のタイトルテキストに自然言語処理を行いPower BIでデータの可視化を行った。



## 経緯

現職でPower BIの利用を検討しているため、試しに使ってみようと思い作成。

よくある売り上げデータの可視化をするだけでは面白くないと思ったため、Pythonライブラリを使用して自然言語処理のデータを作成しPower BIで使用した。



## 完成品

airlines-article-analysis.pbix

<img src="image\完成品.PNG" alt="完成品" />



## モデルビュー

<img src="\image\モデルビュー.PNG" alt="モデルビュー" style="zoom:80%;" />



## 所感

#### データの持たせ方に一番試行錯誤した

各テーブル同士の関係がうまく連結できず、最初はグラフ同士の連動がうまくいかなかった。
そのため、元となるCSVのデータの持たせ方について何回かやり直すこととなった。
実務の際は事前にしっかりとしたテーブル設計を行う必要があると感じた。

#### 自然言語処理も業務で使えそう

ボイスボットに登録する辞書データの加工に自然言語処理が使えると感じた。
辞書データの整備の際に人間が自然に区切って話す箇所にスペースを入れる作業があるが、何十万件もあるデータ全ての適切な箇所にスペースを入れることは難しい。
今までは正規表現などを利用していたが、自然言語処理なら多少のチューニングは必要だが、より適切な箇所にスペースを入れることも出来る気がする。
