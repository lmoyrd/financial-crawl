from pydash import get
from crawler.converter.sz import\
    base_project,\
    process as _process,\
    build_stage_status_name,\
    build_process_stage,\
    build_process_stage_name,\
    build_process_stage_status_name,\
    time

_stage_status_name = build_stage_status_name('IPO_STATUS')

_process_stage = build_process_stage('ZRZ_STATUS')

_process_stage_name = build_process_stage_name('ZRZ_STATUS')

_process_stage_status_name = build_process_stage_status_name('ZRZ_STATUS')

# 上交所ipo的converter
project = {
    **base_project,
    'lastest_audit_end_time': time()
}




process = {
    **_process,
    'stage': _process_stage,
    'stage_name': _process_stage_name,
    'stage_status_name': _process_stage_status_name
}
