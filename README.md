# アトリエとなりの（AtelierTonarino）

https://johntonarino.github.io/AtelierTonarino/

## 構成

```
index.html
assets/   style.css / main.js / icon.png / ogp.png / fonts/
data/     works.json（つくったもの） / log.json（実験ログ）
media/    works/<id>/thumb.webp, video.mp4, image.png
          log/<id>.webp
tools/    media.py（画像・動画の変換） / build_fonts.py（フォントの間引き）
```

## 作品を追加する

1. 変換して置く（id は小文字とハイフン）
   ```
   python tools/media.py add new-work --thumb 元画像.png --video 録画.mp4
   ```
   静止画の作品は `--video` の代わりに `--image 原寸.png`。
2. `data/works.json` に1行足す
   ```json
   { "id": "new-work", "ja": "新しい作品", "title": "NewWork", "year": 2026, "kind": "shader", "media": "video", "tags": ["GLSL"] }
   ```
   - `kind`: `shader` / `3d` / `goods`（絞り込みの分類）
   - `media`: `video` / `image`。省略すると拡大表示なし
   - `event`: カード右上のバッジ（例 `"Vket 2026W"`）。任意
   - `booth`: `true` でショップトップ、URL を書けば商品ページへの「BOOTHで見る」。任意
   - サムネがまだ無いと「画像準備中」の枠が出る
3. 新しい漢字が増えたら `python tools/build_fonts.py`

「今日の一枚」は `kind: shader` で `media` があり、`booth` がない作品から日替わりで選ばれます。

## 実験ログを追加する

`data/log.json` に1件足す。スクショがあれば
```
python tools/media.py log 2026-winter --image スクショ.png
```
して、その項目に `"image": true`（または `"image": "パス"`）。無ければ文字だけのカードになります。

## 手元で確認する

`fetch` で JSON を読むので、ファイルを直接開くのではなくローカルサーバー経由で。
```
python -m http.server 8000
```
→ http://localhost:8000/

## ライセンス

- フォント: Dela Gothic One / Zen Maru Gothic / Yomogi — SIL Open Font License 1.1（`assets/fonts/OFL-*.txt`）
- それ以外（コード・画像・動画）: © Atelier Tonarino. All rights reserved.
