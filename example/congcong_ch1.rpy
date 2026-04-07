label congcong_ch1:

    scene main_menu

    # 定义联系人
    $ mu_xing = WeChatContact("mu_xing", "牧星", avatar_color="#4d7cff")
    $ jiang_mu = WeChatContact("jiang_mu", "姜暮", avatar_color="#f29c6b")
    $ ka_nuo = WeChatContact("ka_nuo", "卡诺", avatar_color="#5d9b6c")
    $ lao_ma = WeChatContact("lao_ma", "老妈", avatar_color="#e92f2f")

    # 初始化会话
    if not wc_has_session("chat.lao_ma"):
        $ wc_register_session(
            WeChatSession(
                "chat.lao_ma",
                title="老妈",
                participants=[mu_xing, lao_ma],
                player=mu_xing,
                entries=[
                    wc_text(lao_ma, "今年过年还回来吗？", timestamp=(2025, 12, 30, 20, 21)),
                    wc_text(lao_ma, "卡诺回来了", timestamp=(2025, 12, 30, 20, 21)),
                    wc_text(mu_xing, "这么早问这个嘛……", timestamp=(2025, 12, 30, 20, 21)),
                    wc_text(mu_xing, "等等", timestamp=(2025, 12, 30, 20, 21)),
                    wc_text(mu_xing, "卡诺现在已经回家了？", timestamp=(2025, 12, 30, 20, 21)),
                    wc_text(lao_ma, "对", timestamp=(2025, 12, 30, 20, 21)),
                    wc_text(mu_xing, "我再看看吧", timestamp=(2025, 12, 30, 20, 21)),
                    wc_text(lao_ma, "臭小子", timestamp=(2025, 12, 30, 20, 21)),
                ],
            )
        )
    if not wc_has_session("chat.ka_nuo"):
        $ wc_register_session(
            WeChatSession(
                "chat.ka_nuo",
                title="卡诺",
                participants=[mu_xing, ka_nuo],
                player=mu_xing,
                entries=[
                    wc_text(ka_nuo, "牧哥", timestamp=(2025, 12, 29, 23, 30)),
                    wc_text(ka_nuo, "想你咯", timestamp=(2025, 12, 29, 23, 30)),
                    wc_text(ka_nuo, "今年还回来吗", timestamp=(2025, 12, 29, 23, 30)),
                ],
            )
        )
    if not wc_has_session("chat.jiang_mu"):
        $ wc_register_session(
            WeChatSession(
                "chat.jiang_mu",
                title="姜暮",
                participants=[mu_xing, jiang_mu],
                player=mu_xing,
                entries=[
                    wc_text(jiang_mu, "今年还回来吗", timestamp=(2025, 12, 29, 20, 1)),
                    wc_text(mu_xing, "应该不回来了", timestamp=(2025, 12, 30, 8, 2)),
                ],
            )
        )
    if not wc_has_session("group.gou_gou_gou"):
        $ wc_register_session(
            WeChatSession(
                "group.gou_gou_gou",
                title="狗狗狗",
                is_group=True,
                participants=[mu_xing, jiang_mu, ka_nuo],
                player=mu_xing,
                entries=[
                    wc_text(jiang_mu, "我在出站口出来左手边", timestamp=(2025, 12, 30, 11, 17)),
                ],
            )
        )
    if not wc_has_session("group.xiang_qin_xiang_ai_yi_jia_ren"):
        $ wc_register_session(
            WeChatSession(
                "group.xiang_qin_xiang_ai_yi_jia_ren",
                title="相亲相爱一家人",
                is_group=True,
                participants=[mu_xing, jiang_mu, ka_nuo, lao_ma],
                player=mu_xing,
                entries=[
                    wc_text(ka_nuo, "随便做点就行啦", timestamp=(2025, 12, 30, 10, 44)),
                ],
            )
        )

    # 设置当前时间
    $ wc_update_current_time((2026, 1, 5, 16, 7))

    # 显示主页
    call wechat_home

    # 插入实时会话
    $ wc_queue_text("chat.lao_ma", mu_xing, "妈", unread_increment=0)
    $ wc_queue_text("chat.lao_ma", mu_xing, "我应该下周三就回来了，出差一个月", unread_increment=0)
    $ wc_queue_text("chat.lao_ma", lao_ma, "这么快啊")
    $ wc_queue_text("chat.lao_ma", lao_ma, "怎么还能来咱们这地出差嘞")
    $ wc_queue_text("chat.lao_ma", lao_ma, "你可别被公司开了")
    $ wc_queue_text("chat.lao_ma", mu_xing, "……", unread_increment=0)
    $ wc_queue_text("chat.lao_ma", lao_ma, "哦对了，这周五张老师寿宴，要不你这周就回来吧")
    $ wc_queue_text("chat.lao_ma", mu_xing, "行，我问问我们老板", unread_increment=0)
    $ wc_queue_text("chat.lao_ma", lao_ma, "还有")
    $ wc_queue_text("chat.lao_ma", lao_ma, "我打算过两天出门，去走走和你爸以前去过的地方，还有本来说好一起去的地方")
    $ wc_queue_text("chat.lao_ma", lao_ma, "年前回")
    $ wc_queue_text("chat.lao_ma", mu_xing, "注意安全", unread_increment=0)

    # 显示会话
    call wechat_session("chat.lao_ma")

    "2026.1.9"
    $ wc_update_current_time((2026, 1, 9, 9, 0))

    $ wc_receive_text("chat.ka_nuo", mu_xing, "我这周五回来，出差，顺便看看张老师", timestamp=(2026, 1, 6, 14, 30), unread_increment=0)
    $ wc_receive_text("chat.ka_nuo", ka_nuo, "行，真想死你了", timestamp=(2026, 1, 6, 14, 30), unread_increment=0)
    $ wc_receive_text("chat.ka_nuo", ka_nuo, "你车次多少", timestamp=(2026, 1, 6, 14, 30), unread_increment=0)
    $ wc_receive_text("chat.ka_nuo", mu_xing, "C746", timestamp=(2026, 1, 6, 14, 30), unread_increment=0)

    $ wc_receive_text("chat.lao_ma", lao_ma, "我出发了")
    $ wc_push_toast("老妈：我出发了")

    "老妈出发了呢"

    $ wc_queue_text("chat.lao_ma", mu_xing, "我也出门了", unread_increment=0)
    $ wc_queue_text("chat.lao_ma", lao_ma, "位置发你了")
    $ wc_queue_text("chat.lao_ma", lao_ma, "【位置】")
    $ wc_queue_text("chat.lao_ma", lao_ma, "老大不小了，照顾好自己")
    $ wc_queue_text("chat.lao_ma", mu_xing, "知道了，你那边也记得给我报平安啊", unread_increment=0)
    $ wc_queue_text("chat.lao_ma", lao_ma, "👌")

    call wechat_session("chat.lao_ma")

    $ wc_receive_text("group.xiang_qin_xiang_ai_yi_jia_ren", lao_ma, "我出发啦")
    $ wc_push_toast("相亲相爱一家人：老妈发来新消息")

    call wechat_home

    "看看群吧"

    call wechat_session("group.xiang_qin_xiang_ai_yi_jia_ren")
    call wechat_session("group.gou_gou_gou")

    call wechat_show_chat("chat.ka_nuo")

    $ wc_queue_text("chat.ka_nuo", ka_nuo, "你怎么说？", timestamp=(2026, 1, 9, 9, 2))
    call wechat_overlay_reveal_next()
    "从家出来之后，卡诺先去忙自己的事了"

    $ wc_queue_text("chat.ka_nuo", mu_xing, "我先随便逛逛", timestamp=(2026, 1, 9, 9, 3), unread_increment=0)
    call wechat_overlay_reveal_next()
    "先这么发吧"

    $ wc_queue_text("chat.ka_nuo", ka_nuo, "晚上见", timestamp=(2026, 1, 9, 9, 4))
    call wechat_overlay_reveal_next()

    call wechat_hide_chat
