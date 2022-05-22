import os
import shutil

import pytest

from audioset_dl import _download, dl_seglist

DATASET_ROOT = f"{os.path.dirname(__file__)}/data"


@pytest.fixture(scope="module")
def make_temp_dir():
    os.makedirs(DATASET_ROOT, exist_ok=True)
    yield
    shutil.rmtree(DATASET_ROOT)


def test_download(make_temp_dir):
    ytid = "BaW_jenozKc"
    start = 0
    end = 10000
    save_path = f"{DATASET_ROOT}/{ytid}_{start}"
    _download([ytid, start, end, save_path])
    assert os.path.exists(save_path)


def test_dl_seglist(make_temp_dir):
    seglist_path = f"{DATASET_ROOT}/seglist.txt"
    seglist = ["b0RFKhbpFJA_30000", "NQNTnl0zaqU_70000", "LvNUyQ3xuAQ_0"]
    with open(seglist_path, "w") as f:
        f.write("\n".join(seglist))
    dl_seglist(DATASET_ROOT, seglist_path)
    for seg_id in seglist:
        assert os.path.exists(f"{DATASET_ROOT}/seglist/{seg_id}.wav")


if __name__ == "__main__":
    pytest.main(["-s", __file__])
