import wave, random

def concat_wav_files(outfname, args):
    """Concatenate a list of wave files"""
    fnames = []
    for x in args:
        if len(x) > 0:
            if len(x) == 1 and isinstance(x, list) \
                    and not isinstance(x, str):
                fnames.extend(x)
            else:
                fnames.append(x)
        else:
            pass

    with wave.open(outfname,
                   'wb') as wav_out:
        for wav_path in fnames:
            with wave.open(wav_path,
                           'rb') as wav_in:
                if not wav_out.getnframes():
                    wav_out.setparams(wav_in.getparams())
                wav_out.writeframes(wav_in.readframes(wav_in.getnframes()))
    return(outfname)

def file_durations(flist):
    """Find the duration in seconds of each of a list of wave files"""

    if isinstance(flist, str):
        fnames = [flist]
    else:
        fnames = flist

    out = []
    for x in fnames:
        with wave.open(x,
                       "rb") as f:
            out.append( f.getnframes()/float(f.getframerate()))
    return(out)

def random_audio_file(file_list, duration, new_filename):
    """Choose a random sequence of files from file_list whose duration
    is at least duration."""

    files = list( zip(file_list,
                      file_durations(file_list)) )
    time_used = 0

    chosen = []
    while(time_used < duration):
        this_file, this_duration = random.choice(files)
        chosen.append(this_file)
        time_used += this_duration

    return(concat_wav_files(new_filename, chosen))
