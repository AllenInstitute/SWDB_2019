import numpy as np
import pandas as pd

def get_mean_df(response_df, analysis=None, conditions=['cell_specimen_id', 'image_name'], flashes=False, omitted=False, get_reliability=False):
    '''
        Computes an analysis on a selection of responses (either flashes or trials). Computes mean_response, sem_response, the pref_stim, fraction_active_responses. 
        
        Returns a dataframe, does not alter the response_df
    '''
    # window = get_window(analysis, flashes, omitted)

    rdf = response_df.copy()
    mdf = rdf.groupby(conditions).apply(get_mean_sem_trace)
    #mdf = mdf[['mean_response', 'sem_response', 'mean_trace', 'sem_trace', 'mean_responses']]
    mdf = mdf[['mean_response', 'sem_response', 'mean_responses']]
    mdf = mdf.reset_index()

    if ('image_name' in conditions) or ('change_image_name' in conditions):
        mdf = annotate_mean_df_with_pref_stim(mdf)

    if analysis is not None:
        raise Exception('Not Implemented yet')
        # mdf = annotate_mean_df_with_p_value(analysis, mdf, window)
        # mdf = annotate_mean_df_with_sd_over_baseline(analysis, mdf, window=window)
        # mdf = annotate_mean_df_with_time_to_peak(analysis, mdf, window=window)
        # mdf = annotate_mean_df_with_fano_factor(analysis, mdf)

    if 'p_value' in mdf.keys(): 
        fraction_significant_responses = rdf.groupby(conditions).apply(get_fraction_significant_responses)
        fraction_significant_responses = fraction_significant_responses.reset_index()
        mdf['fraction_significant_responses'] = fraction_significant_responses.fraction_significant_responses

    if flashes:
        raise Exception('Not Implemented yet')
        # These functions need p_value_baseline, and p_value_omitted, which we dont have yet
        # fraction_responsive_responses = rdf.groupby(conditions).apply(get_fraction_responsive_responses, omitted)
        # fraction_responsive_responses = fraction_responsive_responses.reset_index()
        # mdf['fraction_responsive_responses'] = fraction_responsive_responses.fraction_responsive_responses

    fraction_active_responses = rdf.groupby(conditions).apply(get_fraction_active_responses)
    fraction_active_responses = fraction_active_responses.reset_index()
    mdf['fraction_active_responses'] = fraction_active_responses.fraction_active_responses

    # Not implemented because we don't have n_events calculated
    #    fraction_nonzero_trials = rdf.groupby(conditions).apply(get_fraction_nonzero_trials)
    #    fraction_nonzero_trials = fraction_nonzero_trials.reset_index()
    #    mdf['fraction_nonzero_trials'] = fraction_nonzero_trials.fraction_nonzero_trials

    if get_reliability:
        raise Exception('Not Implemented yet')
        # I dont know what this function does
        # reliability = rdf.groupby(conditions).apply(compute_reliability, analysis, flashes, omitted)
        # reliability = reliability.reset_index()
        # mdf['reliability'] = reliability.reliability

    return mdf

def get_mean_sem_trace(group):
    '''
        Computes the average and sem of the mean_response column
    '''
    mean_response = np.mean(group['mean_response'])
    mean_responses = group['mean_response'].values
    sem_response = np.std(group['mean_response'].values) / np.sqrt(len(group['mean_response'].values))
    #mean_trace = np.mean(group['dff_trace'])
    #sem_trace = np.std(group['dff_trace'].values) / np.sqrt(len(group['dff_trace'].values))
    return pd.Series({'mean_response': mean_response, 'sem_response': sem_response,
    #                  'mean_trace': mean_trace, 'sem_trace': sem_trace,
                      'mean_responses': mean_responses})



def annotate_mean_df_with_pref_stim(mean_df):
    '''
        Calculates the preferred stimulus based on the mean_response index.
    '''
    if 'image_name' in mean_df.keys():
        image_name = 'image_name'
    else:
        image_name = 'change_image_name'
    mdf = mean_df.reset_index()
    mdf['pref_stim'] = False
    if 'cell_specimen_id' in mdf.keys():
        cell_key = 'cell_specimen_id'
    else:
        cell_key = 'cell'
    for cell in mdf[cell_key].unique():
        mc = mdf[(mdf[cell_key] == cell)]
        mc = mc[mc[image_name] != 'omitted']
        temp = mc[(mc.mean_response == np.max(mc.mean_response.values))][image_name].values
        if len(temp) > 0:
            pref_image = temp[0]
            row = mdf[(mdf[cell_key] == cell) & (mdf[image_name] == pref_image)].index
            mdf.loc[row, 'pref_stim'] = True
    return mdf


def get_fraction_significant_responses(group,threshold = 0.05):
    '''
        Calculates the fraction of trials or flashes that have a p_value below threshold
        We really need to think about multiple comparisons corrections here!
    '''
    fraction_significant_responses = len(group[group.p_value < threshold]) / float(len(group))
    return pd.Series({'fraction_significant_responses': fraction_significant_responses})


def get_fraction_active_responses(group,threshold=0.05):
    '''
        Calculates the fraction of trials of flashes, defined as a mean_response above threshold (units of df/f)
    '''
    fraction_active_responses = len(group[group.mean_response > threshold]) / float(len(group))
    return pd.Series({'fraction_active_responses': fraction_active_responses})


