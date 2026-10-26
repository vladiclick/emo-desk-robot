"""Fusion script entry for the included reproducible CAD source."""
import os,sys,importlib.util
def run(context):
    folder=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','EmoComplete'))
    key='emo_complete_task'
    for name in tuple(sys.modules):
        if name==key or name.startswith(key+'.'):del sys.modules[name]
    spec=importlib.util.spec_from_file_location(key,os.path.join(folder,'EmoComplete.py'),submodule_search_locations=[folder])
    module=importlib.util.module_from_spec(spec);sys.modules[key]=module
    spec.loader.exec_module(module);module.run(context)
