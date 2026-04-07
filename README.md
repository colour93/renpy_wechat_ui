# WeChat UI for Ren'Py

一个可直接放进 Ren'Py 项目的微信风格聊天 UI。

目前已经按职责拆分成多个 `.rpy` 文件，方便继续扩展首页、聊天页和后续的朋友圈模块。

## 安装

推荐直接把仓库克隆到你的 Ren'Py 项目 `game/` 目录下喜欢的位置。

例如：

```bash
cd your-project/game
git clone https://github.com/colour93/renpy_wechat_ui.git wechat_ui
```

如果你不是直接把整个仓库放进项目，也至少需要把下面两部分一起带上：

- `game/wechat_ui/`
- `game/wechat_ui.rpy`

## 使用前要改的地方

### 1. 调整字体

默认字体定义在 `game/wechat_ui/util.rpy`：

```renpy
define phone_font = "fonts/MiSans-Normal.otf"
```

你需要把它改成你自己项目里真实存在的字体路径，例如：

```renpy
define phone_font = "fonts/SourceHanSansSC-Regular.otf"
```

如果字体路径不对，UI 文字会无法正常显示。

### 2. 确认头像图片路径

如果你给联系人传了 `avatar_image`，也要保证对应图片资源在项目里存在。

例如：

```renpy
$ lao_ma = WeChatContact(
    "lao_ma",
    "老妈",
    avatar_image="images/avatar/lao_ma.png",
)
```

## 目录结构

- `util.rpy`：数据结构、时间处理、消息/会话状态方法
- `method.rpy`：默认变量和对外 `label`
- `component.rpy`：公共 screen，例如手机外壳、toast、头像、媒体消息体
- `style.rpy`：公共样式
- `home/component.rpy`、`home/style.rpy`：首页列表 UI
- `chat/component.rpy`、`chat/style.rpy`：聊天页 UI
- `moment/component.rpy`、`moment/style.rpy`：朋友圈/时间线预留位置
- `example/congcong_ch1.rpy`：示例脚本

## 快速开始

`game/wechat_ui/example/congcong_ch1.rpy` 里给了一套完整示例，大致分成下面几步。

### 1. 定义联系人

```renpy
$ mu_xing = WeChatContact("mu_xing", "牧星", avatar_color="#4d7cff")
$ lao_ma = WeChatContact("lao_ma", "老妈", avatar_color="#e92f2f")
```

联系人除了 `avatar_color`，也支持 `avatar_image`：

```renpy
$ lao_ma = WeChatContact(
    "lao_ma",
    "老妈",
    avatar_color="#e92f2f",
    avatar_image="images/avatar/lao_ma.png",
)
```

### 2. 注册会话

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

### 3. 设置当前时间并打开首页

```renpy
$ wc_update_current_time((2026, 1, 5, 16, 7))
call wechat_home
```

### 4. 追加实时消息

`wc_queue_*` 会先放进待显示队列，进入 `wechat_session` 后按条展示，适合“边看边弹出”的演出。

```renpy
$ wc_queue_text("chat.lao_ma", mu_xing, "妈", unread_increment=0)
$ wc_queue_text("chat.lao_ma", lao_ma, "还有")
call wechat_session("chat.lao_ma")
```

### 5. 直接收消息 / 顶部提示

`wc_receive_*` 会立即写入会话，常和 `wc_push_toast()` 配合。

```renpy
$ wc_receive_text("chat.lao_ma", lao_ma, "我出发了")
$ wc_push_toast("老妈：我出发了")
```

### 6. 打开指定会话

```renpy
call wechat_session("chat.lao_ma")
call wechat_session("group.xiang_qin_xiang_ai_yi_jia_ren")
```

## Overlay 用法

除了整页聊天模式，也可以把聊天界面作为 overlay 挂在剧情上面。

### 基础 overlay

```renpy
call wechat_show_chat("chat.ka_nuo")

"这里继续正常剧情对白"

call wechat_hide_chat
```

