screen wechat_chat(session):
    modal False
    zorder 90

    key "dismiss" action Return()
    key "K_RETURN" action Return()

    use wechat_chat_panel(session=session)


screen wechat_live_chat(session):
    modal False
    zorder 90

    key "dismiss" action Return()
    key "K_RETURN" action Return()

    use wechat_chat_panel(session=session)


screen wechat_chat_overlay(session):
    zorder -10

    use wechat_chat_panel(session=session)


screen wechat_chat_panel(session):
    $ metrics = wc_phone_metrics()
    $ rendered_entries = wc_render_entries(session)
    $ header_height = 64

    use wechat_phone_shell():
        vbox:
            spacing 0

            frame:
                style "wechat_header"

                fixed:
                    xfill True
                    ysize header_height

                    if session.subtitle:
                        vbox:
                            xalign 0.5
                            yalign 0.5
                            spacing 1

                            text wc_session_title(session) style "wechat_header_title"
                            text session.subtitle style "wechat_header_subtitle"
                    else:
                        text wc_session_title(session) style "wechat_header_title" xalign 0.5 yalign 0.5

                    frame:
                        style "wechat_header_divider"
                        xfill True
                        yalign 1.0

            frame:
                style "wechat_body"

                viewport:
                    xfill True
                    yfill True
                    mousewheel True
                    draggable True
                    pagekeys True
                    yinitial 1.0

                    vbox:
                        style "wechat_message_list"

                        for item_kind, entry in rendered_entries:
                            if item_kind == "new_message_divider":
                                use wechat_new_message_divider()
                            elif entry.entry_type == "separator":
                                use wechat_separator_entry(entry)
                            else:
                                $ is_self = (
                                    entry.sender is not None
                                    and session.player is not None
                                    and entry.sender.contact_id == session.player.contact_id
                                )
                                use wechat_message_entry(
                                    entry,
                                    show_name=session.is_group and not is_self,
                                    is_self=is_self,
                                    bubble_width=metrics["bubble_width"],
                                    quote_width=metrics["quote_width"],
                                    avatar_size=metrics["avatar_size"],
                                )

screen wechat_new_message_divider():
    frame:
        style "wechat_new_message_frame"
        xalign 0.5

        text "以下是新消息" style "wechat_new_message_text"


screen wechat_separator_entry(entry):
    frame:
        style ("wechat_timestamp_frame" if entry.separator_kind == "timestamp" else "wechat_separator_frame")
        xalign 0.5

        text entry.separator_text style ("wechat_timestamp_text" if entry.separator_kind == "timestamp" else "wechat_separator_text")


screen wechat_message_entry(entry, show_name=False, is_self=False, bubble_width=320, quote_width=260, avatar_size=52):
    $ sender = entry.sender

    if is_self:
        hbox:
            xalign 1.0
            spacing 12

            vbox:
                spacing 8
                xmaximum bubble_width
                xalign 1.0

                if show_name:
                    text sender.name style "wechat_sender_name_self"

                frame:
                    style "wechat_bubble_self"
                    background Solid(sender.bubble_color or "#96ec69")
                    xmaximum bubble_width

                    use wechat_message_body(entry, bubble_width=bubble_width)

                if entry.quote is not None:
                    frame:
                        style "wechat_quote_chip"
                        xalign 1.0
                        xmaximum quote_width

                        text wc_quote_text(entry.quote) style "wechat_quote_text"

            use wechat_avatar(sender, size=avatar_size)

    else:
        hbox:
            xalign 0.0
            yalign 0.0
            spacing 12

            use wechat_avatar(sender, size=avatar_size)

            vbox:
                spacing 8
                xmaximum bubble_width
                yalign 0.0

                if show_name:
                    text sender.name style "wechat_sender_name"

                frame:
                    style "wechat_bubble_other"
                    background Solid(sender.bubble_color or "#ffffff")
                    xmaximum bubble_width

                    use wechat_message_body(entry, bubble_width=bubble_width)

                if entry.quote is not None:
                    frame:
                        style "wechat_quote_chip"
                        xmaximum quote_width

                        text wc_quote_text(entry.quote) style "wechat_quote_text"


