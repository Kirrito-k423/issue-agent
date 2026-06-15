---
name: github-issue-close
description: 用中文维护 GitHub issue 自动关闭评估与有界审计状态。Use when Codex needs to inspect oldest unrecorded GitHub issues, describe each issue's current state in Chinese, decide whether automatic closure is safe, draft a respectful close comment, close only after explicit apply=true, and maintain reusable Chinese close records for repositories such as verl-project/verl.
---

# GitHub Issue Close

使用这个 skill 按创建时间从旧到新处理 issue，判断是否适合自动关闭，并为每个 issue 留下一段中文“当前状态描述”和一句中文“是否关闭结论”。默认只预览和写本地过程文件，不公开评论或关闭 GitHub issue。

## 配置

从用户请求、环境说明或本地配置文件读取配置。默认值：

```yaml
repo: verl-project/verl
actor: Kirrito-k423
state_root: .issue-agent/state/verl-project__verl
write_policy: preview
batch_size: 10
summary_tracking_issue_title: "[Automation] Issue processing report"
language: zh-CN
```

使用 `repo` 作为 `gh --repo` 参数。未指定 `state_root` 时，用 `.issue-agent/state/<owner>__<repo>`。除非用户明确给出 `apply=true` 或 `write_policy=apply`，否则必须保持预览模式。

## 关闭判断规则

只有证据清楚、风险低、不会压掉仍可推进的工作时，才标记为“适合自动关闭”：

- **已明确解决**：维护者或相关 PR 已给出完整答案，后续没有新的未回答问题；或对应修复已经合并、发布或被明确替代。
- **明确重复**：能指向仍然有效的 canonical issue/PR/文档，且当前 issue 没有独立的新信息。
- **长期等待信息**：维护者已请求必要复现信息，提问者长期无回应，现有信息不足以继续推进。
- **明确不支持/不在范围内**：维护者已有公开结论说明该需求不会支持，或项目边界明确排除。
- **迁移到其他跟踪项**：需求已经被更具体、仍开放的 issue/PR 接管，且本 issue 不再承载独立信息。

以下情况必须标记为“不适合自动关闭”：

- issue 是 roadmap、feature request、call for contribution、good first issue、help wanted，且工作仍可被贡献者推进。
- 有关联 PR 仍处于 open/review，或关联 PR 关闭但未合并，不能证明问题已解决。
- issue 下仍有未回答的新问题、多人复现、近期活动，或讨论还在扩展范围。
- 作者是维护者，issue 像项目计划/任务卡，而不是用户问答。
- 判断依赖猜测、私有信息、未验证代码状态，或只是“太旧了”。

## 状态文件

在 `state_root/close/` 下创建或更新：

- `records.json`：以 issue number 字符串为 key 的规范记录表。
- `pending-batch.json`：每次运行覆盖，记录本批候选、状态描述、结论和拟执行动作。
- `latest-preview.md`：每次运行覆盖，给人看的中文结果文件。

每个 `records.json` 条目必须包含：

```json
{
  "issue_number": 20,
  "url": "https://github.com/OWNER/REPO/issues/20",
  "title": "Issue title",
  "current_state_cn": "一段中文描述：概括问题诉求、维护者/社区回复、关联 PR 或后续活动，以及当前是否仍有未解决事项。",
  "close_decision_cn": "一句中文结论：建议关闭/暂不关闭，并给出最核心理由。",
  "suitable_to_close": false,
  "auto_close_reason": "resolved-by-maintainer-answer|duplicate|stale-waiting-for-info|unsupported|superseded-by-tracker|not-suitable",
  "evidence_refs": ["issue body", "comment URL or PR URL"],
  "status": "previewed|commented|closed|skipped|failed",
  "comment_url": null,
  "closed_at": null,
  "actor": "Kirrito-k423",
  "last_assessed_at": "ISO-8601 timestamp"
}
```

保持状态有界：同一个 issue 只替换自己的记录，不追加历史流水。

## 工作流

1. 用 `gh auth status` 确认 GitHub 登录状态。
2. 读取 `records.json`；不存在时按 `{}` 处理。
3. 拉取 open issues，按创建时间从旧到新排序：`gh issue list --state open --search "sort:created-asc" --json number,title,url,author,createdAt,updatedAt,labels`。
4. 跳过已经存在于 `records.json` 的 issue，选取接下来 `batch_size` 个。
5. 对每个候选 issue 执行 `gh issue view`，读取正文、标签、评论、作者身份、更新时间。
6. 必要时查看关联 PR/issue 的状态，尤其是评论中出现的 PR 链接、closing reference、superseded tracker。
7. 为每个 issue 写 `current_state_cn`：用一段中文说明当前事实，必须覆盖“原始诉求、已有回复/关联事项、是否仍有未完成点”。
8. 为每个 issue 写 `close_decision_cn`：一句中文结论，格式建议为“建议关闭/暂不关闭：因为……”
9. 若适合关闭，拟定对外关闭评论；评论可用英文或中英双语，但过程文件中的判断必须为中文。
10. 写入 `pending-batch.json`、`latest-preview.md`，并更新 `records.json`。
11. 仅当 `apply=true` 时，才用 `gh issue comment` 发布关闭说明，再用 `gh issue close` 关闭 issue，并回填 `comment_url`、`closed_at`、`status`。

## 子 Agent 使用

子 agent 可以分析互不重叠的 issue 批次，但父 agent 负责最终判断、GitHub 写操作和状态文件写入。给子 agent 原始 issue JSON，并要求返回：

```json
{
  "issue_number": 20,
  "current_state_cn": "一段中文当前状态描述",
  "close_decision_cn": "一句中文关闭结论",
  "suitable_to_close": false,
  "auto_close_reason": "not-suitable",
  "evidence_refs": [],
  "draft_comment": null,
  "confidence": "low|medium|high"
}
```

不要让子 agent 发布评论、关闭 issue 或编辑规范状态文件。

## 安全规则

- 预览模式下绝不评论、绝不关闭。
- 不能因为 issue 年代久远就关闭。
- 对 roadmap、feature request、help wanted、call for contribution 默认保守，除非有明确完成或迁移证据。
- 如果评论已发布但关闭失败，记录 `status: failed` 和评论 URL，并在 `latest-preview.md` 用中文说明失败。
- 如果没有新的未记录 issue，写空 `pending-batch.json`，并在 `latest-preview.md` 用中文说明。

## 完成前检查

结束前报告：本批 issue 编号、建议关闭数量、预览或执行模式、更新的文件路径。预览模式下必须明确说明没有对 GitHub 发布评论或关闭 issue。
