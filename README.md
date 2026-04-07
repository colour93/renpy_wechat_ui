# RenPy WeChat UI

RenPy 下的仿微信 UI 实现。

当前结构：

- `util.rpy`：数据结构、时间处理、消息/会话状态方法
- `method.rpy`：默认变量和对外 `label`
- `component.rpy`：公共 screen，例如手机外壳、toast、头像、媒体消息体
- `style.rpy`：公共样式
- `home/component.rpy`、`home/style.rpy`：首页列表 UI
- `chat/component.rpy`、`chat/style.rpy`：聊天页 UI
- `moment/component.rpy`、`moment/style.rpy`：朋友圈/时间线预留位置

## 基本用法

1. 定义联系人

```renpy
$ mu_xing = WeChatContact("mu_xing", "牧星", avatar_color="#4d7cff")
$ lao_ma = WeChatContact("lao_ma", "老妈", avatar_color="#e92f2f")
```

2. 注册会话

```renpy
if not wc_has_session("chat.lao_ma"):
    $ wc_register_session(
        WeChatSession(
            "chat.lao_ma",
            title="老妈",
            participants=[mu_xing, lao_ma],
            player=mu_xing,
            entries=[
                wc_text(lao_ma, "今年过年还回来吗？", timestamp=(2025, 12, 30, 20, 21)),
                wc_text(mu_xing, "我再看看吧", timestamp=(2025, 12, 30, 20, 21)),
            ],
        )
    )
```

3. 设置当前时间并打开首页

```renpy
$ wc_update_current_time((2026, 1, 5, 16, 7))
call wechat_home
```

4. 追加实时消息

`wc_queue_*` 会先放进待显示队列，进入会话后按条展示，适合“边看边弹出”的演出。

```renpy
$ wc_queue_text("chat.lao_ma", mu_xing, "妈", unread_increment=0)
$ wc_queue_text("chat.lao_ma", lao_ma, "还有")
call wechat_session("chat.lao_ma")
```

5. 直接收消息 / 发提示

`wc_receive_*` 会立即写入会话，常和 `wc_push_toast()` 配合。

```renpy
$ wc_receive_text("chat.lao_ma", lao_ma, "我出发了")
$ wc_push_toast("老妈：我出发了")
```

6. 打开指定会话

```renpy
call wechat_session("chat.lao_ma")
call wechat_session("group.xiang_qin_xiang_ai_yi_jia_ren")
```

## 常用 API

- `WeChatContact(contact_id, name, avatar_color=...)`
- `WeChatSession(session_id, title, participants, player, entries=[...], is_group=False, subtitle=None)`
- `wc_text(sender, text, quote=None, timestamp=None)`
- `wc_image(sender, caption, media=None, quote=None, timestamp=None)`
- `wc_separator(text, kind="system", timestamp=None)`
- `wc_quote(sender_name, preview, kind="text")`
- `wc_register_session(session)`
- `wc_has_session(session_id)`
- `wc_update_current_time(timestamp)`
- `wc_queue_text(...)` / `wc_queue_image(...)`
- `wc_receive_text(...)` / `wc_receive_image(...)`
- `wc_push_toast(message, duration=2.2)`
- `call wechat_home`
- `call wechat_session("session_id")`

## 约定

- `player` 代表主角自己，用来区分左/右气泡和未读数逻辑。
- `session_id` 建议区分前缀，例如私聊用 `chat.xxx`，群聊用 `group.xxx`。
- 时间戳支持元组、日期时间对象，以及类似 `"10:20"` 这样的简写。
- 群聊预览会自动带上发送者名字，单聊不会。

## 后续扩展

- 如果要加朋友圈，可以继续把 `moment/component.rpy` 和 `moment/style.rpy` 按同样结构补齐。
- 如果要扩展消息类型，优先从 `WeChatEntry`、`wc_render_entries()` 和 `wechat_message_body` 一起改。
