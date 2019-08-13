import argparse
import itertools
import gzip
import json
import os
from statistics import mean

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import seaborn as sns

register_matplotlib_converters()

CHART_NODE_DEGREE_FILE_NAME = 'chart-node_degree.png'
CHART_PDR_VS_CHANNEL_FILE_NAME = 'chart-pdr_vs_channel.png'
CHART_NUM_GOOD_CHANNELS_PER_NBR_FILE_NAME = 'chart-num_good_channels.png'
CHART_WATERFALL_RSSI_VS_PDR_FILE_NAME = 'chart-rssi_vs_pdr.png'
CHART_PDR_OVER_TIME_FILE_NAME = 'chart-pdr_over_time_from_{0}_to_{1}.png'


def _construct_bare_link_graph(df, node_count):
    df_per_channel = pd.pivot_table(df,
                                    values='pdr',
                                    index=['src', 'dst', 'channel'],
                                    aggfunc=np.mean)
    df_per_channel = df_per_channel.reset_index()
    df_overall = pd.pivot_table(df, values='pdr', index=['src', 'dst'],
                                    aggfunc=np.mean)
    df_overall = df_overall.reset_index()
    df_overall['channel'] = 'overall'
    df = pd.concat([df_per_channel, df_overall], sort=False)

    G = nx.MultiDiGraph()
    G.add_edges_from([(src, dst, channel, {'avg_pdr': pdr if pdr else 0})
                      for src, dst, channel, pdr in df.itertuples(index=False)])
    return G

def _construct_valid_link_graph(bare_link_graph, min_pdr):
    G = nx.Graph()
    for u, v in itertools.combinations(bare_link_graph.nodes, 2):
        link_u_v = bare_link_graph.get_edge_data(u, v, 'overall',
                                                 default={'avg_pdr': 0})
        link_v_u = bare_link_graph.get_edge_data(u, v, 'overall',
                                                 default={'avg_pdr': 0})

        if ((link_u_v['avg_pdr'] >= min_pdr)
            and (link_v_u['avg_pdr'] >= min_pdr)):
            # if the both directions have enough PDR values, we
            # consider the link as valid
            overall_avg_pdr = (link_u_v['avg_pdr'] + link_v_u['avg_pdr']) /2
            G.add_edge(u, v, overall_avg_pdr=overall_avg_pdr)
    return G

def _plot_node_degree(valid_link_graph):
    # plot node degree
    print('Generate a chart of node degree')
    plt.figure()
    data = [degree for _, degree in valid_link_graph.degree]
    ax = sns.distplot(data, bins=max(data),
                      kde=False, norm_hist=True, hist_kws={'cumulative': True})
    ax.set_xticks(range(0, max(data)))
    ax.set_xlabel('Node Degree')
    ax.set_xlim(0, max(data))
    ax.set_ylabel('Probability')
    ax.set_ylim(0, 1)
    plt.savefig(CHART_NODE_DEGREE_FILE_NAME)
    plt.close()

def _plot_pdr_vs_channel(df):
    # plot PDR vs channel
    print('Generate a chart of average PDR per channel, '
          + 'taking only PDR values > 0%')
    plt.figure()
    data = df[df['pdr'] > 0].copy()
    data['pdr'] *= 100
    ax = sns.barplot(x='channel', y='pdr', data=data,
                     color=sns.xkcd_rgb["windows blue"])
    # add vertical lines for WiFi Channels 1, 6, 11 their center
    # frequencies are roughly located at channel 12.5, 17.5, and 22.5
    # of IEEE 802.15.4
    ax.vlines(x=[1.5, 6.5, 11.5], ymin=0, ymax=100,
              linestyles='dashed', colors='red')
    ax.set_xlabel('IEEE 802.15.4 Channel (2.4GHz)')
    ax.set_ylabel('Average Link PDR (%)')
    ax.set_ylim(0, 100)
    plt.savefig(CHART_PDR_VS_CHANNEL_FILE_NAME)
    plt.close()

def _plot_num_channels_having_valid_links(df, min_pdr, channels):
    # plot number of channels with PDR >= min_pdr
    print('Generate a chart of number of channels with '
          + 'PDR >= {0}% (min_pdr)'.format(min_pdr * 100))
    plt.figure()
    data = pd.pivot_table(df,
                          values='pdr',
                          index=['src', 'dst', 'channel'],
                          aggfunc=np.mean)
    data = data.reset_index()
    data = data.loc[data['pdr'] >= min_pdr]
    data = pd.pivot_table(data,
                          values='channel',
                          index=['src', 'dst'],
                          aggfunc=len)
    data = data.reset_index()
    data = data['channel']
    ax = sns.distplot(data, bins=len(channels), kde=False,
                      norm_hist=True, hist_kws={'cumulative': True})
    ax.set_xlabel('Number of Channels with PDR >= {0}%'.format(min_pdr * 100))
    ax.set_ylabel('Probability')
    plt.savefig(CHART_NUM_GOOD_CHANNELS_PER_NBR_FILE_NAME)
    plt.close()

