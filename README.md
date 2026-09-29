# skills

跨项目复用的 Agent Skills 合集。开发新项目时把仓库地址给 Agent，它就能照同一套标准干活，不用每个仓库重新交代一遍。

## 用法

以 Pi 为例。Pi 可以直接装，仓库带了 `pi` 清单，三个技能会一起注册：

```bash
pi install git:github.com/huaxianyan/skills
```

也可以把技能目录复制过去，适合不想改 `pi` 设置、或者用的是别的工具的场合。Pi 会扫描两个位置：

- 全局 `~/.pi/agent/skills/`，所有项目共用。
- 项目级 `<项目>/.pi/skills/`，只对该项目生效，Pi 首次读取时会要求信任该项目。

装到全局：

```bash
git clone https://github.com/huaxianyan/skills.git
cp -r skills/chinese-tech-writing skills/project-conventions skills/release-notes-standard ~/.pi/agent/skills/
```

只装到某个项目，不影响其他项目：

```bash
git clone https://github.com/huaxianyan/skills.git /tmp/skills
mkdir -p <项目路径>/.pi/skills
cp -r /tmp/skills/project-conventions <项目路径>/.pi/skills/
```

临时加载一次，不改任何目录：

```bash
pi --skill /tmp/skills/project-conventions
```

装好后不需要额外配置，Pi 会在任务匹配时自动加载。想手动指定用 `/skill:chinese-tech-writing`，改过技能内容后跑一次 `/reload` 生效。

用其他支持 Agent Skills 的工具时，把目标目录换成对应的技能目录即可，例如 Claude Code 是 `~/.claude/skills/` 或 `<项目>/.claude/skills/`。

也可以不动手，直接在对话里说清需求并给出仓库地址，让 Agent 自己克隆、挑技能、装到项目里。

### 交给 Agent 的一句话

```
我要开发 <项目名>。先把这个仓库里的规范装到项目里：
https://github.com/huaxianyan/skills
装 chinese-tech-writing、project-conventions 和 release-notes-standard，放到本项目的 .pi/skills/ 下面。
```

Agent 会克隆仓库、挑出这几个技能、放进项目的技能目录。之后写文档、改注释、发版本就都按这套规范来。

## 包含的技能

### project-conventions

项目级开发规范与交接。五件事：

- **凭据与私钥**：SSH 私钥只能让工具直接使用，不读取、不解密、不打印、不比对。连带 API token、证书私钥、keystore 口令的引用方式，读文件前的确认习惯，以及泄露后的处理。
- **项目约定文件**：`AGENTS.md` 的分层、该写什么、不该写什么、怎么维护，以及本地文件边界。
- **开发进度文档**：当交接记忆来写，**放仓库里并进 Git**，不放 `.pi/`、`.claude/`、`.workbuddy/` 这类助手私有目录，不为某个软件做特化。两种可选形态、一条记录写什么、不写什么，以及交接时怎么读别人的记录。另外说清它与本地 `AGENTS.md` 可见性相反带来的写法差异。
- **任务预期与超时**：跑耗时命令前先给预期时长，超时后先缩小范围而不是重跑，停下来的报告格式。
- **测试临时产物的清理**：测试、调试、验证过程中生成的临时文件用完就清。收尾前确认本轮临时文件已处理。长期产物与临时产物分开。清理范围限于本轮自己生成的文件，不用宽泛通配符删别人数据。

自带 `references/handoff-template.md`，里面是可复制的进度记录模板与完整实例。

### chinese-tech-writing

中文技术文案与排版规范。管句子、段落、结构，也管空格、标点、引号。

规则来自两份来源：阮一峰《中文技术文档的写作规范》管句子与结构，《中文文案排版指北》管排版。冲突处默认两项：中文与行内代码之间留空格，简体中文用直角引号 `「」`。
另有 AI 腔清单和默认行文风格。

自带三个只报告不改文件的扫描脚本：

- `check_style.py` 启发式扫描：标点、空格、AI 腔词、破折号、分号、长句。
- `check_clauses.py` 查句长：整句不超过 100 个汉字，逗号隔开的每一截不超过 30 个。
- `check_typography.py` 排版硬规则门禁，退出码非零即失败，适合接 CI。

适用于写或改 README、设计文档、代码注释、提交信息、发布说明，也适用于给整个仓库做一次中文排版体检。

### release-notes-standard

GitHub Release 发布说明与页面的统一规范。

定死发布说明的形态与格式门禁：不超过 40 行、必须有主要更新节、必须链接到该标签下真实存在的文档、
禁止写使用说明与验收细节。Release 标题只留版本号，正文由说明文件加工作流追加的构建信息表拼成。

自带门禁脚本 `verify_release_notes.py`，可以直接接到 CI 里，打标签时跑。
另有 `references/retrofit-history.md`，讲清把历史 Release 追溯回现行标准的完整流程。

## 约定

- 目录结构是 `<技能名>/SKILL.md`，可以带 `references/` 与 `scripts/`。
- 根目录的 `package.json` 只用来支持 `pi install`，里面 `pi` 清单逐个列出技能目录。
  加技能或改目录名时，这里要跟着改。
- frontmatter 只写 `name` 与 `description`，兼容各类支持 Agent Skills 的工具。
- 脚本只用标准库，Python 3.7 以上能跑。

## 许可

[MIT](LICENSE)
