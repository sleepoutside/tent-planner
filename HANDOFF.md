# 帳篷 × 營位 3D 搭設模擬：交接文件

給之後接手這個專案的人或 AI。先讀完「一定要知道的五件事」，再動手。

最後更新：2026-11-19

## 一定要知道的五件事

1. **`types.html`、`tarps.html`、`fire.html`、`sleep.html`、`weather.html` 是產生出來的，不要直接改。** 要改就改 `tools/tpl/` 裡的範本，再跑 `python3 tools/build.py`。直接改這三個檔，下次產生時會被蓋掉。
2. **`index.html` 是所有 3D 造型的唯一來源。** 另外三頁的帳篷、人物、車子造型，都是 `tools/build.py` 從 `index.html` 複製過去的。改了 `index.html` 裡的造型函式或 `TENTS` 資料，就要重跑 `tools/build.py`。
3. **每次改完要推兩個分支**：`main` 和 `gh-pages`。目前不確定 GitHub Pages 用哪一個，所以兩個都推（指令見下方）。
4. **不可複刻真實產品的外觀。** 品牌帳款只使用廠商公布的尺寸，3D 外型一律是依結構類型做的通用造型；車子也是通用車型，不仿特定車款。這是站主的明確要求。
5. **每頁都要保留署名與聲明**：「設計/Sleepoutside Camp *非營利使用」與「資訊僅供參考，請依官方資訊為準」。

## 專案概況

- 站主品牌：Sleepoutside Camp（GitHub 帳號 `sleepoutside`）
- Repo：`sleepoutside/tent-planner`
- 線上網址：`https://sleepoutside.github.io/tent-planner/`
- 對象：台灣露營者，介面全為繁體中文；說明文字語氣輕鬆、口語
- 技術：純靜態網頁。每頁是單一 HTML 檔，內含 CSS 與一個 IIFE 的原生 JavaScript（ES5 風格、無框架、無建置工具）。3D 用 three.js r128，從 cdnjs 載入

## 檔案

| 檔案 | 說明 |
|---|---|
| `index.html` | 搭設模擬（主頁，約 2,000 行）。手寫，直接編輯 |
| `types.html` | 帳型 3D 介紹與優缺點（11 種帳型＋2 種天幕）。**產生檔** |
| `tarps.html` | 天幕搭法 3D 介紹（8 種）。**產生檔** |
| `fire.html` | 焚火安全模擬。**產生檔** |
| `sleep.html` | 帳內睡鋪模擬。**產生檔** |
| `weather.html` | 營地天氣模擬。**產生檔** |
| `og-*.jpg` | 各頁的分享預覽圖（1200×630） |
| `tools/build.py` | 由 `index.html` + 範本產生上面三個頁面 |
| `tools/tpl/types_head.html`、`types_tail.js` | 帳型頁範本（HTML/CSS/資料，與尾段程式） |
| `tools/tpl/tarps.html`、`fire.html`、`sleep.html`、`weather.html` | 天幕搭法頁、焚火頁、睡鋪頁、天氣頁範本，內有 `/*BUILDERS*/`（及 `/*DATA*/`）佔位符 |
| `tools/smoke.py` | 冒煙測試：六頁 × 電腦／手機尺寸，檢查 JS 錯誤與水平溢出 |
| `tools/make_og.py` | 重新產生分享預覽圖 |
| `README.md` | 功能清單（對外） |

站外另有一份給使用者的《使用說明》文字檔，不在 repo 內，由站主保管；新增功能時要請站主一併更新。

## 日常流程

```bash
# 1. 改 index.html 或 tools/tpl/ 裡的範本
# 2. 重新產生三個頁面
python3 tools/build.py
# 3. 測試（機器連不到 cdnjs 時，用 THREE_JS 指向本機的 three.min.js r128）
THREE_JS=/path/to/three.min.js python3 tools/smoke.py
# 4. 提交並推到兩個分支
git add -A && git commit -m "..." && git push origin main && git push origin main:gh-pages
```

測試需要 Python 的 playwright 與 Google Chrome（無 GPU 時用 swiftshader，參數已寫在腳本裡）。冒煙測試只檢查「載得起來、沒有錯誤、手機不會橫向捲動」；功能要另外寫針對性的測試或手動操作。改 `index.html` 前後，先把 `<script>` 內容抽出來跑 `node --check` 可以很快抓到語法錯誤。

