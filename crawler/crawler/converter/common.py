from datetime import datetime

def time(format = ''):
    def convert_time(originValue, *args):
        date_obj = None
        format_arr = ['%Y-%m-%d %H:%M:%S', '%Y%m%d%H%M%S', '%Y-%m-%d %H:%M', '%Y-%m-%d']
        
        if format != '': 
            format_arr.insert(0, format)
        
        for format_str in format_arr:
            try:
                date_obj = datetime.strptime(originValue, format_str)
                if date_obj != None:
                    break
            except:
                pass
        return int(round(date_obj.timestamp() * 1000)) if date_obj != None else None
        
    return convert_time
