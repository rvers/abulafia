# -*- coding: utf-8 -*-

from abulafia.actions import Forward, VerifyPolygon
from abulafia.task_specs import ImageSegmentation, TaskSequence, MulticlassVerification, FixImageSegmentation, \
    SegmentationClassification, ImageClassification
import argparse
import json
import toloka.client as toloka


# Set up the argument parser
ap = argparse.ArgumentParser()

# Add argument for input
ap.add_argument("-c", "--creds", required=True,
                help="Path to a JSON file that contains Toloka credentials. "
                     "The file should have two keys: 'token' and 'mode'. "
                     "The key 'token' should contain the Toloka API key, whereas "
                     "the key 'mode' should have the value 'PRODUCTION' or 'SANDBOX' "
                     "that defines the environment in which the pipeline should be run.")

# Parse the arguments
args = vars(ap.parse_args())

# Assign arguments to variables
cred_file = args['creds']

# Read the credentials from the JSON file
with open(cred_file) as cred_f:

    creds = json.loads(cred_f.read())
    tclient = toloka.TolokaClient(creds['token'], creds['mode'])

# Create class instances of all CrowdsourcingTasks and Actions in the pipeline

# Ask crowdsourced workers to outline objects in diagrams
outline_text = ImageSegmentation(configuration="config/outline_text_verify.yaml",
                                 client=tclient)

# Forward action
forward_detect = Forward(configuration="config/forward_verify_polygon.yaml",
                         client=tclient,
                         targets=[outline_text])

verify_polygon = VerifyPolygon(configuration="config/verify_polygon.yaml",
                               task=outline_text,
                               forward=forward_detect)

# Combine the tasks and actions into one pipeline
pipe = TaskSequence(sequence=[outline_text, verify_polygon, forward_detect],
                    client=tclient)

# Start the task sequence; create the tasks on Toloka
pipe.start()
