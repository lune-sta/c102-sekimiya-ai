# sekimiya-ai-langchain

C102 Labotic;Gate らぼらいふっ！掲載「OpenAI APIとLangChainを使ったDiscord Bot開発」のサンプルコードです。

## 使用方法
1. [rye](https://rye-up.com/guide/installation/) をインストールしていない場合は、インストールします。
2. このレポジトリをcloneします。
```
$ git clone git@github.com:lune-sta/c102-sekimiya-ai.git
$ cd c102-sekimiya-ai
```
3. 環境変数ファイルをコピーし、自分のトークンで書き換えます。各種トークンについては自分で各サービスから取得する必要があります。
```
$ cp .env.sample .env
$ vim .env
```
4. 以下のコマンドで起動します。
```
$ rye sync
$ rye run python src/sekimiya_ai_langchain/bot.py
```

## サポート
本誌をお買い上げの方で、本ソースコードにご不明な点がある方は [@lune_sta](https://twitter.com/lune_sta) までご連絡ください。
