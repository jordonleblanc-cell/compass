────────────────────── Traceback (most recent call last) ───────────────────────

  /home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptru  

  nner/exec_code.py:129 in exec_func_with_error_handling                        

                                                                                

  /home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptru  

  nner/script_runner.py:670 in code_to_exec                                     

                                                                                

  /home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptru  

  nner/script_runner.py:166 in _mpa_v1                                          

                                                                                

  /home/adminuser/venv/lib/python3.13/site-packages/streamlit/navigation/page.  

  py:310 in run                                                                 

                                                                                

  /mount/src/compass/pages/admin-test-redesign.py:87 in <module>                

                                                                                

     84 │   with c1:                                                            

     85 │   │   st.metric("Staff Assessed", len(df))                            

     86 │   with c2:                                                            

  ❱  87 │   │   st.metric("Avg Comm Score", round(df[["primarycomm", "secondar  

     88 │   with c3:                                                            

     89 │   │   st.metric("Avg Motivation", round(df[["primarymotiv", "seconda  

     90 │   with c4:                                                            

                                                                                

  /home/adminuser/venv/lib/python3.13/site-packages/pandas/core/frame.py:4119   

  in __getitem__                                                                

                                                                                

     4116 │   │   else:                                                         

     4117 │   │   │   if is_iterator(key):                                      

     4118 │   │   │   │   key = list(key)                                       

  ❱  4119 │   │   │   indexer = self.columns._get_indexer_strict(key, "columns  

     4120 │   │                                                                 

     4121 │   │   # take() does not accept boolean indexers                     

     4122 │   │   if getattr(indexer, "dtype", None) == bool:                   

                                                                                

  /home/adminuser/venv/lib/python3.13/site-packages/pandas/core/indexes/base.p  

  y:6212 in _get_indexer_strict                                                 

                                                                                

    6209 │   │   else:                                                          

    6210 │   │   │   keyarr, indexer, new_indexer = self._reindex_non_unique(k  

    6211 │   │                                                                  

  ❱ 6212 │   │   self._raise_if_missing(keyarr, indexer, axis_name)             

    6213 │   │                                                                  

    6214 │   │   keyarr = self.take(indexer)                                    

    6215 │   │   if isinstance(key, Index):                                     

                                                                                

  /home/adminuser/venv/lib/python3.13/site-packages/pandas/core/indexes/base.p  

  y:6261 in _raise_if_missing                                                   

                                                                                

    6258 │   │                                                                  

    6259 │   │   if nmissing:                                                   

    6260 │   │   │   if nmissing == len(indexer):                               

  ❱ 6261 │   │   │   │   raise KeyError(f"None of [{key}] are in the [{axis_na  

    6262 │   │   │                                                              

    6263 │   │   │   not_found = list(ensure_index(key)[missing_mask.nonzero()  

    6264 │   │   │   raise KeyError(f"{not_found} not in index")                

────────────────────────────────────────────────────────────────────────────────

KeyError: "None of [Index(['primarycomm', 'secondarycomm'], dtype='object')] are

in the [columns]"
