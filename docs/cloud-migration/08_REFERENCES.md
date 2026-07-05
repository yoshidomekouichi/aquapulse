# 📚 参考資料・実装事例

**ESP32 + 水槽モニタリングの実装事例集**

---

## 🌟 **注目のGitHub実装事例**

### **1. Smart Aquarium Control（2026年更新中）**

**URL**: https://github.com/Armaan4477/Smart-Aquarium-Control

**構成**:
```
ESP32 + DS18B20×2（内部/外部温度）+ 4チャンネルリレー + OLED
```

**機能**:
- ✅ Webダッシュボードでリアルタイム監視
- ✅ スケジュール管理（照明、ポンプ自動制御）
- ✅ 温度異常時のメール通知
- ✅ センサーキャリブレーション機能

**稼働状況**:
- 20秒ごとに内部温度測定
- 60秒ごとに外部温度測定

**参考価値**: コード全体が公開されており、実装の参考になる

---

### **2. AquaPi（Home Assistant統合）**

**URL**: https://github.com/TheRealFalseReality/AquaPi

**構成**:
```
ESP32 + DS18B20（複数対応）+ Atlas Scientific EZO（pH等）
ESPHome + Home Assistant統合
```

**特徴**:
- ✅ OTA（WiFi経由）アップデート対応
- ✅ 複数センサーをindex指定で管理
- ✅ Home Assistantで自動化

**参考価値**: OTAアップデートの実装例として最適（将来的なUSB接続不要化）

---

### **3. aquaeye（ESP32-C3使用）**

**URL**: https://github.com/alexantao/aquaeye

**構成**:
```
ESP32-C3 Supermini + DS18B20 + pH + 水位センサー + 照度センサー
Home Assistant統合 + オフライン表示（ディスプレイ）
```

**特徴**:
- ✅ カスタムPCB設計
- ✅ センサー保護回路（ショート対策）
- ✅ Home Assistantとオフライン表示の両立

**参考価値**: ハードウェア設計の参考、センサー保護の考え方

---

### **4. smart-aquarium-iot-analytics-platform（フルスタック）**

**URL**: https://github.com/YasinduKaveesha/smart-aquarium-iot-analytics-platform

**構成**:
```
ESP32 + センサー → MQTT → FastAPI → MongoDB → React
機械学習: 異常検知（Isolation Forest）+ 予測（SARIMA）
```

**技術スタック**:
- ESP32 + pH/温度/TDS/濁度センサー
- MQTT（Eclipse Mosquitto）
- FastAPI + MongoDB
- React + TypeScript + Tailwind CSS
- 機械学習（scikit-learn, statsmodels）

**参考価値**: モダンなデータスタック、機械学習統合の実例

---

## 📝 **日本語技術ブログ**

### **1. HomeMadeGarbage: 金魚水槽監視システム**

**URL**: https://homemadegarbage.com/ai14

**構成**:
```
ESP32 + ESP32-CAM + DS18B20 + pHセンサー + UnitV（AI）
```

**機能**:
- 水温/pH測定
- Webサーバでブラウザ表示
- LED輝度調整
- AI（UnitV）で金魚認識

**運用実績**: 2-3年間稼働中（記事は2019年頃から）

**参考価値**: 日本語ドキュメント、長期運用の実例

---

### **2. tohrusan: メダカ水槽（2年間のデータ蓄積）**

**URL**: https://tohrusan.com/blogs/83/iot-raspberrypi-ds18b20/

**構成**:
```
Raspberry Pi + DS18B20（ESP32でも同じセンサー）
```

**運用実績**:
- 2020年の1年間の水温データ収集
- センサーは2年間問題なく動作
- 季節ごとの水温推移を可視化

**実践的な知見**:
> 「コケがよく付着するので、こまめに掃除が必要」

**参考価値**: 長期運用の現実的な課題、メンテナンスのアドバイス

---

## 🎓 **学術論文**

### **1. IoT-Enabled Smart Aquarium System（2026年1月）**

**URL**: https://arxiv.org/html/2601.08484v1

**構成**:
```
ESP32 + pH/TDS/温度/濁度センサー + Blynk IoT
サーボ自動給餌機 + 水ポンプ制御
```

**実験結果**:
- ✅ 96%の平均センサー精度
- ✅ 1.2秒の異常検知応答時間
- ✅ 97%の自動制御信頼性

**結論**:
> 「低コストIoTソリューションで水槽管理を革新できる」

**参考価値**: 性能指標の参考、学術的な有効性の実証

---

### **2. Semar AquaConnect: Closed-Loop IoT System（2026年）**

**URL**: https://journal.unm.ac.id/index.php/JESSI/article/view/11782

