####### NICK. All you need to do is add these line to save_flash_response_df.py, and add the functions below to that file.
'''
    flash_response_df = get_p_values_from_shuffle(spontaneous(session,flash_response_df)
    flash_response_df = add_image_name(session,flash_response_df)
    flash_response_df = annotate_flash_response_df_with_pref_stim(flash_response_df)
'''

def check_p_values_alignment(flash_response_df,flash_p_values):
    ''' 
        DEBUGGING FUNCTION
        Checks to make sure p values were correctly placed in flash_response_df.
        Only useful when using the OLD VERSION of get_p_values()
    '''
    for index,row in flash_response_df.iterrows():
        if not (flash_p_values.loc[index[1]][str(index[0])] == row.p_value):
            print(index)
            raise Exception('bad_alignment')

def merge_p_values_bad(flash_response_df, flash_p_values):
    '''
        DEBUGGING FUNCTION
        Merge the flash_p_values into the flash_response_df using the method in VBA.
        BUT IT IS WRONG. Included here to document that it doesnt work
    '''
    p_values = []
    for flash_number in flash_response_df.index.get_level_values(1).unique():
        p_values = p_values + list(flash_p_values.loc[flash_number, :].values)
    flash_response_df['p_value'] = p_values
    return flash_response_df


def get_p_values_from_shuffle_spontaneous_DEBUGGING(session, flash_response_df, response_window_duration=0.5,OLD_VERSION=False):
    '''
        DEBUGGING FUNCTION
        Computes the P values for each cell/flash. The P value is the probability of observing a response of that
        magnitude in the spontaneous window. The algorithm is copied from VBA
    '''
    if OLD_VERSION:
        raise Exception('Dont do this! just here for debugging later')
    # Organize Data
    fdf = flash_response_df.copy()
    st  = session.stimulus_presentations.copy()
    included_flashes = fdf.index.get_level_values(1).unique()
    st  = st[st.index.isin(included_flashes)]
    # Get Sample of Spontaneous Frames
    spontaneous_frames = get_spontaneous_frames(session)
    #  Set up Params
    ophys_frame_rate = 31
    n_mean_response_window_frames = int(np.round(response_window_duration * ophys_frame_rate, 0))
    cell_ids = np.unique(fdf.index.get_level_values(0))    
    n_cells = len(cell_ids)
    # Get Shuffled responses from spontaneous frames
    # get mean response for 10000 shuffles of the spontaneous activity frames
    # in a window the same size as the stim response window duration
    shuffled_responses = np.empty((n_cells, 10000, n_mean_response_window_frames))
    idx = np.random.choice(spontaneous_frames, 10000)
    dff_traces = np.stack(session.dff_traces.to_numpy()[:,1],axis=0)
    for i in range(n_mean_response_window_frames):
        shuffled_responses[:, :, i] = dff_traces[:, idx + i]
    shuffled_mean = shuffled_responses.mean(axis=2)
    # compare flash responses to shuffled values and make a dataframe of p_value for cell by sweep
    #flash_p_values = pd.DataFrame(index=st.index.values, columns=cell_ids.astype(str))
    interables = [cell_ids, st.index.values]
    if OLD_VERSION:
        flash_p_values = pd.DataFrame(index=st.index.values, columns=cell_ids.astype(str)) ##OLD VERSION
    else:
        flash_p_values = pd.DataFrame(index=pd.MultiIndex.from_product(interables,names= ['cell_specimen_id','flash_id']))
    for i, cell_index in enumerate(cell_ids):
        responses = fdf.loc[cell_index].mean_response.values
        null_dist_mat = np.tile(shuffled_mean[i, :], reps=(len(responses), 1))
        actual_is_less = responses.reshape(len(responses), 1) <= null_dist_mat
        p_values = np.mean(actual_is_less, axis=1)
        if OLD_VERSION:
            flash_p_values[str(cell_index)] = p_values ##OLD VERSION
        else:
            for j in range(0,len(p_values)):
                flash_p_values.at[(cell_index,j),'p_value'] = p_values[j] 
    fdf = pd.concat([fdf,flash_p_values],axis=1)
    return fdf 

def get_p_values_from_shuffle_spontaneous(session, flash_response_df, response_window_duration=0.5):
    '''
        Computes the P values for each cell/flash. The P value is the probability of observing a response of that
        magnitude in the spontaneous window. The algorithm is copied from VBA
    '''
    # Organize Data
    fdf = flash_response_df.copy()
    st  = session.stimulus_presentations.copy()
    included_flashes = fdf.index.get_level_values(1).unique()
    st  = st[st.index.isin(included_flashes)]
    # Get Sample of Spontaneous Frames
    spontaneous_frames = get_spontaneous_frames(session)
    #  Set up Params
    ophys_frame_rate = 31
    n_mean_response_window_frames = int(np.round(response_window_duration * ophys_frame_rate, 0))
    cell_ids = np.unique(fdf.index.get_level_values(0))    
    n_cells = len(cell_ids)
    # Get Shuffled responses from spontaneous frames
    # get mean response for 10000 shuffles of the spontaneous activity frames
    # in a window the same size as the stim response window duration
    shuffled_responses = np.empty((n_cells, 10000, n_mean_response_window_frames))
    idx = np.random.choice(spontaneous_frames, 10000)
    dff_traces = np.stack(session.dff_traces.to_numpy()[:,1],axis=0)
    for i in range(n_mean_response_window_frames):
        shuffled_responses[:, :, i] = dff_traces[:, idx + i]
    shuffled_mean = shuffled_responses.mean(axis=2)
    # compare flash responses to shuffled values and make a dataframe of p_value for cell by sweep
    #flash_p_values = pd.DataFrame(index=st.index.values, columns=cell_ids.astype(str))
    iterables = [cell_ids, st.index.values]
    flash_p_values = pd.DataFrame(index=pd.MultiIndex.from_product(iterables,names= ['cell_specimen_id','flash_id']))
    for i, cell_index in enumerate(cell_ids):
        responses = fdf.loc[cell_index].mean_response.values
        null_dist_mat = np.tile(shuffled_mean[i, :], reps=(len(responses), 1))
        actual_is_less = responses.reshape(len(responses), 1) <= null_dist_mat
        p_values = np.mean(actual_is_less, axis=1)
        for j in range(0,len(p_values)):
            flash_p_values.at[(cell_index,j),'p_value'] = p_values[j] 
    fdf = pd.concat([fdf,flash_p_values],axis=1)
    return fdf 

