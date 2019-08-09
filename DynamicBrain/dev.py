import os
os.chdir('SWDB/SWDB_2019/DynamicBrain/')
import allensdk.brain_observatory.behavior.swdb.utilities as tools

from allensdk.brain_observatory.behavior.swdb import behavior_project_cache as bpc

cache_json = {'manifest_path': '/allen/programs/braintv/workgroups/nc-ophys/visual_behavior/SWDB_2019/visual_behavior_data_manifest.csv',
              'nwb_base_dir': '/allen/programs/braintv/workgroups/nc-ophys/visual_behavior/SWDB_2019/nwb_files',
              'analysis_files_base_dir': '/allen/programs/braintv/workgroups/nc-ophys/visual_behavior/SWDB_2019/extra_files'
              }
cache = bpc.BehaviorProjectCache(cache_json)

experiment_id = 792812544
session = cache.get_session(experiment_id)
tr = session.trial_response_df




def create_multi_session_mean_df(manifest,sessions,conditions=['cell_specimen_id','change_image_name'],flashes=False):
    '''
        Creates a mean response dataframe by combining multiple sessions. 
        
        manifest, the cache manifest
        Sessions, is a list of session objects to merge
        conditions is the set of conditions to send to get_mean_df() to merge. The first entry should be 'cell_specimen_id'
        flashes, if TRUE, merges the flash_response_df, otherwise merges the trial_response_df

        Returns a dataframe with index given by the session experiment ids. This allows for easy analysis like:
        mega_mdf.groupby('experiment_id').mean_response.mean()
    '''
    mega_mdf = pd.DataFrame()
    for session in sessions:
        print(session.metadata['ophys_experiment_id'])
        if flashes:
            mdf = tools.get_mean_df(session.flash_response_df,conditions=conditions)
        else:
            mdf = tools.get_mean_df(session.trial_response_df,conditions=conditions)
        mdf['experiment_id'] = session.metadata['ophys_experiment_id']
        mdf['stage_name'] = manifest[manifest.ophys_experiment_id == session.metadata['ophys_experiment_id']].stage_name.values[0]
        mega_mdf = pd.concat([mega_mdf,mdf])
    mega_mdf = mega_mdf.reset_index()
    mega_mdf = mega_mdf.set_index('experiment_id')
    mega_mdf = mega_mdf.drop(columns=['level_0','index'])
    return mega_mdf





