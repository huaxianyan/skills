---
name: release-notes-standard
description: GitHub Release 发布说明与页面的统一规范。写发布说明、建 Release、给发布流程加门禁、把历史 Release 追溯回现行标准时使用。触发语句：「发布 release」「发新版」「写发布说明」「Release 描述改一下」「把之前的 release 也按标准重写」「Release 标题只留版本号」「release 页面全是一样的看不出是哪个版本」。
---

# 发布说明与 Release 页面规范

GitHub Release 页面是发布出去的门面。这里定一套跨项目通用的写法，配上可执行的门禁脚本。

目标：一屏读完知道这版改了什么，详细内容留在仓库文档里。Release 列表能直接看出是哪个版本。

## 格式门禁

脚本按下面的规则判。任何一条不过，CI 就该失败。

| 规则 | 判据 |
| --- | --- |
| 不得以一级标题开头 | 首行不能匹配 `# `。产品名和版本号由 Release 页面自己展示 |
| 行数 | 全文不超过 40 行 |
| 必须有更新摘要节 | 默认要求 `## 主要更新` |
| 必须链接详细记录 | 至少一条链接匹配 `/blob/v<标签>/`，指向该标签下真实存在的文档 |
| 禁止出现的节 | `## 使用说明`、`## 真机验收`、`## 构建与兼容范围`、`## 兼容边界` |
| 身份节至多一个 | `## 版本信息` 与 `## 构建信息` 只能出现一个，且通常由工作流追加 |

四个禁用节的原因一样：使用方式、验收过程、构建范围属于长期文档，写在 `docs/` 里可以随版本更新，
写在 Release 里就会在下一个版本变成过时的死文本。

## 标准形态

```
<概述段：这版解决了什么，一到两句>

## 主要更新

- **小标题**：说明
- **小标题**：说明

<可选说明段：设计取舍、已知边界、升级注意事项>

完整实现与验收记录见 [标题](https://github.com/<owner>/<repo>/blob/v<版本>/<文档>)。

<许可证尾句>
```

几条写法上的要求：

- **概述段讲解决什么问题，不讲改了多少行。** 读者关心的是他的使用体验变了什么。
- **主要更新的每一条以加粗小标题开头**，冒号后写说明。一条说一件事。
- **链接的锚点要在那个标签下真实存在。** 核对方式：
  `git show <tag>:docs/architecture.md | grep -E '^#{1,3} '`。不要拿现在的文档结构去写历史版本的链接。
- **升级注意事项**（能否覆盖安装、要不要同步升级配套组件）放在主要更新之后的说明段里。
- 说明文件只是 Release 正文的前半段，工作流会在后面追加 `## 构建信息`，所以自己不要写这一节。

## Release 页面形态

- **标题就是标签本身**（`v0.2.0`），不加产品名前缀。
  加了前缀以后，左侧 Release 列表会变成一列被截断的同一个名字，看不出是哪个版本，
  反而失去了列表的作用。
- **正文 = 仓库里的发布说明文件 + 工作流追加的 `## 构建信息` 表**。
  表里放版本号与每个产物的 SHA-256。

工作流里的拼装方式（`cat` 加 `printf` 直出，不要用模板引擎）：

```bash
notes_out="build/release/release-notes.md"
mkdir -p "$(dirname "$notes_out")"
{
  cat "$notes_file"
  printf '\n## 构建信息\n\n'
  printf '| 项目 | 值 |\n'
  printf '| --- | --- |\n'
  printf '| 版本 | `%s` |\n' "$GITHUB_REF_NAME"
  for apk in app/build/outputs/apk/release/app-release.apk \
             system-extension/build/outputs/apk/release/system-extension-release.apk; do
    printf '| %s SHA-256 | `%s` |\n' "${apk##*/}" "$(sha256sum "$apk" | cut -d' ' -f1)"
  done
} > "$notes_out"
gh release create "$GITHUB_REF_NAME" --title "$GITHUB_REF_NAME" --notes-file "$notes_out" ...
```

同时改已有的 Release 时只传 `--title`，正文不动。只传 `--notes-file`，标题不动。

```bash
gh release edit vX.Y.Z --title "vX.Y.Z" --notes-file /path/to/body.md
```

