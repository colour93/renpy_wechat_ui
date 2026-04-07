screen wechat_home_screen(inbox_items=None):
    modal False
    zorder 90

    $ items = inbox_items if inbox_items is not None else wechat_state.inbox_items()

    key "dismiss" action Return()
    key "K_RETURN" action Return()

    use wechat_phone_shell():
        vbox:
            spacing 0

            frame:
                style "wechat_home_header"

                fixed:
                    xfill True
                    ysize 56

                    frame:
                        style "wechat_header_divider"
                        xfill True
                        yalign 1.0

                    text "微信" style "wechat_home_title"

            frame:
                style "wechat_home_body"

                viewport:
                    xfill True
                    yfill True
                    mousewheel True
                    draggable True
                    pagekeys True

                    vbox:
                        xfill True

                        for item in items:
                            use wechat_home_item(item)


screen wechat_home_item(item):
    $ avatar_contact = wc_session_avatar(item.session)
    $ preview_text = item.preview if item.preview is not None else wc_session_preview_display(item.session)
    $ metrics = wc_phone_metrics()
    $ row_width = metrics["screen_width"] - 54 - 14 - 28
    $ time_column_width = 150
    $ badge_column_width = 36
    $ title_text_column_width = row_width - time_column_width - 8
    $ preview_text_column_width = row_width - badge_column_width - 8

    frame:
        style "wechat_home_item_card"

        hbox:
            xfill True
            spacing 14

            use wechat_avatar(avatar_contact, size=54)

            vbox:
                xsize row_width
                spacing 6

                hbox:
                    xsize row_width
                    spacing 8

                    text wc_home_session_title(item.session) style "wechat_home_item_title" xsize title_text_column_width

                    if item.timestamp:
                        text item.timestamp style "wechat_home_item_time" xsize time_column_width
                    else:
                        null width time_column_width

                fixed:
                    xsize row_width
                    yfit True

                    text preview_text style "wechat_home_item_preview" xsize preview_text_column_width xpos 0

                    if item.unread_count:
                        frame:
                            style "wechat_home_unread_badge"
                            xpos row_width
                            xanchor 1.0

                            text wc_badge_text(item.unread_count) style "wechat_home_unread_text"


