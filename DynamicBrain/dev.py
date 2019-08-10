import allensdk.brain_observatory.behavior.swdb.utilities as tools
from allensdk.brain_observatory.behavior.swdb import behavior_project_cache as bpc
cache_json = {'manifest_path': '/allen/programs/braintv/workgroups/nc-ophys/visual_behavior/SWDB_2019/visual_behavior_data_manifest.csv',
              'nwb_base_dir': '/allen/programs/braintv/workgroups/nc-ophys/visual_behavior/SWDB_2019/nwb_files',
              'analysis_files_base_dir': '/allen/programs/braintv/workgroups/nc-ophys/visual_behavior/SWDB_2019/extra_files_final'
              }
cache = bpc.BehaviorProjectCache(cache_json)
experiment_id = 792812544
session = cache.get_session(experiment_id)
tr = session.trial_response_df
fr = session.flash_response_df

import numpy as np
import pandas as pd
from scipy import stats

trial_response_df = add_p_vals_tr(trial_response_df)
trial_response_df = annotate_trial_response_df_with_pref_stim(trial_response_df)

def add_p_vals_tr(tr):
    tr['p_value'] = 1.
    response_window = [4, 4.5]  
    ophys_frame_rate=31.
    for index,row in tr.iterrows():
        tr.at[index,'p_value'] = get_p_val(row.dff_trace, response_window, ophys_frame_rate)
    return tr

def get_p_val(trace, response_window, frame_rate):
    response_window_duration = response_window[1] - response_window[0]
    baseline_end = int(response_window[0] * frame_rate)
    baseline_start = int((response_window[0] - response_window_duration) * frame_rate)
    stim_start = int(response_window[0] * frame_rate)
    stim_end = int((response_window[0] + response_window_duration) * frame_rate)
    (_, p) = stats.f_oneway(trace[baseline_start:baseline_end], trace[stim_start:stim_end])
    return p

def annotate_trial_response_df_with_pref_stim(trial_response_df):
    rdf = trial_response_df.copy()
    rdf['pref_stim'] = False
    cell_key = 'cell_specimen_id'
    mean_response = rdf.groupby([cell_key, 'change_image_name']).apply(get_mean_sem_trace)
    m = mean_response.unstack()
    for cell in m.index:
        image_index = np.where(m.loc[cell]['mean_response'].values == np.max(m.loc[cell]['mean_response'].values))[0][0]
        pref_image = m.loc[cell]['mean_response'].index[image_index]
        rdf = rdf.reset_index()
        rdf = rdf.set_index(['cell_specimen_id','change_image_name'])
        rdf.at[(cell,pref_image),'pref_stim'] = True
    rdf = rdf.reset_index()
    rdf = rdf.set_index(['cell_specimen_id','trial_id'])
    return rdf

def get_mean_sem_trace(group):
    '''
        Computes the average and sem of the mean_response column
    '''
    mean_response = np.mean(group['mean_response'])
    mean_responses = group['mean_response'].values
    sem_response = np.std(group['mean_response'].values) / np.sqrt(len(group['mean_response'].values))
    mean_trace = np.mean(group['dff_trace'])
    sem_trace = np.std(group['dff_trace'].values) / np.sqrt(len(group['dff_trace'].values))
    return pd.Series({'mean_response': mean_response, 'sem_response': sem_response,
                      'mean_trace': mean_trace, 'sem_trace': sem_trace,
                      'mean_responses': mean_responses})





