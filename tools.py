def ms_to_min_sec_text(ms):
    seconds=str(int((ms/1000)%60))
    minutes=str(int((ms/(1000*60))%60))
    hours= str(int(ms/(1000*60*60)%24))

    if len(seconds) == 0:
        seconds += '00'

    elif len(seconds) == 1:
        seconds = '0' + seconds

    if len(minutes) == 0:
        minutes += '00'

    elif len(minutes) == 1:
        minutes = '0' + minutes

    if len(hours) == 0:
        hours += '00'

    elif len(hours) == 1:
        hours = '0' + hours



    if int(hours) > 1:
        return f'{hours}:{minutes}:{seconds}'

    else:
        return f'{minutes}:{seconds}'