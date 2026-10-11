from datetime import date, datetime, timedelta, timezone

from mcp_ical.models import Event

PARIS = timezone(timedelta(hours=2))


def make(title, start, **kw):
    return Event(title=title, start_time=start, end_time=start, identifier=f"id-{title}", **kw)


def test_sort_mixes_all_day_naive_and_aware():
    events = [
        make("aware-13", datetime(2026, 10, 13, 15, 30, tzinfo=PARIS)),
        make("allday-14", date(2026, 10, 14), all_day=True),
        make("aware-12", datetime(2026, 10, 12, 16, 40, tzinfo=PARIS)),
        make("naive-12-morning", datetime(2026, 10, 12, 8, 0)),
    ]
    events.sort(key=Event.sort_key)
    assert [e.title for e in events] == ["naive-12-morning", "aware-12", "aware-13", "allday-14"]


def test_str_omits_empty_fields_but_keeps_identifier():
    out = str(make("Dentist", datetime(2030, 1, 7, 9, 30, tzinfo=PARIS), calendar_name="Work"))
    assert "Identifier: id-Dentist" in out
    assert "Calendar: Work" in out
    assert "N/A" not in out
    for absent in ("Location", "Notes", "Alarms", "URL", "All Day", "Organizer", "Attendees", "recurrence"):
        assert absent not in out


def test_str_shows_filled_fields():
    out = str(
        make(
            "Meeting",
            date(2026, 10, 14),
            all_day=True,
            location="Office",
            alarms_minutes_offsets=[15, 60],
            attendees=["a@b.fr"],
        )
    )
    assert "Location: Office" in out
    assert "Alarms (minutes before): 15, 60" in out
    assert "All Day Event: yes" in out
    assert "Attendees: a@b.fr" in out
