
class Exploration:
    def __init__(self,data):
        self.data = data

    def missing_col(self,df):
        missing_values = df.isnull().sum()
        missing_values = missing_values.sort_values(ascending=False)

        return missing_values

    def df_info_(self,df):
        """
            Information about the DataFrame
        """

        features_dtypes = df.dtypes
        rows, columns = df.shape

        missing_cols = self.missing_col(df)
        features_names = missing_cols.index.values
        missing_values = missing_cols.values

        print('=' * 50)
        print('===> This data frame contains {} rows and {} columns'.format(rows, columns))
        print('=' * 50)

        print("{:13}{:13}{:30}{:15}".format('Feature Name'.upper(),
                                            'Data Format'.upper(),
                                            'Number of Missing Values'.upper(),
                                            'The first few samples'.upper()))

        for features_names, features_dtypes, missing_values in zip(features_names, features_dtypes[features_names],
                                                                   missing_values):
            print('{:15} {:14} {:20}'.format(features_names, str(features_dtypes), str(missing_values) + '-' +
                                             str(round(100 * missing_values / sum(missing_cols), 3)) + ' %'), end=" ")

            for i in range(5):
                print(df[features_names].iloc[i], end=",")

            print("=" * 50)