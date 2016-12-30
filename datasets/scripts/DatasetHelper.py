class DatasetHelper(object):

    def __init__(self, df, testbed=None):
        self.node_count = None
        self.tx_count = None
        self.testbed = testbed

        # remove wrong values

        df.drop_duplicates(inplace=True)
        df = df[(df.crc == 1) & (df.expected == 1)]

        # extract dataset properties

        self.node_count = len(df.groupby(df["mac"]))
        self.tx_count = df["txnumpk"].iloc[0]
