default wechat_state = WeChatState()
default wechat_toast = None
default wechat_overlay_session_ref = None
default wechat_current_time = None


label wechat_home(inbox_items=None):
    $ _wechat_old_quick_menu = quick_menu
    $ quick_menu = False
    call screen wechat_home_screen(inbox_items=inbox_items)
    $ quick_menu = _wechat_old_quick_menu
    return


label wechat_session(session_ref):
    $ _wechat_old_quick_menu = quick_menu
    $ quick_menu = False
    $ _wechat_session = wc_open_session(session_ref)

label .wechat_session_loop:
    call screen wechat_chat(session=_wechat_session)

    if wc_has_pending(_wechat_session):
        $ wc_reveal_next(_wechat_session)
        jump .wechat_session_loop

    $ wc_close_session(_wechat_session)
    $ quick_menu = _wechat_old_quick_menu
    return


label wechat_show_chat(session_ref):
    $ _wechat_overlay_session = wc_open_session(session_ref)
    $ wechat_overlay_session_ref = _wechat_overlay_session
    show screen wechat_chat_overlay(session=_wechat_overlay_session)
    return


label wechat_hide_chat():
    if wechat_overlay_session_ref is not None:
        $ wc_close_session(wechat_overlay_session_ref)
        $ wechat_overlay_session_ref = None
    hide screen wechat_chat_overlay
    return


label wechat_live_session(session_ref):
    call wechat_session(session_ref)
    return


