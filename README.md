# reed
Reed is Easy Debug module for Ren'Py.  
*RE*npy *E*asy *D*ebug module

Authorized by [MTTLDev](https://github.com/mttldev).

# 実行に際して
基本的に`Ren'Py 8`での実行を想定しています。  
通常のPythonとしての実行も可能なように調整しているように見えるかもしれませんが、これはあくまでもLint対策です。  
通常のPython環境で動作するかどうかはわかりません。

# 使い方
## インストール
1. Ren'Pyのプロジェクトフォルダの中の`game`フォルダに、このレポジトリをクローンしてください。
2. `pip install --target game/python-packages websockets`と入れて、`game/python-packages`に`websockets`をインストールしてください。

## 実行
`reed`を実行するには、Ren'Pyのゲームスクリプト内で、実行することを明示的に記載する必要があります。

```renpy
python:
    import reed
    reed.run()
```

実行を行うには最低限、上記のコードが必要です。  
これを行うことで、デフォルトでは`35124`ポートでWebSocketを待ち受けます。(`run`関数の`port`引数に対してポートを指定するとカスタマイズできます)  
あとはWebSocketクライアントを用いて、`ws://localhost:35124`に接続することで、デバッグを行うことができます。

また、デバイスによってはネットワークの仕様に制限がかかっている場合があります。  
（iOS/iPadOSでは初回実行時にネットワーク通信に関するアラートが表示される可能性があります。また、Emscriptenでは使用できません。）

## クライアント
`client.py`を実行することで簡易クライアントが使用できます。
