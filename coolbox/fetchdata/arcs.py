import os.path as osp
import subprocess as subp
import pandas as pd

from coolbox.fetchdata.base import FetchTrackData
from coolbox.utilities import (
    to_gr, get_logger,
)


log = get_logger(__name__)


def bgz_bedpe(bedpe_path, bgz_path):
    if not osp.exists(bgz_path):
        cmd = f"sort -k1,1 -k4,4 -k2,2n -k5,5n {bedpe_path} | bgzip > {bgz_path}"
        subp.check_call(cmd, shell=True)


def index_bedpe(bgz_path):
    cmd = f"pairix -s 1 -d 4 -b 2 -e 3 -u 5 -v 6 {bgz_path}".split(" ")
    subp.check_call(cmd)


def pairix_query(bgz_file, query, second=None, split=True):
    cmd = ['pairix', bgz_file, query]
    if second:
        cmd.append(second)
    p = subp.Popen(cmd, stdout=subp.PIPE)
    for line in p.stdout:
        line = line.decode('utf-8')
        if not split:
            yield line
        else:
            yield line.strip().split('\t')


def process_bedpe(path):
    if path.endswith(".bgz"):
        bgz_file = path
    else:
        bgz_file = path + ".bgz"
        bgz_bedpe(path, bgz_file)
    if not osp.exists(f"{bgz_file}.px2"):
        index_bedpe(bgz_file)
    return bgz_file


class FetchBEDPE(FetchTrackData):

    def __init__(self, *args, **kwargs):
        path = self.properties['file']
        self.bgz_file = process_bedpe(path)

    def fetch_data(self, genome_range):
        """
        Parameters
        ----------
        genome_range : {str, GenomeRange}

        Return
        ------
        intervals : pandas.core.frame.DataFrame
            Arcs interval table.
        """
        return self.fetch_intervals(genome_range)

    def fetch_intervals(self, genome_range, open_query=True):
        gr = to_gr(genome_range)
        rows = self.__load(gr, open_query)
        fields = ["chrom1", "start1", "end1", "chrom2", "start2", "end2",
                  "name", "score", "strand1", "strand2"]
        if len(rows) == 0:
            gr.change_chrom_names()
            rows = self.__load(gr, open_query)
        if len(rows) == 0:
            return pd.DataFrame([], columns=fields)

        _row = rows[0]
        _diff = len(_row) - len(fields)
        if _diff > 0:
            fields += [f"extra_{i}" for i in range(_diff)]
        df = pd.DataFrame(rows, columns=fields)
        # Convert type of columns
        df['start1'] = df['start1'].astype(int)
        df['end1'] = df['end1'].astype(int)
        df['start2'] = df['start2'].astype(int)
        df['end2'] = df['start2'].astype(int)
        try:
            float(_row[7])
            df['score'] = df['score'].astype(float)
        except ValueError:
            pass
        return df

    def __load(self, gr, open_):
        rows = []
        second = gr.chrom if open_ else None
        g = pairix_query(self.bgz_file, str(gr), second=second, split=True)
        for row_item in g:
            rows.append(row_item)
        return rows
