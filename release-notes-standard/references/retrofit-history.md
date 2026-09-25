# 把发布说明标准追溯回历史 Release

门禁改了以后，历史 Release 的正文不会自动跟着变。这份文档是把它们统一到现行标准的完整流程。

前提：`gh` 已登录，本地有仓库的完整标签历史。

## 一、先摸清现状

```bash
gh release list --limit 50 --json tagName,name,isDraft,isPrerelease,publishedAt \
  --jq '.[] | "\(.tagName)\t title=\(.name)\t draft=\(.isDraft)\t pub=\(.publishedAt)"'
git tag --list --sort=version:refname
```

注意两件事：

- **标题可能已经符合要求，也可能没有。** 逐个确认，别假设全都要改。
- **发布说明文件可能已经存在。** 先看 `docs/release-notes/`（或该项目约定的目录）里有没有
  对应的文件，有的话是重写而不是新建。

## 二、备份旧正文

这是唯一的回滚手段，动手前必做。

```bash
mkdir -p /tmp/release-bodies
for t in v0.1.0 v0.1.1 v0.1.2; do
  gh release view "$t" --json body --jq .body > "/tmp/release-bodies/$t.md"
done
```

## 三、比对仓库文件与线上正文

**不要拿仓库文件当历史事实。** 发布之后说明文件还可能改过，线上正文才是当时发出去的东西。
两者不一致时，线上独有的内容要合并进新版本。

```bash
python - <<'EOF'
import difflib, io, pathlib
for v in ["v0.1.0", "v0.1.1"]:
    a = pathlib.Path("docs/release-notes/%s.md" % v).read_text(encoding="utf-8").splitlines()
    b = pathlib.Path("/tmp/release-bodies/%s.md" % v).read_text(encoding="utf-8").splitlines()
    print("=" * 20, v)
    for line in difflib.unified_diff(b, a, "online", "repo", lineterm="", n=0):
        print(line)
EOF
```

实际遇到过的情况：线上正文比仓库文件多一整节，如果只按仓库文件重写就会丢内容。

## 四、核对链接锚点

写进说明文件的 `blob/v<标签>/` 链接，锚点必须在那个标签下真实存在。

```bash
for t in v0.1.0 v0.1.4; do
  echo "===== $t README.md ====="
  git show "$t:README.md" | grep -E '^#{1,3} '
  echo "===== $t docs/architecture.md ====="
  git show "$t:docs/architecture.md" | grep -E '^#{1,3} '
done
```

要挑在各个标签下都稳定存在的节，只在后期版本里出现的节不能写进早期版本的链接。

## 五、重写说明文件

统一成主文件里的标准形态。一次生成多份用脚本，比逐个手写可靠：

- 把每个版本的结构化内容写成脚本里的数据，用同一套模板渲染。
- 脚本里对每份文件断言「渲染后不超过 40 行」「含 `## 主要更新`」「含 `blob/v<版本>/` 链接」。
- 落盘后再跑一遍门禁脚本与中文扫描脚本。

## 六、收集产物哈希

`## 构建信息` 表要列每个产物的 SHA-256，可以从两个来源取：

- **优先读 Release 里的 `SHA256SUMS` 资产。** 早期版本可能没有这个资产，那就下载产物本地算。
- 抽查一次即可确认 `SHA256SUMS` 的记录与产物本体一致，之后可以直接当数据源。

```bash
for t in v0.1.2 v0.1.3; do
  curl -sS -L --proxy http://127.0.0.1:37777 -o "$t.SHA256SUMS" \
    "https://github.com/<owner>/<repo>/releases/download/$t/SHA256SUMS"
done
```

没有 `SHA256SUMS` 的版本：

```bash
for a in app-release.apk system-extension-release.apk; do
  curl -sS -L --proxy http://127.0.0.1:37777 -o "v0.1.0.$a" \
    "https://github.com/<owner>/<repo>/releases/download/v0.1.0/$a"
done
sha256sum v0.1.0.app-release.apk v0.1.0.system-extension-release.apk
```

## 七、按工作流的拼装逻辑生成新正文

新正文必须和工作流将来生成的一模一样，所以直接复用 `Publish GitHub release` 步骤里那几行
`cat` 加 `printf`，不要另写一套格式。

生成后逐份确认行数：

```
说明文件行数 + 空行 + "## 构建信息" + 空行 + 三到四行表格
```

## 八、批量改写标题与正文

```bash
# 标题已经是纯版本号的，只改正文
gh release edit v0.1.0 --notes-file /tmp/hist-bodies/v0.1.0.md

# 标题和正文都要改的
gh release edit v0.1.1 --title "v0.1.1" --notes-file /tmp/hist-bodies/v0.1.1.md
```

逐个执行，失败的单独重试，不要写成一个循环就不管结果。

## 九、逐个复核

```bash
gh release list --limit 50 --json tagName,name --jq '.[] | "\(.tagName)\t\(.name)"'
for t in v0.1.0 v0.1.1; do
  echo "--- $t ---"
  gh release view "$t" --json body --jq '.body | split("\n") | length'
  gh release view "$t" --json assets --jq '[.assets[] | "\(.name)(\(.size))"] | join("  ")'
done
```

对照检查：

- 标题等于标签。
- 正文含摘要节与 `## 构建信息`，身份节只有一个，没有禁用的节，首行不是一级标题，行数在上限内。
- **资产的数量与字节数与改之前完全一致。** 改描述不该动产物，这一条最容易发现问题。

## 十、提交仓库侧的改动

重写后的说明文件、门禁脚本、工作流里的标题改动都要提交。

按项目惯例开独立分支，验收后快进合并。工作流里如果还写着带产品名前缀的
`--title`，一并改成 `--title "$GITHUB_REF_NAME"`，否则下次发布又会带上前缀。

## 容易踩的坑

- **行尾不统一。** 同一仓库里有的文件是 LF，有的是 CRLF。重写整份文件时按原行尾写回，
  用 `io.open(path, newline="")` 读写，并记着 universal newline 读法会把 CRLF 归一成 LF，
  让 `"\r\n" in text` 永远为假。
- **`gh release edit` 只传 `--title` 时正文不动，只传 `--notes-file` 时标题不动。**
  需要一起改就两个都传。
- **批量写中文用脚本文件，不要用 `python -c "..."`。** shell 会吃掉反引号。
- **别在一条消息里并发下发多个写文件的调用。** 会静默丢改动，逐个写逐个验证。
