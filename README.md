# 电商产品图生成器

`generate-ecommerce-product-images` 是一个 Codex Skill，用于把一张或多张同款产品原图，自动转化为经过市场调研、产品保真检查和交付验证的电商图片套系。

它适合实体商家、手工艺品牌和电商运营人员使用。默认少提问、自动执行；只有原图无法识别、不同图片疑似属于多个 SKU，或关键信息冲突时才暂停确认。

## 主要能力

- 支持单张或多张同款产品图，包括不同角度、细节、包装和配件图。
- 自动识别商品轮廓、比例、部件、方向、材质、纹理和 Logo，建立产品指纹。
- 联网调研当前品类的热门电商视觉趋势，并区分热卖标记、互动信号、搜索靠前和纯设计参考。
- 默认调用 ImageGen 生成 7 张 `1:1` 方图。
- 新增规格尺寸图：使用用户输入的真实参数生成参数表、尺寸线和测量说明。
- 用户在调用时直接提供尺寸信息，Skill 一次性交付完整 7 张图。
- 商品保真采用 Fidelity A 优先；确实无法稳定生成时才允许受限的 Fidelity B。
- 每张图片最多进行两次定向重试，避免无限消耗生成次数。
- 自动生成调研、视觉简报、最终提示词、交付清单和质量报告。
- 使用脚本检查图片数量、比例、状态和报告完整性。

## 默认图片套系

| 编号 | 图片类型 | 作用 |
| --- | --- | --- |
| 01 | 白底或净背景主图 | 清晰、准确地展示商品 |
| 02 | 品牌氛围图 | 建立风格、价格感和情绪价值 |
| 03 | 材质工艺细节图 | 展示纹理、连接和工艺细节 |
| 04 | 寓意文字图 | 用简短中文文案表达文化寓意 |
| 05 | 真实使用场景图 | 展示使用方式、环境和尺寸关系 |
| 06 | 卖点说明图 | 展示最多 3 个有依据的产品卖点 |
| 07 | 规格尺寸图 | 展示用户确认的参数、尺寸标线和测量说明 |

默认只生成 `1:1` 方图。只有用户明确提出时，才增加 `3:4`、`4:5`、`16:9` 或其他比例。

## 安装

克隆仓库并放入个人 Codex Skills 目录：

```bash
mkdir -p ~/.codex/skills
git clone \
  https://github.com/xiaotiezhuer/generate-ecommerce-product-images.git \
  ~/.codex/skills/generate-ecommerce-product-images
```

如果目标目录已经存在，请先备份或删除旧版本，避免新旧文件混合。

## 使用

在 Codex 中上传一张或多张产品图片，然后调用：

```text
使用 $generate-ecommerce-product-images，根据我上传的产品图和以下规格尺寸，
自动调研当前热门视觉风格并生成完整七图电商套系。
口径：约6厘米
高度：约4厘米
底径：约3厘米
```

指定额外比例：

```text
使用 $generate-ecommerce-product-images 生成完整商品图，
除了默认方图，再增加适合小红书的 3:4 竖图。
```

补充品牌或产品事实：

```text
使用 $generate-ecommerce-product-images 处理这些产品图。
品牌定位为中高端中式茶器；材质为用户已确认的紫铜；
寓意文案希望表达纳福、团圆和茶事雅趣。
```

提供规格尺寸：

```text
使用 $generate-ecommerce-product-images 处理这些产品图。
品牌：归银堂
材质：足银999
容量：80毫升
口径：约6厘米
高度：约4厘米
底径：约3厘米
工艺：一张打
```

规格图至少需要一项用户确认的尺寸字段，并应在调用 Skill 时随产品图一起输入。Skill 不会根据照片估算尺寸、容量、重量、材质纯度或工艺，也不支持缺少第 07 张的部分交付。

## 工作流程

1. 检查输入图片并识别同款、多角度、细节、包装和配件。
2. 建立产品指纹，锁定不能改变的结构和外观。
3. 调研当前市场视觉趋势并记录来源与证据等级。
4. 制定统一视觉风格、场景和文案策略。
5. 创建标准交付目录和 `manifest.json`。
6. 读取用户随调用输入的规格尺寸参数。
7. 逐张调用 ImageGen 生成完整 7 张图片。
8. 检查商品一致性、文字和参数准确性、事实依据和电商可用性。
9. 完成交付报告并运行严格验证。

## 交付目录

```text
<product-name>-ecommerce-images/
├── 01-main-square.png
├── 02-atmosphere-square.png
├── 03-detail-square.png
├── 04-meaning-copy-square.png
├── 05-usage-square.png
├── 06-selling-points-square.png
├── 07-specifications-square.png
├── research.md
├── visual-brief.md
├── prompts.md
├── manifest.json
└── quality-report.md
```

## 辅助脚本

创建标准交付目录：

```bash
python3 scripts/create_delivery.py \
  ./output/product-ecommerce-images \
  --product-name "产品名称"
```

增加额外比例：

```bash
python3 scripts/create_delivery.py \
  ./output/product-ecommerce-images \
  --product-name "产品名称" \
  --ratio square \
  --ratio 3x4
```

验证交付：

```bash
python3 scripts/validate_delivery.py ./output/product-ecommerce-images
```

校验器要求全部 7 张图都存在、比例正确且状态为 `complete`；任何缺图或未完成状态都会导致验证失败。

## 保真规则

### Fidelity A

默认等级。允许更换背景、灯光、镜头和环境，但不得改变：

- 商品轮廓和比例。
- 部件数量、位置、连接方式和朝向。
- 开口、把手、壶嘴、接口等功能结构。
- 真实材质、纹理、Logo、铭文和图案。

### Fidelity B

只有 A 级经过定向重试仍无法得到可用结果时才允许使用。可轻微修整表面瑕疵、增强真实材质表现或修正很小的透视畸变，但仍不得重新设计商品。

所有 B 级图片必须在 `manifest.json` 和 `quality-report.md` 中明确标记。

## 项目结构

```text
.
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── image-set-prompts.md
│   ├── product-fidelity.md
│   ├── quality-checklist.md
│   └── research-workflow.md
├── scripts/
│   ├── create_delivery.py
│   └── validate_delivery.py
└── tests/
    └── test_delivery_scripts.py
```

## 测试

本项目的脚本仅使用 Python 标准库。

```bash
python3 -m unittest discover -s tests -v
```

## 注意事项

- AI 生成图片不能替代商家的上架审核。
- 正式发布前，应人工确认商品结构、颜色、文字、Logo、尺寸数值、单位、标线指向和使用方式。
- 材质纯度、产地、纯手工、非遗、认证、安全和功效等声明必须有可靠依据。
- 尺寸、容量、重量和工艺必须来自用户确认的信息，不得由商品照片推算。
- 网络或平台访问受限时，Skill 会使用保守的品类视觉规则继续执行，并明确标记未完成实时市场验证。
