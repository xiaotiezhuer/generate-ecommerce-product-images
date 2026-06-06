# 六类电商图片提示词

## 通用规则

- 默认比例为 `1:1`，默认只生成 6 张方图。
- 只有用户明确要求平台或比例时，才增加 `3:4`、`4:5`、`16:9` 等版本。
- 每张图使用一次独立 ImageGen 调用。
- 每个提示词都列出输入图角色、产品指纹、不可变项和禁止项。
- 需要文字时逐字引用；不得自行添加价格、销量、认证或功效。

## 通用提示词骨架

```text
Use case: product-mockup 或 ads-marketing
Asset type: <图片类型与平台用途>
Primary request: <本张图片唯一销售任务>
Input images:
- Image 1: main-identity，商品身份参考
- Image 2: alternate-angle 或 detail-reference
Product fingerprint: <轮廓、比例、部件、方向、颜色、材质、纹理、Logo>
Scene/backdrop: <环境>
Composition/framing: <比例、机位、主体位置、留白>
Lighting/mood: <光线和情绪>
Text (verbatim): "<准确文字>" 或 none
Fidelity: A，严格保持商品结构
Constraints: <必须保留>
Avoid: <结构漂移、虚构附件、水印、乱码、无依据卖点>
```

## 01 白底或净背景主图

销售任务：快速、准确地看清商品。

```text
Use case: product-mockup
Asset type: ecommerce main image, 1:1 square
Primary request: create a clean product-first catalog image
Scene/backdrop: pure white or category-appropriate very light neutral background
Composition/framing: complete product, centered, 70-82% frame occupancy, no cropping
Lighting/mood: soft controlled studio light, realistic contact shadow
Text (verbatim): none
Fidelity: A
Constraints: preserve exact silhouette, proportions, components, orientation, color and texture
Avoid: props, hands, packaging not supplied, extra parts, dramatic reflections, text, logo invention, watermark
```

## 02 品牌氛围图

销售任务：建立价格感、风格和情绪价值。

```text
Use case: ads-marketing
Asset type: premium ecommerce atmosphere image, 1:1 square
Primary request: place the exact product in the visual-brief's strongest researched setting
Scene/backdrop: use one coherent, category-relevant environment; keep props subordinate
Composition/framing: product remains the dominant subject with intentional negative space
Lighting/mood: match the researched price position and material
Text (verbatim): none unless the user explicitly asks
Fidelity: A
Constraints: props must be plausible and must not imply included accessories
Avoid: copying a named competitor, clutter, misleading scale, structural redesign, watermark
```

## 03 材质工艺细节图

销售任务：用可见细节证明材质和工艺。

```text
Use case: product-mockup
Asset type: ecommerce craft detail macro, 1:1 square
Primary request: show one real, reference-supported material or construction detail
Input images: prioritize detail-reference images for the selected area
Composition/framing: macro close-up with enough context to identify where the detail belongs
Lighting/mood: raking or soft directional light that reveals true texture
Text (verbatim): none
Fidelity: A
Constraints: reproduce the real texture scale, joint, edge and color variation
Avoid: invented engraving, repeated fake texture, excessive sharpening, unrelated decorative detail
```

## 04 寓意文字图

销售任务：把可见造型、用途或文化联想转成简短正向寓意。

文案规则：

- 主文案优先 4–8 个汉字。
- 可增加一行不超过 8 个汉字的辅助文案。
- 寓意可以创作，但不得伪装成产品功效或事实。

```text
Use case: ads-marketing
Asset type: Chinese meaning-copy ecommerce poster, 1:1 square
Primary request: combine the exact product with restrained culturally appropriate typography
Composition/framing: product dominant; reserve a clean text zone; no text over critical product details
Text (verbatim):
- Main: "<4-8 Chinese characters>"
- Support: "<optional exact short line>"
Typography: readable Chinese calligraphy or serif style matched to the category
Fidelity: A
Constraints: render every Chinese character exactly once and keep it legible
Avoid: invented seals, extra copy, misspelled characters, fake certifications, watermark
```

若文字第一次失败，只缩短文案并简化字体重试一次。仍失败时生成无字底图，保留排版安全区，并在报告中提供准确文案。

## 05 真实使用场景图

销售任务：解释使用方式、环境和尺寸关系。

```text
Use case: photorealistic-natural
Asset type: ecommerce usage scene, 1:1 square
Primary request: show the exact product being used in a physically plausible real-life context
Scene/backdrop: category-appropriate, researched setting
Composition/framing: keep product readable; hands or people only when they clarify use
Lighting/mood: natural or softly staged commercial light
Text (verbatim): none
Fidelity: A
Constraints: preserve realistic scale, grip, orientation and operating state
Avoid: unsafe use, impossible physics, misleading included accessories, obscured product, structural redesign
```

## 06 卖点说明图

销售任务：用最多 3 个有依据的卖点降低理解成本。

卖点来源优先级：

1. 用户明确提供并可确认的信息。
2. 多角度图片中直接可见的结构或材质特征。
3. 可靠来源支持的通用品类事实。

```text
Use case: ads-marketing
Asset type: ecommerce selling-points graphic, 1:1 square
Primary request: explain up to three evidence-backed product features
Composition/framing: one clear product view, restrained callouts, generous spacing
Text (verbatim):
- "<卖点 1>"
- "<卖点 2>"
- "<卖点 3>"
Fidelity: A
Constraints: each callout must point to a visible or supplied fact; text must be exact
Avoid: unverifiable material purity, origin, handmade, heritage, safety, medical, performance or sales claims
```

没有可靠卖点时，使用可见特征描述，例如“圆润壶身”“锤目肌理”“提梁设计”，不要补造认证或功效。

## 额外比例

用户明确要求额外比例时：

- 为每个比例重新组织构图和文字安全区。
- 不用机械裁切破坏商品完整性或文字。
- 文件名使用 manifest 中的比例后缀。
- 保持同一视觉简报和产品指纹。
