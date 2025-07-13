# RFID Reader UNIT

<img src="https://github.com/akita11/RFID_ReaderUNIT/blob/main/RFID_ReaderUNIT1.jpg" width="240px">

<img src="https://github.com/akita11/RFID_ReaderUNIT/blob/main/RFID_ReaderUNIT2.jpg" width="240px">

<img src="https://github.com/akita11/RFID_ReaderUNIT/blob/main/RFID_ReaderUNIT3.jpg" width="240px">

## 内容

Felica対応のRFIDリーダICのForSinVe社FSVP532（よく使われるNXP社のPN532互換）を使ったRFIDリーダです。M5Stack等のマイコンとGroveケーブル（I2C通信）で接続して、FelicaやNFCを読み書きすることができます。PN532用のライブラリで使用することができます。（UIFlow用のカスタムブロックを用意する予定）


## 使い方

ArduinoやM5Stack等のマイコンにGroveポート経由でI2C接続します。
ソフトウエアはは、PN532用のもの使用します。
PN532用のソフトウエアとしては、Arduino用ライブラリがいくつかあります。
例えばAdafruitやSeeedのものがありますが、Felicaを読み出す関数とサンプルプログラムは提供されていないようです。
[こちら](https://github.com/elechouse/PN532)のライブラリは、これらを元にしたもの（fork）で、Felica関連の関数やサンプルプログラムも含まれているので、こちらを利用するとよいでしょう。
ただしサンプルプログラムは、PN532をI2C接続して使用する設定にはなっていませんので、冒頭の以下の「※」のところを変更します。これにより、I2C接続で使用できるようになります。
```FeliCa_card_read.pde
#if 0 // <--- ※original:1
  #include <SPI.h>
  #include <PN532_SPI.h>
  #include <PN532.h>

PN532_SPI pn532spi(SPI, 10);
PN532 nfc(pn532spi);
#elif 0
  #include <PN532_HSU.h>
  #include <PN532.h>

PN532_HSU pn532hsu(Serial1);
PN532 nfc(pn532hsu);
#else
  #include <Wire.h>
  #include <PN532_I2C.h>
  #include <PN532.h>

PN532_I2C pn532i2c(Wire);
PN532 nfc(pn532i2c);
#endif
```

なお稀に電源ON時のリセット(POR; Power On Reset)が効かず、初期化に失敗することがあるようです。その場合は、電源を入れなおしてください。


## 電波関連法令の規格について

RFIDリーダは無線通信機器ではなく「誘導式読み書き通信設備」というカテゴリに含まれます。
そのため、無線通信機器の認証に必要な、いわゆる技適は無関係です。
（[法令関連の情報まとめの例](http://dsas.blog.klab.org/archives/2018-04/52291765.html)）
「誘導式読み書き通信設備」は、法令の要件（電界強度の規定、または総務大臣型式指定）を満たせば許可不要で使用することができる、と規定されています。
その要件のうちの「電界強度の規定」（3mの距離における電界強度が500μV/m（≒54dBμV/m）以下）を満たしていることの表示方法については明記されていません。
そのため、測定条件や測定データ等の客観的なデータを示すことで、その要件を満たす、というのが一般的な解釈と考えています。
例えば（株）スイッチサイエンスで販売している[RFID2 Unit](https://www.switch-science.com/products/8301)では、電界強度の測定法・測定結果を示し、それに基づいて規定を満たしている、と表示しています。

このRFID Reader UNITの電界強度測定の測定法・測定結果は「RFID_ReaderUNIT_meaasure.pdf」に記載の通り、これは法令の要件である電界強度の規定を満たしています。
なお今回のアンテナ設計手順をまとめた資料は、AntennaDesign/以下にあります。


## Author

Junichi Akita (@akita11) / akita@ifdl.jp
