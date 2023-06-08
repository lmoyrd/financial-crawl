

from pydash import get
from crawler.converter.sh import\
    base_project,\
    process as _process,\
    build_stage_status, build_stage_status_name

_stage_status = build_stage_status('ZRZ_STATUS')

_stage_status_name = build_stage_status_name('ZRZ_STATUS', _stage_status)


# 上交所ipo的converter
project = {
    **base_project,
    'stage_status': _stage_status,
    'stage_status_name': _stage_status_name,
    
}



process = {
    **_process,
    'stage_status': _stage_status,
    'stage_status_name': _stage_status_name,
}