**構成**:
```
ESP32 + 温度/pH/溶存酸素/TDS/水位センサー
リレー制御（ポンプ、エアレーション、ヒーター）
Webダッシュボード + Telegram Bot
```

**実験結果**:
- 温度: 平均誤差 0.12°C
- pH: 平均誤差 0.33
- 溶存酸素: 平均誤差 0.08 mg/L
- 応答遅延: 0.85〜1.42秒

**参考価値**: ナマズ養殖での実用例、クローズドループ制御の参考

---

## 🔧 **公式チュートリアル**

### **Random Nerd Tutorials: ESP32 + DS18B20**

**URL**: https://randomnerdtutorials.com/esp32-ds18b20-temperature-arduino-ide/

**内容**:
- DS18B20の配線方法（詳細図解）
- Arduino IDEでのコード例
- 複数センサーの扱い方
- Webサーバ統合

**参考価値**: 初心者向けの丁寧な解説、トラブルシューティング

---

### **ESP32.co.uk: DS18B20 + Home Assistant（2026年版）**

**URL**: https://esp32.co.uk/esp32-ds18b20-with-home-assistant-esphome-mqtt-complete-2025-guide/

**内容**:
- ESPHome設定（YAML）
- Home Assistant統合
- MQTT連携
- 複数センサーの管理

**参考価値**: ESPHome + Home Assistantの最新情報

---

## 🎯 **標準構成パターン**

### **共通する設計パターン**

| 要素 | 標準構成 |
|------|----------|
| **センサー** | DS18B20（防水版） |
| **配線** | GPIO + 4.7kΩプルアップ抵抗 |
| **測定間隔** | 20-60秒 |
| **データ送信** | HTTP POST / MQTT |
| **クラウド** | Blynk / Home Assistant / カスタムバックエンド |
| **可視化** | Webダッシュボード / Grafana / モバイルアプリ |

---

## 📊 **あなたの実装の位置づけ**

```
趣味レベル:
  ESP32 + DS18B20 + Webサーバ（ローカルのみ）

中級レベル:
  ESP32 + DS18B20 + Blynk/Home Assistant（クラウド連携）

あなたの設計（本プロジェクト）:
  ESP32 + DS18B20 + GCP（BigQuery + Grafana Cloud）
  → エンタープライズレベルのデータスタック
  → スケーラブル、拡張性高い
  → 学習価値が非常に高い
  → 将来的な機械学習統合も視野
```

---

## 💡 **実装事例から学べること**

### **1. OTAアップデートは重要**

**事例**: AquaPi, ESPHome

**学び**:
- WiFi経由でコード更新可能
- USB接続不要になる
- Phase 2以降で導入を検討

---

### **2. センサーのメンテナンスは必須**

**事例**: tohrusan（メダカ水槽）

**学び**:
- 水槽内のセンサーにはコケが付着
- 定期的な掃除が必要
- センサー保護回路も検討価値あり

---

### **3. 異常検知・予測は有用**

**事例**: smart-aquarium-iot-analytics-platform

**学び**:
- 機械学習で異常検知（Isolation Forest）
- 時系列予測（SARIMA）でメンテナンス計画
- Phase 3（機械学習）の参考になる

---

### **4. 複数センサーの管理**

**事例**: Smart Aquarium Control, AquaPi

**学び**:
- DS18B20は複数接続可能（同じGPIO）
- センサーIDで識別
- キャリブレーション機能が重要

---

## 🔗 **関連リンク**

### **コミュニティ・フォーラム**

- **ESP32 Forum**: https://www.esp32.com/
- **Reddit r/esp32**: https://www.reddit.com/r/esp32/
- **Reddit r/Aquariums**: https://www.reddit.com/r/Aquariums/

### **公式ドキュメント**

- **ESP32 公式**: https://www.espressif.com/en/products/socs/esp32
- **MicroPython**: https://docs.micropython.org/en/latest/esp32/quickref.html
- **DS18B20 Datasheet**: https://datasheets.maximintegrated.com/en/ds/DS18B20.pdf

### **ツール・ライブラリ**

- **ESPHome**: https://esphome.io/
- **Thonny IDE**: https://thonny.org/
- **ampy**: https://github.com/scientifichackers/ampy

---

## ✅ **結論**

- ESP32 + DS18B20での水槽モニタリングは**実証済みの定番構成**
- 日本でも金魚・メダカ水槽で長期運用実績あり
- 学術論文でも2026年に有効性が実証されている
- あなたの設計は「趣味レベル」を超えた**プロダクショングレード**

**→ 自信を持って進めて大丈夫です！**

---

**戻る**: [README.md](README.md) | **トラブルシューティング**: [07_TROUBLESHOOTING.md](07_TROUBLESHOOTING.md)
