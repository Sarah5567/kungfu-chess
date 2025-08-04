import pytest
from unittest.mock import MagicMock
from Log import Log

def test_log_initially_empty():
    log = Log()
    assert log.log == []

def test_log_updates_with_valid_time():
    event = MagicMock()
    event.data = {
        'time': 3723000,  # 1 hour, 2 minutes, 3 seconds
        'source': 'A1',
        'destination': 'B2'
    }

    log = Log()
    log.update_log(event)

    assert len(log.log) == 1
    assert log.log[0]['time'] == '01:02:03'
    assert log.log[0]['source'] == 'A1'
    assert log.log[0]['destination'] == 'B2'

def test_log_updates_with_invalid_time_prints_warning_and_defaults_to_zero(capsys):
    event = MagicMock()
    event.data = {
        'time': 'invalid',
        'source': 'A2',
        'destination': 'B3'
    }

    log = Log()
    log.update_log(event)

    captured = capsys.readouterr()
    assert "Invalid time format" in captured.out

    assert len(log.log) == 1
    assert log.log[0]['time'] == '00:00:00'
    assert log.log[0]['source'] == 'A2'
    assert log.log[0]['destination'] == 'B3'

def test_log_multiple_entries():
    log = Log()

    for i in range(3):
        event = MagicMock()
        event.data = {
            'time': i * 1000,
            'source': f'A{i}',
            'destination': f'B{i}'
        }
        log.update_log(event)

    assert len(log.log) == 3
    assert log.log[0]['time'] == '00:00:00'
    assert log.log[1]['time'] == '00:00:01'
    assert log.log[2]['time'] == '00:00:02'