**尚未驗證的部分**：所有手機行為都只在模擬的手機尺寸測過，沒有在真實手機上驗證。拖曳、分享連結的自動複製、存圖最可能在實機出問題。

## index.html 的結構

程式依註解分段（搜尋 `/* ----------`）：資料 → three 設定 → 幾何工具 → 營位 → 環境與天氣 → 帳篷 → 帳內睡鋪 → 天幕 → 寵物 → 桌椅燈與焚火台 → 包區模式 → 放置判斷 → 鏡頭 → 手機選單 → 指標操作 → UI → 瀏覽次數 → 網址參數 → 啟動。

### 資料表

- `TENTS`：品牌帳款（尺寸為廠商公布的搭設外尺寸，單位公分）＋通用帳型（`brand:'通用'`）＋最後一筆 `custom`。欄位：`id, brand, name, L, W, H, shape, color, note`；有原廠內帳數字的另有 `inner:{l,w,from}`；`full:true` 表示 L×W 本身就是內帳尺寸。
- `shape` 可用值：`dome, domeVest, tworoom, tunnel, bell, cabin, carside, pyramid, air`。
- `TARPS`（天幕）、`CARS`（通用車型輪廓）、`SITE_TYPES`、`PRESETS`、`ENVS`（草地／森林／河邊／海邊／高山）、`WX`（天氣與時段）、`COATS`／`PET_SIZE`、`CHAIR_SIZE`／`TABLE_SIZE`、`MATS`（床墊）、`PROPS`（兩張椅子、桌子、汽化燈、焚火台）。

### 狀態

- `S`：單一營位模式的全部狀態（帳篷、旋轉與位置、營位長寬與類型、環境、天氣、車、人、寵物、天幕、睡鋪等）。
- `slot2`：第 2 頂帳篷。`CUSTOM2` 是它的自訂尺寸。
- `AREA`：包區包場模式的物件清單，存在 localStorage，鍵名 `tentPlannerArea_v1`。

### 重要機制

- **帳篷只有一個建構函式 `buildTent1()`**，它讀寫全域變數（`S.tent`、`tentG`、`tentMeshes`、`shellMat` 等）。第 2 頂帳篷與包區模式的多頂帳篷，都是「把狀態換進去、建好、再換回來」（`swap2`／`with2`、包區的 `swapS`）。新增帳型時只要在 `buildTent1()` 加一個 `shape` 分支。
- **`MOVERS`**：所有可拖曳物件的登記表（`name, has, pos, set, turn, center`）。新增可移動的物件要在這裡登記，`pick()` 才點得到，上方「操作：○○」下拉選單才會出現。
- **放置判斷**：`updateFit()` 產生上方結果列，內部呼叫 `tentFit()`、`tarpCheck()`、`fireCheck()`（焚火台 3 m／4.5 m）、`matCheck()`（睡鋪）。帳篷重疊用 `bodyRect()` + `rectsOverlap()`（只算帳體，不算營繩）。
- **render-on-dirty**：畫面只有在 `redraw()` 被呼叫後才重畫；下雨、水面等動畫用 `anim`／`tick(dt)`。
- **網址參數**：
  - `#type-<id>`：從帳型頁帶入帳型（`applyTypeHash`）；`#tarp-hexa`／`#tarp-rect`：帶入自訂天幕。
  - `#s=<base64url JSON>`：單一營位分享連結（`singleData`／`singleApply`）。
  - `#a=<base64url JSON>`：包區分享連結（`areaData`／`areaReplace`）。
  - 讀取分享資料時所有數值都經過範圍限制；格式壞掉會跳提示而不是讓頁面出錯。**改動 `S` 的欄位時，記得同步更新 `singleData` 與 `singleApply`，並保持舊連結可讀。**
- **手機版（寬度 ≤ 900px）**：場景全螢幕；`.panel` 是底部選單，用 `display` 切換。不要改成 `transform` 動畫，iOS 會出現選單空白的繪製問題。選單打開時場景縮到上方（`body.sheet-open`）。
- **包區模式上限**：帳篷 10、天幕 3、車 10；每頂帳篷配 2 人、2 椅、1 桌、1 寵物、1 燈。焚火台與帳內睡鋪目前只支援單一營位模式。

