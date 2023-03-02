import boto3
import time
import datetime
from sagemaker.analytics import ExperimentAnalytics


sm = boto3.client('sagemaker')

def createExperiment(experiment_prefix, experiment_description):
    experiment_name = '{0}-{1}'.format(experiment_prefix, str(int(time.time())))
    try:
        return sm.describe_experiment(ExperimentName=experiment_name)
    except sm.exceptions.from_code('ResourceNotFound'): 
        print('Creating experiment {}'.format(experiment_name))
        sm.create_experiment(
            ExperimentName=experiment_name,
            Description=experiment_description
        )
    return experiment_name
        
def createTrial(experiment_name, trial_prefix, project_id):
    trial_name = '{0}-{1}'.format(trial_prefix, str(int(time.time())))
    print('Creating trial, {}'.format(trial_name))
    sm.create_trial(
        TrialName=trial_name,
        ExperimentName=experiment_name,
        MetadataProperties={
            'ProjectId': project_id
        }
    )
    return trial_name

def createTrialComponent(trial_name, trial_comp_prefix, project_id, file_path, training_path, validation_path, model_path, parameters):    
    trial_comp_name = '{0}-{1}'.format(trial_comp_prefix, str(int(time.time())))
    print('Creating trial component {0} for trial {1}'.format(trial_comp_name , trial_name))
    input_artifacts={
        'input_data': {
            'MediaType': 'text/csv',
            'Value': file_path
        }
    }
    output_artifacts={
        'train_data': {
            'MediaType': 'text/csv',
            'Value': training_path
        },
        'val_data': {
            'MediaType': 'text/csv',
            'Value': validation_path
        },
        'model': {
            'MediaType': 'text/plain',
            'Value': model_path
        }
    }
    sm.create_trial_component(
        TrialComponentName = trial_comp_name,
        Status={
            'PrimaryStatus': 'InProgress'
        },
        StartTime=datetime.datetime.now(),
        InputArtifacts = input_artifacts,
        OutputArtifacts= output_artifacts,
        Parameters=parameters,
        MetadataProperties={
            'ProjectId': project_id
        }
    )
    sm.associate_trial_component(
        TrialComponentName=trial_comp_name,
        TrialName=trial_name
    )
    return trial_comp_name   

def cleanup(experiment_name):
    trials = sm.list_trials(ExperimentName=experiment_name)['TrialSummaries']
    print('TrialNames:')
    for trial in trials:
        trial_name = trial['TrialName']
        print(f"\n{trial_name}")

        components_in_trial = sm.list_trial_components(TrialName=trial_name)
        print('\tTrialComponentNames:')
        for component in components_in_trial['TrialComponentSummaries']:
            component_name = component['TrialComponentName']
            print(f"\t{component_name}")
            sm.disassociate_trial_component(TrialComponentName=component_name, TrialName=trial_name)
            try:
                # comment out to keep trial components
                sm.delete_trial_component(TrialComponentName=component_name)
            except:
                # component is associated with another trial
                continue
            # to prevent throttling
            time.sleep(.5)
        sm.delete_trial(TrialName=trial_name)
    sm.delete_experiment(ExperimentName=experiment_name)
    print(f"\nExperiment {experiment_name} deleted")