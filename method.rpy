default wechat_state = WeChatState()
default wechat_toast = None
default wechat_overlay_session_ref = None
default wechat_current_time = None
default wechat_overlay_hide_window_when_idle = False


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


label wechat_show_chat(session_ref, hide_window_when_idle=True):
    $ _wechat_overlay_session = wc_open_session(session_ref)
    $ wechat_overlay_session_ref = _wechat_overlay_session
    $ wechat_overlay_hide_window_when_idle = hide_window_when_idle
    show screen wechat_chat_overlay(session=_wechat_overlay_session)
    with None

    if wechat_overlay_hide_window_when_idle:
        window hide
        with config.window_hide_transition

    return


label wechat_hide_chat():
    $ wechat_overlay_hide_window_when_idle = False
    $ wc_hide_chat_overlay()
    return


label wechat_overlay_reveal_next(session_ref=None, wait_for_click=True):
    if wait_for_click:
        if wechat_overlay_hide_window_when_idle:
            window hide
            with config.window_hide_transition
        pause
    $ wc_overlay_reveal_next(session_ref=session_ref)
    return


label wechat_live_session(session_ref):
    call wechat_session(session_ref)
    return


