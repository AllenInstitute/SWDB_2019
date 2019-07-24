from allensdk.brain_observatory.behavior.behavior_ophys_api import behavior_ophys_nwb_api as nwbapi
from allensdk.internal.api import behavior_ophys_api as boa
from allensdk.brain_observatory.behavior import behavior_ophys_session as bos

manifest = pd.read_csv('visual_behavior_data_manifest.csv')

def get_nwb_filepath(ophys_experiment_id):
    api = boa.BehaviorOphysLimsApi(ophys_experiment_id)
    nwb_path = api.get_nwb_filepath()
    return nwb_path

errors = 0
for ind_row, row in manifest.iterrows():
    try:
        nwb_filepath = get_nwb_filepath(row['ophys_experiment_id'])
        api = nwbapi.BehaviorOphysNwbApi(nwb_filepath)
        session = bos.BehaviorOphysSession(api)
        print(session.running_speed)
    except Exception:
        errors += 1
        print("error")
