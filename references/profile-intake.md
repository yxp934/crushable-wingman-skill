# Profile Intake (Initialization + Reuse)

Use this only when local profiles are missing or incomplete, or when the user asks to update their stored info.

Goals:
- Fully cover the Crushable onboarding questionnaires for `user profile` and `crush profile`.
- Reuse stored answers to avoid asking the same questions again.
- Ask in small batches (2-4 questions per round).

## 0) Setup (Once Per Session)

Commands below assume you are running from the skill folder. If not, use the installed path:
`python ~/.codex/skills/crushable-wingman/scripts/wingman_store.py ...`

1. Ensure local store exists:
```bash
python scripts/wingman_store.py init
```

2. Determine the active target:
- Read `active_handle.txt` via:
```bash
python scripts/wingman_store.py crush get-active
```
- Confirm with the user: "We are focusing on <handle> (<name>) right?"
- If no active handle, ask the user to pick/create one:
  - Ask for `handle` (hyphen-case) and display `name`.
  - Create crush folder + templates:
```bash
python scripts/wingman_store.py crush init --handle <handle> --name "<Name>"
python scripts/wingman_store.py crush set-active --handle <handle>
```

## 1) Reuse Rule (Non-Negotiable)

Before asking any intake question:
1. Load the existing profile file.
2. If the field is already filled, do NOT ask again unless:
   - The user explicitly says it changed, or
   - The user says it was wrong, or
   - The user asks to "re-do my profile".

Helpful commands:
```bash
python scripts/wingman_store.py user show-profile
python scripts/wingman_store.py crush show-profile --handle <handle>
python scripts/wingman_store.py user missing
python scripts/wingman_store.py crush missing --handle <handle>
```

## 2) User Profile Intake (Full Coverage)

Source: Crushable `profile-questionnaire` fields.

Write answers into `user/profile.md` using the template:
```bash
python scripts/wingman_store.py init
python scripts/wingman_store.py user show-profile
```

If you need to reset templates (rare):
```bash
python scripts/wingman_store.py user init --force
```

### Ask In Batches (Suggested)

Batch 1 (Basics)
- `user_name`: "我该怎么称呼你？"
- `user_pronouns`: "你的代词/称呼偏好？(she/her, he/him, they/them, 其他, 不想说)"
- `sexual_orientation`: "你通常对哪类人感兴趣？(men/women/everyone/其他/不想说)"

Batch 2 (Basics + Personality)
- `age_range`: "你的年龄段？(16-18 / 19-24 / 25-30 / 31-35 / 36+ / 不想说)"
- `relationship_status`: "你的当前关系状态？(single / complicated / just vibing / talking to someone / 其他)"
- `social_energy`: "你更像：内向/外向/中间？"

Batch 3 (Personality + Interests)
- `planning_style`: "你对计划更像：规划型/随性/看心情？"
- `confidence_level`: "你在 crush 面前的自信程度 1-10？(不知道可答 unknown)"
- `date_preferences`: "理想约会更像哪种？(咖啡深聊/户外冒险/电影宅/晚餐氛围/其他)"

Batch 4 (Interests + Dating Style)
- `hobbies`: "你最常做/最喜欢的兴趣（多选）？"
  - Store as JSON array, e.g. `hobbies: [\"音乐\", \"旅行\"]`
  - If they refuse: use `hobbies: [\"prefer_not_to_say\"]`
- `approach_style`: "你更像：害羞/直接/调皮flirty/体贴？"
- `pace`: "你的节奏偏好：慢热(slow burn)/稳步(steady)/直接冲(go for it)/其他？"

Batch 5 (Communication)
- `comm_method`: "你更喜欢怎么建立联系：text/in-person/calls/mixed？"
- `response_time`: "你通常回消息速度：秒回/1小时内/几小时/看到才回/会刻意等？"
- `emoji_user`: "你常用 emoji 吗？(true/false/unknown)"

Batch 6 (Boundaries)
- `comfort_sharing`: "你表达/分享感受的舒适度 1-10？(不知道可答 unknown)"
- `pda_comfort`: "公开亲密(PDA)你更舒服：喜欢/只小动作/更私密/看场合？"
- `relationship_goal`: "你现在更想要：认真关系/顺其自然/轻松随缘/还在想？"

## 3) Crush Profile Intake (Full Coverage + Confidence)

Source: Crushable `crush-profile` fields.

Write answers into `crushes/<handle>/profile.md` using the template:
```bash
python scripts/wingman_store.py crush init --handle <handle> --name "<Name>"   # if missing
python scripts/wingman_store.py crush show-profile --handle <handle>
```

### Ask In Batches (Suggested)

Batch 1 (Basic)
- `name`: "我该怎么称呼 TA？"
- `nickname`: "你给 TA 的昵称？(可空)"
- `how_you_know_them`: "你们怎么认识的？(同事/同学/朋友介绍/线上/其他)"

Batch 2 (Interests + confidence)
- `interests`: "TA 明显喜欢什么？(多选/举例)"
- `interests_confidence`: "你对这些兴趣的确定度：sure/guess/unknown？"

Batch 3 (Communication + confidence)
- `communication_style`: "TA 的沟通方式更像什么？(多选)"
- `communication_confidence`: "确定度：sure/guess/unknown？"

Batch 4 (Availability + confidence)
- `availability_pattern`: "TA 一般什么时候更有空/更愿意见面或聊天？"
- `availability_confidence`: "确定度：sure/guess/unknown？"

Batch 5 (Context)
- `relationship_context`: "你们关系背景：刚认识/朋友一阵/同学/同事/线上/共同朋友/其他？"
- `current_status`: "现在进展状态：刚crush/聊过/会见面/暧昧张力/信号不清/其他？"

Batch 6 (Sensitive)
- `sensitive_topics`: "有哪些话题/点最好先别碰？(多选)"
  - Store as JSON array, e.g. `sensitive_topics: [\"前任\", \"政治\"]`

Batch 7 (History)
- `last_meaningful_moment`: "最近一次有意义的互动是什么？"
- `last_contact_date`: "最后一次联系/见面的日期？(YYYY-MM-DD 或 unknown)"

## 4) Writeback And Validate

After each batch:
1. Update the profile file(s) (upsert the full Markdown).
2. Validate constraints (memory snapshots especially):
```bash
python scripts/wingman_store.py validate --handle <handle>
```

If the user says "I don't know / skip":
- Prefer filling the field with a clear sentinel (`unknown` or `prefer_not_to_say`) rather than leaving it blank.
