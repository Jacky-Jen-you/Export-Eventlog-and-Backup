import enum
from datetime import datetime
import win32evtlog
import os


class ELogType(enum.IntEnum):
    Application = 0
    System = enum.auto()


def get_current_time():
    now = datetime.now()

    return now.strftime('%Y%m%d_(%H-%M-%S)')


def export(log_name: ELogType, output_dir):
    current_date = get_current_time()

    output_filename = f'{log_name.name}_{current_date}.evtx'

    output_filename = os.path.join(output_dir, output_filename)

    try:
        win32evtlog.EvtExportLog(log_name.name, output_filename, 1)

    except:
        print(f'An exception occurred in the export {log_name.name} event log.')

        return False

    return True