### Overlay + queue 消息逐条出现

overlay 模式下不会自动消费 `wc_queue_text()`，你需要手动调用：

- `call wechat_overlay_reveal_next()`

例如：

```renpy
call wechat_show_chat("chat.ka_nuo")

"从家出来之后，卡诺先去忙自己的事了"

$ wc_queue_text("chat.ka_nuo", mu_xing, "我先随便逛逛", timestamp=(2026, 1, 9, 9, 3), unread_increment=0)
call wechat_overlay_reveal_next()

"先这么发吧"

$ wc_queue_text("chat.ka_nuo", ka_nuo, "晚上见", timestamp=(2026, 1, 9, 9, 4))
call wechat_overlay_reveal_next()

call wechat_hide_chat
```

### 点击节奏

`wechat_overlay_reveal_next()` 默认会先等一次点击，再把下一条 queue 消息 reveal 出来。

也就是说下面这段：

```renpy
"从家出来之后，卡诺先去忙自己的事了"
$ wc_queue_text("chat.ka_nuo", mu_xing, "我先随便逛逛")
call wechat_overlay_reveal_next()
```

实际节奏是：

1. 左键，显示对白
2. 再左键，显示消息

如果你想让消息立刻出现，不再额外等一次点击，可以写：

```renpy
call wechat_overlay_reveal_next(wait_for_click=False)
```

### 脚本文本窗口自动隐藏

`wechat_show_chat()` 默认会带上：

```renpy
hide_window_when_idle=True
```

效果是：

- 没有对白时，脚本文本窗口会自动隐藏
- 到下一句对白时，Ren'Py 会正常显示对白框
- 隐藏时会沿用项目自己的 `config.window_hide_transition`

如果你不想要这个行为，可以显式关闭：

```renpy
call wechat_show_chat("chat.ka_nuo", hide_window_when_idle=False)
```

## 常用 API

- `WeChatContact(contact_id, name, avatar_color=..., bubble_color=None, role=None, avatar_image=None, avatar_text=None)`
- `WeChatSession(session_id, title, participants, player, entries=[...], subtitle=None, is_group=False, avatar_contact=None, unread_count=0, last_timestamp=None, last_read_entry_count=None, active_divider_index=None, pending_entries=None)`
- `wc_text(sender, text, quote=None, timestamp=None)`
- `wc_image(sender, caption, media=None, quote=None, timestamp=None)`
- `wc_separator(text, kind="system", timestamp=None)`
- `wc_timestamp(text, timestamp=None)`
- `wc_quote(sender_name, preview, kind="text")`
- `wc_register_session(session)`
- `wc_has_session(session_id)`
- `wc_update_current_time(timestamp)`
- `wc_queue_text(...)` / `wc_queue_image(...)` / `wc_queue_separator(...)`
- `wc_receive_text(...)` / `wc_receive_image(...)` / `wc_receive_separator(...)`
- `wc_push_toast(message, duration=2.2)`
- `call wechat_home`
- `call wechat_session("session_id")`
- `call wechat_show_chat("session_id", hide_window_when_idle=True)`
- `call wechat_overlay_reveal_next(wait_for_click=True)`
- `call wechat_hide_chat`

## 约定

- `player` 代表主角自己，用来区分左右气泡和未读数逻辑。
- `session_id` 建议区分前缀，例如私聊用 `chat.xxx`，群聊用 `group.xxx`。
- 时间戳支持元组、`datetime`、`date`，以及类似 `"10:20"`、`"今天 18:30"` 的简写。
- 群聊预览会自动带上发送者名字，单聊不会。
- 如果同一段消息的时间间隔超过阈值，会自动插入时间分隔。

## 后续扩展

- 如果要加朋友圈，可以继续把 `moment/component.rpy` 和 `moment/style.rpy` 按同样结构补齐。
- 如果要扩展消息类型，优先从 `WeChatEntry`、`wc_render_entries()` 和 `wechat_message_body` 一起改。
