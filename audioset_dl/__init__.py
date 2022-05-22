import datetime as dt
import multiprocessing as mp
import os

import pandas as pd
from tqdm import tqdm
from youtube_dl import YoutubeDL


def _download(x):
    ytid, start, end, out_dir = x
    start_dt, end_dt = dt.timedelta(milliseconds=start), dt.timedelta(milliseconds=end)
    ydl_opts = {
        "outtmpl": f"{out_dir}/%(id)s_{start}.%(ext)s",
        "format": "bestaudio/best",
        "external_downloader": "ffmpeg",
        "external_downloader_args": ["-ss", str(start_dt), "-to", str(end_dt), "-loglevel", "panic"],
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
            }
        ],
        "quiet": True,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={ytid}"])
    except KeyboardInterrupt:
        raise
    except Exception:
        pass


def download_ps(ytid, st_list, ed_list, save_path, desc=None):
    with mp.Pool(processes=mp.cpu_count() // 2) as pool, tqdm(total=len(ytid), desc=desc) as pbar:
        for _ in tqdm(pool.imap(_download, zip(ytid, st_list, ed_list, [save_path] * len(ytid)))):
            pbar.update()


def dl_audioset_strong(save_path, split):
    path = f"{save_path}/{split}_strong"
    os.makedirs(path, exist_ok=True)
    meta = pd.read_csv(f"audioset_dl/metadata/audioset_{split}_strong.tsv", sep="\t")
    segment_id = pd.Series(meta.segment_id.unique())
    ytid = segment_id.str[:11]
    start_time = segment_id.str[12:].astype(int)
    end_time = start_time + 10000
    download_ps(ytid, start_time, end_time, path, desc=f"dl_{split}_strong")


def dl_audioset(save_path, split):
    path = f"{save_path}/{split}"
    os.makedirs(path, exist_ok=True)
    meta = pd.read_csv(f"audioset_dl/metadata/{split}_segments.csv", header=2, quotechar='"', skipinitialspace=True)
    ytid = meta["# YTID"]
    start_time = (meta.start_seconds * 1000).astype(int)
    end_time = (meta.end_seconds * 1000).astype(int)
    download_ps(ytid, start_time, end_time, path, desc=f"dl_{split}")


def dl_seglist(save_path, seglist_path):
    path = f"{save_path}/seglist"
    os.makedirs(path, exist_ok=True)
    segment_id = pd.Series(open(seglist_path, "r").read().splitlines())
    ytid = segment_id.str[:11]
    start_time = segment_id.str[12:].astype(int)
    end_time = start_time + 10000
    download_ps(ytid, start_time, end_time, path, desc="dl_seglist")
