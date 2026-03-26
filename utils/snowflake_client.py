import os
import pandas as pd
import snowflake.connector as sc
from snowflake.connector.pandas_tools import write_pandas

class snowflake_client:
    def __init__(self, logger, conn_params):
        self.logger = logger
        # connect to snowflake
        self.snow_conn = sc.connect(**conn_params)

    def run_query_get_results(self, query):
        with self.snow_conn.cursor() as cur:
            cur.execute(query)
            results = cur.fetchone()[0]
            
        return results

    def run_query_get_dataframe(self, query):
        with self.snow_conn.cursor() as cur:
            try:
                cur.execute(query)
                results = cur.fetch_pandas_all()
                # ^for some reason fetch_pandas_all() often fails, not sure why
            except:
                self.logger.info("fetch_pandas_all failed, making dataframe the manual way")
                rows = cur.fetchall()
                cols = [col[0] for col in cur.description]
                results = pd.DataFrame(rows, columns=cols)
            
        return results
    
    def load_data_snowflake(self,df,dest_table,):
        success, num_chunks, num_rows, _ = write_pandas(
            conn=self.snow_conn,
            df=df,
            table_name=dest_table,
            quote_identifiers=False
        )
        return success, num_chunks, num_rows, _ 

    
    def run_script(self, script):
        cursors = self.snow_conn.execute_string(script)
        num_cursors = len(cursors)
        # get results for each individual query in script
        for x in range(num_cursors):
            cursor = cursors[x]
            result = cursor.fetchone()[0]
            print(f"      {result}")
            self.logger.info(f"      {result}")
        
        return

    
    def close_conn(self):
        if self.snow_conn:
            self.snow_conn.close()
            self.logger.info("snowflake connection closed")
            print("snowflake connection closed")