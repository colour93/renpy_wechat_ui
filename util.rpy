define phone_font = "fonts/MiSans-Normal.otf"


init -2 python:
    import datetime
    import re
    import store

    try:
        string_types = (basestring,)
    except NameError:
        string_types = (str,)

    WC_TIMESTAMP_WINDOW_MINUTES = 10
    WC_WEEKDAY_NAMES = (
        u"\u5468\u4e00",
        u"\u5468\u4e8c",
        u"\u5468\u4e09",
        u"\u5468\u56db",
        u"\u5468\u4e94",
        u"\u5468\u516d",
        u"\u5468\u65e5",
    )


    class WeChatContact(object):
        def __init__(
            self,
            contact_id,
            name,
            avatar_color="#5b8def",
            bubble_color=None,
            role=None,
            avatar_image=None,
            avatar_text=None,
        ):
            self.contact_id = contact_id
            self.name = name
            self.avatar_color = avatar_color
            self.bubble_color = bubble_color
            self.role = role
            self.avatar_image = avatar_image
            self.avatar_text = avatar_text

        def initials(self):
            if self.avatar_text is not None:
                return self.avatar_text
            if not self.name:
                return "?"
            return self.name[0]


    class WeChatQuote(object):
        def __init__(self, sender_name, preview, kind="text"):
            self.sender_name = sender_name
            self.preview = preview
            self.kind = kind


    class WeChatEntry(object):
        def __init__(
            self,
            entry_type,
            sender=None,
            text=None,
            media=None,
            caption=None,
            quote=None,
            separator_text=None,
            separator_kind="system",
            timestamp=None,
        ):
            self.entry_type = entry_type
            self.sender = sender
            self.text = text
            self.media = media
            self.caption = caption
            self.quote = quote
            self.separator_text = separator_text
            self.separator_kind = separator_kind
            self.timestamp = timestamp


    class WeChatSession(object):
        def __init__(
            self,
            session_id,
            title,
            participants,
            player,
            entries=None,
            subtitle=None,
            is_group=False,
            avatar_contact=None,
            unread_count=0,
            last_timestamp=None,
            last_read_entry_count=None,
            active_divider_index=None,
            pending_entries=None,
        ):
            self.session_id = session_id
            self.title = title
            self.participants = participants
            self.player = player
            self.entries = list(entries or [])
            self.subtitle = subtitle
            self.is_group = is_group
            self.avatar_contact = avatar_contact
            self.unread_count = unread_count
            self.last_timestamp = last_timestamp
            self.last_read_entry_count = len(self.entries) if last_read_entry_count is None else last_read_entry_count
            self.active_divider_index = active_divider_index
            self.pending_entries = list(pending_entries or [])

        def add(self, entry):
            self.entries.append(entry)
            timestamp = wc_entry_timestamp(entry)
            if timestamp is not None:
                self.last_timestamp = timestamp
            return self


    class WeChatInboxItem(object):
        def __init__(self, session, timestamp=None, preview=None, unread_count=0):
            self.session = session
            self.timestamp = timestamp
            self.preview = preview
            self.unread_count = unread_count


    class WeChatToast(object):
        def __init__(self, message, duration=2.2):
            self.message = message
            self.duration = duration


    class WeChatState(object):
        def __init__(self):
            self.sessions = {}
            self.order = []

        def has_session(self, session_id):
            return session_id in self.sessions

        def register_session(self, session):
            wc_prepare_session(session)
            existing = self.sessions.get(session.session_id)

            if existing is None:
                self.sessions[session.session_id] = session
                self.order.insert(0, session.session_id)
                return session

            existing.title = session.title
            existing.participants = session.participants
            existing.player = session.player
            existing.subtitle = session.subtitle
            existing.is_group = session.is_group
            existing.avatar_contact = session.avatar_contact

            if session.entries:
                existing.entries = list(session.entries)
            if session.last_timestamp is not None:
                existing.last_timestamp = session.last_timestamp
            if session.last_read_entry_count is not None:
                existing.last_read_entry_count = session.last_read_entry_count
            if session.active_divider_index is not None:
                existing.active_divider_index = session.active_divider_index
            if session.pending_entries:
                existing.pending_entries = list(session.pending_entries)

            wc_prepare_session(existing)
            return existing

        def get_session(self, session_id):
            session = self.sessions[session_id]
            wc_prepare_session(session)
            return session

        def move_to_top(self, session_id):
            if session_id in self.order:
                self.order.remove(session_id)
            self.order.insert(0, session_id)

        def add_entry(self, session_id, entry, timestamp=None, unread_increment=None):
            session = self.get_session(session_id)
            normalized_timestamp = wc_assign_entry_timestamp(
                entry,
                timestamp=timestamp,
                default_now=True,
            )
            session.entries.append(entry)

            if normalized_timestamp is not None:
                session.last_timestamp = normalized_timestamp

            if unread_increment is None:
                is_other = (
                    entry.sender is not None
                    and session.player is not None
                    and entry.sender.contact_id != session.player.contact_id
                )
                unread_increment = 1 if is_other else 0

            session.unread_count = max(0, session.unread_count + unread_increment)
            self.move_to_top(session_id)
            return entry

        def queue_entry(self, session_id, entry, timestamp=None, unread_increment=None):
            session = self.get_session(session_id)
            normalized_timestamp = wc_assign_entry_timestamp(
                entry,
                timestamp=timestamp,
                default_now=True,
            )

            if normalized_timestamp is not None:
                session.last_timestamp = normalized_timestamp

            if unread_increment is None:
                is_other = (
                    entry.sender is not None
                    and session.player is not None
                    and entry.sender.contact_id != session.player.contact_id
                )
                unread_increment = 1 if is_other else 0

            session.unread_count = max(0, session.unread_count + unread_increment)
            session.pending_entries.append((entry, normalized_timestamp, unread_increment))
            self.move_to_top(session_id)
            return entry

        def has_pending(self, session_id):
            return bool(self.get_session(session_id).pending_entries)

        def reveal_next(self, session_id):
            session = self.get_session(session_id)

            if not session.pending_entries:
                return None

            entry, timestamp, unread_increment = session.pending_entries.pop(0)
            return self.add_entry(
                session_id,
                entry,
                timestamp=timestamp,
                # Pending entries already affected unread_count when queued.
                unread_increment=0,
            )

        def mark_read(self, session_id):
            self.get_session(session_id).unread_count = 0

        def open_session(self, session_id):
            session = self.get_session(session_id)
            session.unread_count = 0

            if len(session.entries) > session.last_read_entry_count or session.pending_entries:
                session.active_divider_index = session.last_read_entry_count
            else:
                session.active_divider_index = None

            return session

        def close_session(self, session_id):
            session = self.get_session(session_id)
            session.last_read_entry_count = len(session.entries)
            session.active_divider_index = None

        def inbox_items(self):
            items = []
            indexed_session_ids = list(enumerate(self.order))

            def sort_key(indexed_session):
                index, session_id = indexed_session
                session = self.sessions[session_id]
                timestamp = wc_session_last_timestamp(session)
                has_timestamp = 1 if timestamp is not None else 0
                return (
                    has_timestamp,
                    timestamp or datetime.datetime.min,
                    -index,
                )

            for index, session_id in sorted(indexed_session_ids, key=sort_key, reverse=True):
                session = self.sessions[session_id]
                items.append(
                    WeChatInboxItem(
                        session=session,
                        timestamp=wc_format_inbox_timestamp(wc_session_last_timestamp(session)),
                        preview=wc_session_preview_display(session),
                        unread_count=session.unread_count,
                    )
                )

            return items


    def wc_text(sender, text, quote=None, timestamp=None):
        return WeChatEntry("text", sender=sender, text=text, quote=quote, timestamp=timestamp)


    def wc_image(sender, caption, media=None, quote=None, timestamp=None):
        return WeChatEntry("image", sender=sender, media=media, caption=caption, quote=quote, timestamp=timestamp)


    def wc_separator(text, kind="system", timestamp=None):
        return WeChatEntry("separator", separator_text=text, separator_kind=kind, timestamp=timestamp)


    def wc_timestamp(text, timestamp=None):
        return WeChatEntry("separator", separator_text=text, separator_kind="timestamp", timestamp=timestamp)


    def wc_quote(sender_name, preview, kind="text"):
        return WeChatQuote(sender_name, preview, kind=kind)


    def wc_trim_timestamp(value):
        return value.replace(second=0, microsecond=0)


    def wc_now():
        current = getattr(store, "wechat_current_time", None)

        if isinstance(current, datetime.datetime):
            return wc_trim_timestamp(current)

        return wc_trim_timestamp(datetime.datetime.now())


    def wc_normalize_timestamp(value, reference=None):
        if value is None:
            return None

        if isinstance(value, datetime.datetime):
            return wc_trim_timestamp(value)

        if isinstance(value, datetime.date):
            return datetime.datetime(value.year, value.month, value.day)

        if isinstance(value, (tuple, list)):
            if len(value) == 5:
                return datetime.datetime(value[0], value[1], value[2], value[3], value[4])
            if len(value) == 3:
                return datetime.datetime(value[0], value[1], value[2])
            return None

        if not isinstance(value, string_types):
            return None

        text = value.strip()
        if not text:
            return None

        reference = reference or wc_now()

        for pattern in ("%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M", "%Y.%m.%d %H:%M"):
            try:
                return datetime.datetime.strptime(text, pattern)
            except ValueError:
                pass

        relative_match = re.match(u"^(\\u4eca\\u5929|\\u6628\\u5929|\\u524d\\u5929)\\s+(\\d{1,2}):(\\d{2})$", text)
        if relative_match:
            offset_map = {
                u"\u4eca\u5929": 0,
                u"\u6628\u5929": 1,
                u"\u524d\u5929": 2,
            }
            day_offset = offset_map.get(relative_match.group(1), 0)
            base_date = reference.date() - datetime.timedelta(days=day_offset)
            return datetime.datetime(
                base_date.year,
                base_date.month,
                base_date.day,
                int(relative_match.group(2)),
                int(relative_match.group(3)),
            )

        month_day_match = re.match(u"^(\\d{1,2})-(\\d{1,2})\\s+(\\d{1,2}):(\\d{2})$", text)
        if month_day_match:
            return datetime.datetime(
                reference.year,
                int(month_day_match.group(1)),
                int(month_day_match.group(2)),
                int(month_day_match.group(3)),
                int(month_day_match.group(4)),
            )

        time_only_match = re.match(u"^(\\d{1,2}):(\\d{2})$", text)
        if time_only_match:
            base_date = reference.date()
            return datetime.datetime(
                base_date.year,
                base_date.month,
                base_date.day,
                int(time_only_match.group(1)),
                int(time_only_match.group(2)),
            )

        return None


    def wc_entry_timestamp(entry):
        return wc_normalize_timestamp(getattr(entry, "timestamp", None))


    def wc_assign_entry_timestamp(entry, timestamp=None, default_now=False):
        normalized_timestamp = wc_normalize_timestamp(timestamp)

        if normalized_timestamp is None:
            normalized_timestamp = wc_entry_timestamp(entry)

        if normalized_timestamp is None and default_now and entry.entry_type in ("text", "image"):
            normalized_timestamp = wc_now()

        entry.timestamp = normalized_timestamp
        return normalized_timestamp


    def wc_prepare_session(session):
        inferred_timestamp = None

        for entry in session.entries:
            entry_timestamp = wc_entry_timestamp(entry)

            if entry.entry_type == "separator" and entry.separator_kind == "timestamp":
                if entry_timestamp is None:
                    entry_timestamp = wc_normalize_timestamp(entry.separator_text)
                    entry.timestamp = entry_timestamp
                inferred_timestamp = entry_timestamp or inferred_timestamp
                continue

            if entry_timestamp is None and inferred_timestamp is not None and entry.entry_type in ("text", "image"):
                entry.timestamp = inferred_timestamp
            elif entry_timestamp is not None:
                inferred_timestamp = entry_timestamp

        normalized_pending_entries = []
        inferred_pending_timestamp = inferred_timestamp

        for entry, timestamp, unread_increment in session.pending_entries:
            normalized_timestamp = wc_normalize_timestamp(timestamp)
            if normalized_timestamp is None:
                normalized_timestamp = wc_entry_timestamp(entry)
            if normalized_timestamp is None and inferred_pending_timestamp is not None and entry.entry_type in ("text", "image"):
                normalized_timestamp = inferred_pending_timestamp

            if normalized_timestamp is not None:
                entry.timestamp = normalized_timestamp
                inferred_pending_timestamp = normalized_timestamp

            normalized_pending_entries.append((entry, normalized_timestamp, unread_increment))

        session.pending_entries = normalized_pending_entries
        session.last_timestamp = wc_normalize_timestamp(session.last_timestamp)

        if session.last_timestamp is None:
            session.last_timestamp = wc_session_last_timestamp(session)

        return session


    def wc_session_last_timestamp(session):
        for entry, timestamp, unread_increment in reversed(session.pending_entries):
            normalized_timestamp = wc_normalize_timestamp(timestamp)
            if normalized_timestamp is not None:
                return normalized_timestamp

            normalized_timestamp = wc_entry_timestamp(entry)
            if normalized_timestamp is not None:
                return normalized_timestamp

        for entry in reversed(session.entries):
            normalized_timestamp = wc_entry_timestamp(entry)
            if normalized_timestamp is not None:
                return normalized_timestamp

            if entry.entry_type == "separator" and entry.separator_kind == "timestamp":
                normalized_timestamp = wc_normalize_timestamp(entry.separator_text)
                if normalized_timestamp is not None:
                    return normalized_timestamp

        return wc_normalize_timestamp(session.last_timestamp)


    def wc_format_time(timestamp):
        return timestamp.strftime("%H:%M")


    def wc_same_week(left, right):
        left_year, left_week, left_weekday = left.isocalendar()
        right_year, right_week, right_weekday = right.isocalendar()
        return left_year == right_year and left_week == right_week


    def wc_format_date_label(timestamp, current_time=None):
        current_time = current_time or wc_now()
        day_delta = (current_time.date() - timestamp.date()).days

        if day_delta == 0:
            return u"\u4eca\u5929"
        if day_delta == 1:
            return u"\u6628\u5929"
        if day_delta == 2:
            return u"\u524d\u5929"
        if day_delta > 2 and wc_same_week(timestamp, current_time):
            return WC_WEEKDAY_NAMES[timestamp.weekday()]
        if timestamp.year == current_time.year:
            return u"%d\u6708%d\u65e5" % (timestamp.month, timestamp.day)
        return u"%d\u5e74%d\u6708%d\u65e5" % (timestamp.year, timestamp.month, timestamp.day)


    def wc_format_timestamp(timestamp, current_time=None):
        if timestamp is None:
            return ""

        return u"%s %s" % (
            wc_format_date_label(timestamp, current_time=current_time),
            wc_format_time(timestamp),
        )


    def wc_format_inbox_timestamp(timestamp, current_time=None):
        if timestamp is None:
            return ""

        current_time = current_time or wc_now()
        day_delta = (current_time.date() - timestamp.date()).days

        if day_delta == 0:
            return wc_format_time(timestamp)

        return wc_format_date_label(timestamp, current_time=current_time)


    def wc_should_insert_timestamp(previous_timestamp, current_timestamp):
        if current_timestamp is None:
            return False
        if previous_timestamp is None:
            return True

        delta_seconds = (current_timestamp - previous_timestamp).total_seconds()
        if delta_seconds < 0:
            return True

        return delta_seconds > WC_TIMESTAMP_WINDOW_MINUTES * 60


    def wc_render_entries(session):
        rendered_entries = []
        previous_message_timestamp = None

        for entry_index, entry in enumerate(session.entries):
            if session.active_divider_index is not None and entry_index == session.active_divider_index:
                rendered_entries.append(("new_message_divider", None))

            if entry.entry_type == "separator" and entry.separator_kind == "timestamp":
                entry_timestamp = wc_entry_timestamp(entry)
                if entry_timestamp is None:
                    entry.timestamp = wc_normalize_timestamp(entry.separator_text)
                continue

            entry_timestamp = wc_entry_timestamp(entry)

            if entry.entry_type in ("text", "image") and wc_should_insert_timestamp(previous_message_timestamp, entry_timestamp):
                rendered_entries.append(("entry", wc_timestamp(wc_format_timestamp(entry_timestamp), timestamp=entry_timestamp)))

            if entry.entry_type in ("text", "image") and entry_timestamp is not None:
                previous_message_timestamp = entry_timestamp

            rendered_entries.append(("entry", entry))

        return rendered_entries


    def wc_update_current_time(timestamp=None, days=0, hours=0, minutes=0):
        if timestamp is not None:
            current_time = wc_normalize_timestamp(timestamp, reference=wc_now())
        else:
            current_time = wc_now() + datetime.timedelta(days=days, hours=hours, minutes=minutes)

        if current_time is None:
            raise Exception("Invalid WeChat timestamp: %r" % (timestamp,))
        store.wechat_current_time = wc_trim_timestamp(current_time)

        try:
            renpy.restart_interaction()
        except Exception:
            pass

        return store.wechat_current_time


    def wc_last_content_entry(session):
        for entry in reversed(session.entries):
            if entry.entry_type in ("text", "image"):
                return entry
            if entry.entry_type == "separator" and entry.separator_kind != "timestamp":
                return entry
        return None


    def wc_session_title(session):
        if session.is_group:
            return "%s (%d)" % (session.title or "", len(session.participants or []))
        return session.title or ""


    def wc_home_session_title(session):
        return session.title or ""


    def wc_entry_preview_text(entry):
        if entry is None:
            return ""
        if entry.entry_type == "text":
            return entry.text or ""
        if entry.entry_type == "image":
            caption = entry.caption or ""
            if caption:
                return "[图片] %s" % caption
            return "[图片]"
        return entry.separator_text or ""


    def wc_session_preview(session):
        entry = wc_last_content_entry(session)

        if entry is None:
            return ""
        if entry.entry_type == "text":
            return entry.text
        if entry.entry_type == "image":
            return "[图片] %s" % (entry.caption or "")
        return entry.separator_text or ""


    def wc_session_preview_display(session):
        entry = wc_last_content_entry(session)
        preview_text = wc_entry_preview_text(entry)

        if entry is None:
            return ""
        if session.is_group and entry.entry_type in ("text", "image"):
            is_self = (
                entry.sender is not None
                and session.player is not None
                and entry.sender.contact_id == session.player.contact_id
            )
            if entry.sender is not None and not is_self:
                return u"%s\uff1a%s" % (entry.sender.name, preview_text)
        return preview_text


    def wc_session_avatar(session):
        if session.avatar_contact is not None:
            return session.avatar_contact

        if not session.is_group:
            for participant in session.participants:
                if session.player is None or participant.contact_id != session.player.contact_id:
                    return participant

        return WeChatContact(
            "session.%s" % session.session_id,
            session.title,
            avatar_color="#59636e",
            avatar_text=session.title[:1] if session.title else "群",
        )


    def wc_quote_text(quote):
        return u"%s：%s" % (quote.sender_name, quote.preview)


    def wc_badge_text(count):
        if count > 99:
            return "99+"
        return str(count)


    def wc_phone_metrics():
        outer_margin = 24
        device_height = config.screen_height - outer_margin * 2
        device_width = int(device_height * 9.0 / 20.0)

        if device_width > config.screen_width - outer_margin * 2:
            device_width = config.screen_width - outer_margin * 2
            device_height = int(device_width * 20.0 / 9.0)

        bezel = 12

        return {
            "outer_margin": outer_margin,
            "device_width": device_width,
            "device_height": device_height,
            "bezel": bezel,
            "screen_width": device_width - bezel * 2,
            "screen_height": device_height - bezel * 2,
            "avatar_size": 52,
            "bubble_width": int((device_width - bezel * 2) * 0.64),
            "quote_width": int((device_width - bezel * 2) * 0.54),
        }


    def wc_resolve_session(session_ref):
        if isinstance(session_ref, WeChatSession):
            return wc_register_session(session_ref)
        return store.wechat_state.get_session(session_ref)


    def wc_has_session(session_id):
        return store.wechat_state.has_session(session_id)


    def wc_register_session(session):
        return store.wechat_state.register_session(session)


    def wc_mark_read(session_ref):
        session = wc_resolve_session(session_ref)
        store.wechat_state.mark_read(session.session_id)
        return session


    def wc_open_session(session_ref):
        session = wc_resolve_session(session_ref)
        return store.wechat_state.open_session(session.session_id)


    def wc_close_session(session_ref):
        session = wc_resolve_session(session_ref)
        store.wechat_state.close_session(session.session_id)
        return session


    def wc_send_entry(session_ref, entry, timestamp=None, unread_increment=None):
        session = wc_resolve_session(session_ref)
        return store.wechat_state.add_entry(
            session.session_id,
            entry,
            timestamp=timestamp,
            unread_increment=unread_increment,
        )


    def wc_queue_entry(session_ref, entry, timestamp=None, unread_increment=None):
        session = wc_resolve_session(session_ref)
        return store.wechat_state.queue_entry(
            session.session_id,
            entry,
            timestamp=timestamp,
            unread_increment=unread_increment,
        )


    def wc_send_text(session_ref, sender, text, quote=None, timestamp=None, unread_increment=None):
        return wc_send_entry(
            session_ref,
            wc_text(sender, text, quote=quote),
            timestamp=timestamp,
            unread_increment=unread_increment,
        )


    def wc_receive_text(session_ref, sender, text, quote=None, timestamp=None, unread_increment=None):
        return wc_send_text(
            session_ref,
            sender,
            text,
            quote=quote,
            timestamp=timestamp,
            unread_increment=unread_increment,
        )


    def wc_receive_separator(session_ref, text, kind="system", timestamp=None):
        return wc_send_entry(
            session_ref,
            wc_separator(text, kind=kind),
            timestamp=timestamp,
            unread_increment=0,
        )


    def wc_receive_timestamp(session_ref, text):
        return wc_send_entry(
            session_ref,
            wc_timestamp(text),
            unread_increment=0,
        )


    def wc_queue_text(session_ref, sender, text, quote=None, timestamp=None, unread_increment=None):
        return wc_queue_entry(
            session_ref,
            wc_text(sender, text, quote=quote),
            timestamp=timestamp,
            unread_increment=unread_increment,
        )


    def wc_send_image(session_ref, sender, caption, media=None, quote=None, timestamp=None, unread_increment=None):
        return wc_send_entry(
            session_ref,
            wc_image(sender, caption, media=media, quote=quote),
            timestamp=timestamp,
            unread_increment=unread_increment,
        )


    def wc_receive_image(session_ref, sender, caption, media=None, quote=None, timestamp=None, unread_increment=None):
        return wc_send_image(
            session_ref,
            sender,
            caption,
            media=media,
            quote=quote,
            timestamp=timestamp,
            unread_increment=unread_increment,
        )


    def wc_queue_separator(session_ref, text, kind="system", timestamp=None):
        return wc_queue_entry(
            session_ref,
            wc_separator(text, kind=kind),
            timestamp=timestamp,
            unread_increment=0,
        )


    def wc_queue_timestamp(session_ref, text):
        return wc_queue_entry(
            session_ref,
            wc_timestamp(text),
            unread_increment=0,
        )


    def wc_queue_image(session_ref, sender, caption, media=None, quote=None, timestamp=None, unread_increment=None):
        return wc_queue_entry(
            session_ref,
            wc_image(sender, caption, media=media, quote=quote),
            timestamp=timestamp,
            unread_increment=unread_increment,
        )


    def wc_has_pending(session_ref):
        session = wc_resolve_session(session_ref)
        return store.wechat_state.has_pending(session.session_id)


    def wc_reveal_next(session_ref):
        session = wc_resolve_session(session_ref)
        return store.wechat_state.reveal_next(session.session_id)


    def wc_push_toast(message, duration=2.2):
        toast = WeChatToast(message, duration=duration)
        store.wechat_toast = toast
        renpy.show_screen("wechat_top_toast", toast=toast)
        renpy.restart_interaction()
        return toast


    def wc_clear_toast():
        store.wechat_toast = None
        renpy.hide_screen("wechat_top_toast")
        renpy.restart_interaction()


