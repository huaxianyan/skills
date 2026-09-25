# skills

跨项目复用的 Agent Skills 合集。开发新项目时把仓库地址给 agent，它就能照同一套标准干活，不用每个仓库重新交代一遍。

## 用法

克隆到本地，把需要的技能目录复制到技能目录下。

装到全局，所有项目共用：

```bash
git clone https://github.com/huaxianyan/skills.git
cp -r skills/chinese-tech-writing skills/release-notes-standard ~/.workbuddy/skills/
```

只装到某个项目，不影响其他项目：

```bash
git clone https://github.com/huaxianyan/skills.git /tmp/skills
mkdir -p <项目路径>/.workbuddy/skills
cp -r /tmp/skills/release-notes-standard <项目路径>/.workbuddy/skills/
```

用其他支持 Agent Skills 的工具时，把目标目录换成对应的技能目录即可，
例如 Claude Code 是 `~/.claude/skills/` 或 `<项目>/.claude/skills/`。

也可以不动手，直接在对话里说清需求并给出仓库地址，让 agent 自己克隆、挑技能、装到项目里。

### 交给 agent 的一句话

```
我要开发 <项目名>。先把这两个规范装到项目里：
https://github.com/huaxianyan/skills
装 chinese-tech-writing 和 release-notes-standard，放到本项目的 .workbuddy/skills/ 下面。
```

agent 会克隆仓库、挑出这两个技能、放进项目的技能目录。之后写文档、改注释、发版本就都按这套规范来。

## 包含的技能

### chinese-tech-writing

中文技术文案规范。约束中文与英文数字之间的空格、全角标点、长句拆解、破折号与分号的使用，
另外带一份 AI 腔清单，逐条给出「找这种写法 → 改成」。

自带两个扫描脚本，只报告不改文件：

- `check_style.py` 查标点、空格、AI 腔词、破折号、分号、长句。
- `check_clauses.py` 查句长，整句不超过 100 个汉字，逗号隔开的每一截不超过 30 个。

适用于写或改 README、设计文档、代码注释、提交信息、发布说明，
也适用于给整个仓库做一次中文排版体检。

### release-notes-standard

GitHub Release 发布说明与页面的统一规范。

定死发布说明的形态与格式门禁：不超过 40 行、必须有主要更新节、必须链接到该标签下真实存在的文档、
禁止写使用说明与验收细节。Release 标题只留版本号，正文由说明文件加工作流追加的构建信息表拼成。

自带门禁脚本 `verify_release_notes.py`，可以直接接到 CI 里，打标签时跑。
另有 `references/retrofit-history.md`，讲清把历史 Release 追溯回现行标准的完整流程。

## 约定

- 目录结构是 `<技能名>/SKILL.md`，可以带 `references/` 与 `scripts/`。
- frontmatter 只写 `name` 与 `description`，兼容各类支持 Agent Skills 的工具。
- 脚本只用标准库，Python 3.7 以上能跑。

## 许可

[MIT](LICENSE)
