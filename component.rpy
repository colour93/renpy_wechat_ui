screen wechat_phone_shell():
    $ metrics = wc_phone_metrics()

    fixed:
        xfill True
        yfill True

        frame:
            style "wechat_device_outer"
            xalign 0.5
            yalign 0.5
            xsize metrics["device_width"]
            ysize metrics["device_height"]

            fixed:
                xfill True
                yfill True

                frame:
                    style "wechat_device_bezel"
                    xfill True
                    yfill True

                frame:
                    style "wechat_device_screen"
                    xpos metrics["bezel"]
                    ypos metrics["bezel"]
                    xsize metrics["screen_width"]
                    ysize metrics["screen_height"]

                    transclude


screen wechat_top_toast(toast=None):
    zorder 95

    if toast is None:
        $ toast = wechat_toast

    if toast is not None:
        $ metrics = wc_phone_metrics()

        frame:
            style "wechat_toast_frame"
            xalign 0.5
            ypos metrics["outer_margin"] + 22
            xmaximum metrics["screen_width"] - 40

            text toast.message style "wechat_toast_text"

        timer toast.duration action Function(wc_clear_toast)



screen wechat_avatar(contact, size=64):
    frame:
        style "wechat_avatar"
        background Solid(contact.avatar_color)
        xsize size
        ysize size

        if contact.avatar_image is not None:
            add Transform(contact.avatar_image, fit="cover", xsize=size, ysize=size)
        else:
            text contact.initials() style "wechat_avatar_text"


screen wechat_message_body(entry, bubble_width=320):
    vbox:
        spacing 8

        if entry.entry_type == "text":
            text entry.text style "wechat_bubble_text"

        elif entry.entry_type == "image":
            frame:
                style "wechat_media_frame"
                xmaximum bubble_width - 36

                vbox:
                    xalign 0.5
                    yalign 0.5
                    spacing 8

                    if entry.media is not None:
                        add Transform(
                            entry.media,
                            fit="contain",
                            xsize=bubble_width - 68,
                            ysize=280,
                        ) xalign 0.5
                    else:
                        text "图片" style "wechat_media_badge"

                    if entry.caption:
                        text entry.caption style "wechat_media_caption"