def get_spontaneous_frames(session):
    '''
        Returns a list of the frames that occur during the before and after spontaneous windows
    '''
    st = session.stimulus_presentations.copy()
    # dont use full 5 mins to avoid fingerprint and countdown
    # spont_duration_frames = 4 * 60 * 60  # 4 mins * * 60s/min * 60Hz
    spont_duration = 4 * 60  # 4mins * 60sec
    # for spontaneous at beginning of session
    behavior_start_time = st.iloc[0].start_time
    spontaneous_start_time_pre = behavior_start_time - spont_duration
    spontaneous_end_time_pre = behavior_start_time
    spontaneous_start_frame_pre = get_successive_frame_list(spontaneous_start_time_pre, session.ophys_timestamps)
    spontaneous_end_frame_pre = get_successive_frame_list(spontaneous_end_time_pre, session.ophys_timestamps)
    spontaneous_frames_pre = np.arange(spontaneous_start_frame_pre, spontaneous_end_frame_pre, 1)
    # for spontaneous epoch at end of session
    behavior_end_time = st.iloc[-1].stop_time
    spontaneous_start_time_post = behavior_end_time + 0.5
    spontaneous_end_time_post = behavior_end_time + spont_duration
    spontaneous_start_frame_post = get_successive_frame_list(spontaneous_start_time_post, session.ophys_timestamps)
    spontaneous_end_frame_post = get_successive_frame_list(spontaneous_end_time_post, session.ophys_timestamps)
    spontaneous_frames_post = np.arange(spontaneous_start_frame_post, spontaneous_end_frame_post, 1)
    # add them together
    spontaneous_frames = list(spontaneous_frames_pre) + (list(spontaneous_frames_post))
    return spontaneous_frames


def get_successive_frame_list(timepoints_array, timestamps):
    '''
        Returns the next frame after timestamps in timepoints_array
        copied from VBA
    '''
    # This is a modification of get_nearest_frame for speedup
    #  This implementation looks for the first 2p frame consecutive to the stim
    successive_frames = np.searchsorted(timestamps, timepoints_array)
    return successive_frames


def add_image_name(session,fdf):
    '''
        Adds a column to flash_response_df with the image_name taken from the stimulus_presentations table
        Slow to run
    '''
    fdf = fdf.reset_index()
    fdf = fdf.set_index('flash_id')
    fdf['image_name']= ''
    # So slow!!!
    for stim_id in np.unique(fdf.index.values):
        fdf.loc[stim_id,'image_name'] = session.stimulus_presentations.loc[stim_id].image_name
    fdf = fdf.reset_index()
    fdf = fdf.set_index(['cell_specimen_id','flash_id'])
    return fdf




def annotate_flash_response_df_with_pref_stim(fdf):
    '''
        Adds a column to flash_response_df with a boolean value of whether that flash was that cells pref image.
        Computes preferred image by looking for the image that on average evokes the largest response.
        Slow to run
    '''
    fdf = fdf.reset_index()
    if 'cell_specimen_id' in fdf.keys():
        cell_key = 'cell_specimen_id'
    else:
        cell_key = 'cell'
    fdf['pref_stim'] = False
    mean_response = fdf.groupby([cell_key, 'image_name']).apply(get_mean_sem)
    m = mean_response.unstack()
    for cell in m.index:
        temp = np.where(m.loc[cell]['mean_response'].values == np.nanmax(m.loc[cell]['mean_response'].values))[0]
        if len(temp) > 0:
            image_index = temp[0]
            pref_image = m.loc[cell]['mean_response'].index[image_index]
            trials = fdf[(fdf[cell_key] == cell) & (fdf.image_name == pref_image)].index
            fdf.loc[trials, 'pref_stim'] = True
    fdf = fdf.set_index(['cell_specimen_id','flash_id'])
    return fdf



def get_mean_sem(group):
    '''
        Returns the mean and sem of the mean_response values for all entries in the group
    '''
    mean_response = np.mean(group['mean_response'])
    sem_response = np.std(group['mean_response'].values) / np.sqrt(len(group['mean_response'].values))
    return pd.Series({'mean_response': mean_response, 'sem_response': sem_response})