def _plot_waterfall_rssi_vs_pdr(df):
    # plot waterfall
    print('Generate a waterfall plot')
    plt.figure()
    data = df[df['pdr'] > 0].copy()
    data = data[['mean_rssi', 'pdr']]
    data['pdr'] *= 100
    ax = sns.scatterplot(x='mean_rssi', y='pdr', data=data, marker='+')
    ax.set_xticks([i for i in range(-100, 0, 10)])
    ax.set_xlabel('Average RSSI (dB)')
    ax.set_ylabel('PDR (%)')
    ax.set_ylim(0, 110)
    plt.savefig(CHART_WATERFALL_RSSI_VS_PDR_FILE_NAME)
    plt.close()

def _plot_pdr_over_time(df, src, dst, channels):
    print('Generate a chart for PDR over time from {0} to {1}'.format(src, dst))
    fig = plt.figure()
    data = df[(df['src']==src) & (df['dst']==dst)].copy()
    # use relative time in minutes ax index, from the first
    # measurement
    data['timedelta'] = data['datetime'] - min(data['datetime'])
    data['min'] = data.apply(lambda x: x['timedelta'].total_seconds() / 60,
                             axis=1)
    data = data.set_index('min')

    data_mean_pdr = pd.pivot_table(data, values='pdr', index='channel',
                                   aggfunc=np.mean)
    data_mean_pdr['pdr'] *= 100
    data_mean_pdr = data_mean_pdr.T.to_dict()

    _data = pd.DataFrame(index=data.index, columns=channels, dtype=int)
    _data.index.astype(data.index.dtype)
    _data.rename_axis('')
    del _data.index.name
    pdr_values = {channel: None for channel in channels}
    start_index = None
    for index, row in data.iterrows():
        pdr_values[row['channel']] = row['pdr'] * 100
        if (not start_index) and (None not in pdr_values.values()):
            start_index = index
        _data.loc[index] = list(pdr_values.values())
    data = _data.loc[start_index:]

    axes = data.plot.line(ylim=(0, 110), use_index=True, subplots=True,
                          sharex=True, legend=False,
                          style=['red' if channel % 2 else 'blue'
                                 for channel in channels])
    for channel, ax in zip(channels, axes):
        ax.set_xlabel('Elapsed Time (min)')
        ax.set_yticks([])
        ax.set_ylabel(channel,
                      rotation='horizontal', ha='right', va='center')
        ax_right = ax.twinx()
        ax_right.set_yticks([])
        ax_right.set_ylabel('{0}%'.format(int(data_mean_pdr[channel]['pdr'])),
                            rotation='horizontal', ha='left', va='center')

    fig = axes[0].figure
    fig.text(0.07, 0.55, 'PDR (%) per IEEE802.15.4 Channel',
             rotation='vertical', ha='center', va='center')
    plt.savefig(CHART_PDR_OVER_TIME_FILE_NAME.format(src, dst))
    plt.close('all')

def analyze_k7_file(k7_file_path, min_pdr, single_tx):
    with gzip.open(k7_file_path, 'rt') as f:
        config = json.loads(f.readline())
        df = pd.read_csv(f, header=0,
                         dtype={'datetime': str, 'src': int, 'dst': int,
                                'channel': int, 'mean_rssi': float,
                                'pdr': float, 'tx_count': int},
                         na_values='None',
                         parse_dates=[0])

    df['valid_link'] = df.apply(lambda x: 1 if x['pdr'] >= min_pdr else 0,
                                axis=1)

    bare_link_graph = _construct_bare_link_graph(df, config['node_count'])
    valid_link_graph = _construct_valid_link_graph(bare_link_graph, min_pdr)

    if single_tx:
        src_list = set(df['src'])
        assert len(src_list) > 0
        if len(src_list) > 1:
            print('Multiple TX nodes are found')
            print('Cannot use --single-tx with such a K7 file')
            exit(1)
        else:
            src = src_list.pop()
            for dst in set(df['dst']):
                _plot_pdr_over_time(df, src, dst, config['channels'])
    else:
        _plot_node_degree(valid_link_graph)
        _plot_pdr_vs_channel(df)
        _plot_num_channels_having_valid_links(df, min_pdr, config['channels'])
        _plot_waterfall_rssi_vs_pdr(df)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--min-pdr', dest='min_pdr',
                        help='minimum PDR(%%) of a valid link',
                        type=int, default=50)
    parser.add_argument('--single-tx', dest='single_tx',
                        help='generate charts for a single TX case',
                        action='store_true', default=False)
    parser.add_argument('k7_file_path',
                        help='path to a K7 file (.k7.gz) to analyze')
    args = parser.parse_args()

    if (args.min_pdr < 0) or (args.min_pdr > 100):
        raise ValueError('Invalid min_pdr value: {0}%'.format(args.min_pdr))
    min_pdr = args.min_pdr / 100.0

    if not os.path.exists(args.k7_file_path):
        raise ValueError('{0} doesn\'t exist'.format(args.raw_file_path))
    else:
        analyze_k7_file(args.k7_file_path, min_pdr, args.single_tx)

if __name__ == '__main__':
    main()