## 其他頁面

導覽方塊：除了 `index.html` 自己手寫一份之外，其他頁的導覽方塊與樣式由 `tools/build.py` 的 `CARDS`／`NAVCSS` 統一產生（範本裡的 `/*NAV*/`、`/*NAVCSS*/`）。**新增頁面時，在 `CARDS` 加一筆，並手動更新 `index.html` 的 `.navcards` 與手機版 `.qlink`。**

各頁共用同一套寫法：自己的場景與鏡頭，加上一組「假的」全域變數（`S`、`WX`、`siteY`、`isArea()`、`placeTent()` 等）讓複製過來的 `buildTent1()` 能運作。若 `buildTent1()` 之後用到新的全域變數，每個範本都要補上對應的假變數，否則該頁會壞（`tools/smoke.py` 會抓到）。

- **types.html**：`TYPES` 資料含 11 種帳型與 2 種天幕的尺寸、六項評分、優缺點。車頂帳只在這頁展示，不進搭設模擬。按鈕連到 `index.html#type-<id>`；天幕連到 `index.html#tarp-hexa`／`#tarp-rect`。
- **tarps.html**：`PITCHES` 每筆是一種搭法，用 `net`（布面控制點，公尺）、`poles`、`ropes`、`pegs` 描述，`buildPitch()` 依此畫出布面、營柱、營繩。**新增搭法只要在 `PITCHES` 加一筆資料**，不用改造型程式。`net` 可以有兩排以上（蝶形天幕用四排，兩端各一排重合的點當尖端）；`car:[x,z]` 會放一台車。這頁目前沒有「帶進搭設模擬」的按鈕。
- **fire.html**：六種焚火台、五種燃料、風向風力；判斷邏輯在 `judge()`。
- **sleep.html**：內帳範圍由 `sleepArea()`（複製自 `index.html`）決定；床墊可混搭、拖曳、轉向，`autoArrange()` 自動排列。
- **weather.html**（營地天氣模擬，2026-11-19 第一階段）：
  - **資料都來自另一個 repo `sleepoutside/hero-camping-map`（勇者露營天氣查詢）**，同網域直接讀：`places.json`（熱點與營地清單，營地索引與天氣站的 `?camp=` 一致）、`cwa.json`（氣象署鄉鎮預報）、`om_hot.json`（熱點的 Open-Meteo 預報，含多模型雨量，由那邊的 GitHub Actions 排程每 6 小時更新）。在 `*.github.io` 用相對路徑 `/hero-camping-map/`，其他地方（含本機 file://）用完整網址。
  - 熱點優先用 `om_hot.json`（12 小時內且有風向欄位才用）；營地或資料過期時即時向 Open-Meteo 抓單點每小時資料，多模型雨量另外抓、晚到也沒關係。
  - 時間軸：週五 12:00 到週日 12:00（已過的部分從現在開始），一律用台灣時間的字串鍵 `YYYY-MM-DDTHH:00`（`keyMs`／`msKey`），不依賴瀏覽器時區。
  - 太陽位置 `sunPos()` 依經緯度計算；場景北方是 -z、東方是 +x。風向是「風從哪裡來」（氣象慣例），畫箭頭與雨絲時要加 180°。
  - 網址參數：`?camp=<索引>` 或 `?hot=<鄉鎮名>`，加 `&h=MM-DD-HH` 指定時間。天氣站冒險情報的「3D 天氣模擬」按鈕會帶 `camp`／`hot` 過來。
  - 分享預覽圖 `og-weather.jpg`：`tools/make_og.py weather` 需要能連到天氣站與 Open-Meteo 才畫得出天氣，連不到時頁面只會顯示讀取訊息。
  - **第二階段（2026-11-19）：帶入自己的配置**
    - 搭設模擬的分享視窗有「☔ 看這個配置的週末天氣」，開 `weather.html#s=<與分享連結相同的編碼>`。天氣頁用 `buildLayout()` 還原：帳篷、第 2 頂帳篷（`swapS`）、天幕（`buildTarp1`）、車、人、桌椅燈與焚火台（`buildProp`），這些函式與 `TENTS`／`TARPS`／`PROPS` 等資料都由 `tools/build.py` 從 `index.html` 複製。寵物與帳內睡墊沒有還原。包區包場（`#a=`）不支援，會顯示說明並改用通用示意。
    - **門口方向的約定**：所有帳型的門口都當成帳篷自己的 +x 方向（長邊前端，與模擬器擺天幕的預設方向一致）。使用者用 8 個方位鈕設定門口朝向，整個營位（`layG`）跟著轉；天氣、樹、指北針固定不動。網址參數 `o=<方位角>`。
    - 判斷都在世界座標算：`wetAt()`（雨滴斜率 = 風速 / 7，從天幕高度往上風回推，看是否落在天幕投影內）、`shadeAt()`（依太陽方位與仰角推天幕影子）、`doorWind()`（門口方位與風來向夾角 ≤45° 迎風、≤100° 側風）、焚火台下風 35° 扇形 6 m 內有帳篷或天幕就提醒。天幕投影用矩形或六角形近似，`TP.He` 取邊緣與最高點的平均高度。這些都是簡化估算，不是流體模擬。
    - `bestDoor()`：以陣風平方加權平均整個週末的風來向，建議門口朝反方向；風向太分散時說「風向不定」。
    - 錄影 `recStart()`：用 MediaRecorder 錄一張合成 canvas（3D 畫面＋字幕＋迷你時間軸），錄影時暫時把繪圖解析度提高到 1280 寬、拿掉地上的風向標籤；優先 MP4（H.264，LINE 可播），不支援才用 WebM。
    - 月亮 `moonInfo()` 為低精度公式（誤差約 1–2 度、相位幾個百分點），月相圖畫在 canvas 上；夜間有月亮時主光改成月光。結露水珠 `buildDew()` 取帳篷網格頂點，`dewRisk()` ≥1 且清晨或夜間時顯示。

