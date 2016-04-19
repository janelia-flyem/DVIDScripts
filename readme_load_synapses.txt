# Create a new annotation instance the name is "annot_synapse"
curl -X POST localhost:9000/api/repo/bfaef/instance -d '{"typename": "annotation", "dataname": "annot_synapse_99"}'

# Create a sync.json file that has this in it. first value is the name of the labelbk and the second is the labelvol that you want to sync to (what is being used for production segmentation)
{ "sync": "segmentation121714,bodies121714" }
# Post the json file to sync. In this example al7sync.json is our json file
curl -X POST localhost:9000/api/node/bfaef/annot_synapse/sync --data-binary @al7sync.json

# Load the synapses
python ./load_dvid_synapses_batch.py collision_rem_annotations-synapse_2_dvid_1703-4827_6339-10088.json localhost:9000 bfaef annot_synapse dal-proof 10000 0 > bfaef_syn_load.log&