## 门禁脚本

```bash
python scripts/verify_release_notes.py docs/release-notes/v0.2.0.md
python scripts/verify_release_notes.py --tag v0.2.0
python scripts/verify_release_notes.py --tag v0.2.0 --dir docs/releases
```

参数：

- `notes`：要检查的文件，可以给多个。都不给时用 `--tag` 和 `--dir` 拼路径。
- `--tag`：版本标签，例如 `v0.2.0`。
- `--dir`：发布说明目录，默认 `docs/release-notes`。
- `--max-lines`：行数上限，默认 40。
- `--summary-heading`：必须出现的摘要节，默认 `## 主要更新`。
- `--link-pattern`：详细记录链接的正则，默认 `/blob/v[^/\s]+/`。
  用 CHANGELOG 风格的项目改成 `CHANGELOG\.md#\d`。
- `--forbidden`：追加禁止出现的节，可以重复给。

通过时输出 `verified across N file(s)`，失败时逐条打印原因并以非零码退出。

## 接到 CI

在打标签时才跑，放在发布步骤之前：

```yaml
      - name: Verify release notes
        if: startsWith(github.ref, 'refs/tags/v')
        run: python3 scripts/verify_release_notes.py --tag "$GITHUB_REF_NAME"
```

发布任务用 `if: startsWith(github.ref, 'refs/tags/v')` 控制，这样推分支只跑构建，推标签才发 Release。

## 发布顺序

1. **先在本地过门禁**，这一步不通后面全白做。
2. 提交并推主分支，等 CI 绿。这一步失败还有机会修。
3. 打注解标签并推送，触发发布。
4. 复核线上产物。

**发布成功后标签与 Release 都不可撤销。** 要重发得先删标签，修完再重打。
但 `gh release edit` 可以随时改标题与正文，不必删标签。

先推主分支再推标签的理由很简单：主分支那次失败可以重来，标签推出去就不能收回了。

## 复核线上产物

先看资产清单，再逐个下载核算。

```bash
gh release view vX.Y.Z --json tagName,name,assets \
  --template '{{.tagName}} | {{.name}}{{"\n"}}{{range .assets}}ASSET {{.name}}  {{.size}} bytes{{"\n"}}{{end}}'
```

逐项核对：

- 每个资产的大小与 `gh release view --json assets` 报的一致。
- 下载后实测 SHA-256 与 `SHA256SUMS` 逐字节一致。
- 签名证书与上一版一致。**不一致就停下来问**，因为这决定老用户能否覆盖安装。
- 包的版本号是新的，且不含 debug 标志。
- 正文行数与结构符合上面的形态，链接的锚点真实存在。

直连 GitHub 慢的机器走代理下载：

```bash
curl -sS -L --proxy http://127.0.0.1:37777 -o app-release.apk \
  "https://github.com/<owner>/<repo>/releases/download/vX.Y.Z/app-release.apk"
```

## 把标准追溯回历史 Release

门禁改了以后，历史 Release 不会自动更新。回填流程见
[references/retrofit-history.md](references/retrofit-history.md)，关键点有三条：

- 先备份旧正文，那是唯一的回滚手段。
- 不要拿仓库文件当历史事实，发布之后说明文件还可能改过，线上正文才是当时发出去的东西。
- 改完逐个复核，**确认资产数量和字节数没有变化**。改描述不该动产物。

## 项目适配清单

接手一个新项目时，先确认这几项，写进项目的 `AGENTS.md`：

- 版本号的唯一来源（例如 `gradle.properties`、`package.json`、`Cargo.toml`）。
- 发布说明目录。默认 `docs/release-notes/v<版本>.md`。
- 详细记录的链接形态。多数项目用 `/blob/v<标签>/<文档>`，用 CHANGELOG 的项目改成 `CHANGELOG.md#<版本>`。
- 构建信息表要列哪些产物。
- 构建与签名的命令、签名证书指纹。
- CI 工作流的位置，以及 `release` 任务是不是只在标签下触发。

## 来源

这套规范在 syncclipboard、comeback-google-pinyin-input 等项目上跑通，
门禁脚本最早从 comeback 项目移植。