## 內容來源與站主已知的限制

- **焚火安全距離**：黃圈 4.5 m 取自美國 Smokey Bear／Recreation.gov（15 英尺）；紅圈 3 m 取自日本 BE-PAL（2–3 m 的上限）；帳內不可用火依新竹縣消防局宣導。來源連結列在 `fire.html` 頁尾。風造成的安全圈拉長、火焰與火星大小是示意，不是計算結果。
- **以下數字是一般性估計，不是官方資料**，頁面上都有標示：通用帳型的尺寸、車型尺寸、營繩配置、桌椅與寵物尺寸、床墊尺寸、沒有原廠數字的內帳範圍、帳型與焚火台的評分和優缺點。
- 睡鋪只算平面長寬，不扣帳壁傾斜。

## 計數器

- **GoatCounter**：`https://tent-planner.goatcounter.com`，每頁都有載入，供站主在後台看流量。
- **畫面上的「瀏覽 N 次」**：用 Abacus（`abacus.jasoncameron.dev`，鍵 `sleepoutside-tent-planner/views`）。只在 `*.github.io` 網域下才累加，其他地方只讀取。站主要求畫面上只顯示瀏覽次數，不顯示人次。

## 分享預覽

每頁的 `<head>` 都有 `og:*` 與 `twitter:card` 標籤，圖片是 `og-*.jpg`。網址寫死為 `https://sleepoutside.github.io/tent-planner/`；若日後換網域，要改 `index.html` 與三個範本裡的網址。LINE、臉書會快取預覽，更新圖片後可能要一段時間才會生效。

## 討論過但還沒做的

- **夜晚光感**：只在夜晚加光暈與暖色調（試作過，站主暫緩）。完整的 HD-2D 像素風格評估後不建議做。
- **日照與遮蔭**：依時間與營位朝向顯示影子。
- **延長線長度**：量電箱到帳篷的距離。
- **雨天天幕排水方向**。
- **包區模式的焚火台**。
- **裝備檢查清單**。
- 車內裝載：評估後不建議做（各車款差異太大）。

## 與站主合作的習慣

- 站主說「先不要執行」、「先思考」時，只回答可行性與方案，等決定後才動手。
- 回報時要明講哪些驗證過、哪些沒有（特別是真實手機與線上網站）。
- 新功能做完，要更新 `README.md`，並提醒更新《使用說明》文字檔。
