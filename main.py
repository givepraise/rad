# MAIN COORDINATOR SCRIPT

# This program:
#   -Takes the Paramter JSON file
#   -Loads the data from the addresses specified there
#   -Creates object instances of every employed rewards system
#   -loops through all the specifed analysis notebook reports, sending them the necessary data objects
#       - executed notebooks get saved
#   - loops through all the specified exports
#      - the data for the exports can be sourced either from the reward object of from the analysis (maybe?)
#      - exports get saved
#   -moves all the exports + notebooks to the correct output folder
#   -cleans up

import argparse
import os
import subprocess
import json
import shutil
from pathlib import Path
from natsort import natsorted

import papermill as pm
from sources.rad_module.rewardDistribution import RewardDistribution


import sources.rad_module.rewardObjectBuilder as objBuilder
import sources.rad_module.distributionObjectBuilder as distBuilder
from sources.rad_module.rewardSystem import RewardSystem
import src.notebookbuilder as nbBuilder

# import src.exporter as exportBuilder

import sources.rad_module.imports as importer


def run_rad(_inputPath):

    ROOT_INPUT_PATH = _inputPath
    PARAMETERS_PATH = ROOT_INPUT_PATH + "parameters.json"

    ROOT_OUTPUT_PATH = ROOT_INPUT_PATH + "analysis_results/"

    NOTEBOOK_OUTPUT_PATH = ROOT_OUTPUT_PATH + "executed_notebooks/"
    REPORT_OUTPUT_PATH = ROOT_OUTPUT_PATH + "reports/"

    # create output file structure:
    Path(ROOT_OUTPUT_PATH).mkdir(parents=True, exist_ok=True)
    Path(NOTEBOOK_OUTPUT_PATH).mkdir(parents=True, exist_ok=True)
    Path(REPORT_OUTPUT_PATH).mkdir(parents=True, exist_ok=True)

    (rwdObjs, dstObjs) = importer.load_sources_from_json(PARAMETERS_PATH)

    # prepare papermill inputs

    # loop through "reports" folder
    # for each folder -> run ipynb with papermill

    # move outputs to results folder

    # /// COPIED FROM RAD CLASSIC

    # TODO: look for a way to send the exisitng objects (rwdObjs, dstObjs) instead of the path and loading it inside the nb. Will probably require a (much needed) review of the object level import/export funcs

    ### Implementation idea (since current impl leaves notebooks unopenable (though reports work!))

    # Save all te rwdObjs and distObjs in a buffer JSON
    # create list with name and type ("rwdObj / dstObj")
    # send to each notebook the path of the bufJSON and the selection of list elements detailing the objects it needs
    # each notebook calls a function in importer which takes path+list as arg and returns (rwdObjs, dstObjs)
    # notebook works normally
    # JSON gets deleted after run. If the user wants to rerun the notebook they can do importer.full_load_json(PATH) form the original paramters.json
    # (maybe we should keep the files and save them in exports?)

    rwdObjs_dicts = {}
    for rwd in rwdObjs:
        rwdObjs_dicts[rwd] = rwdObjs[rwd].export_to_dict(rwdObjs[rwd])

    dstObjs_dicts = {}
    for dst in dstObjs:
        dstObjs_dicts[dst] = dstObjs[dst].export_to_dict(dstObjs[dst])

    # prepare the parameter set we will use for analysis and the folder with the notebook templates
    analysis_params = {
        "parameters_path": PARAMETERS_PATH,
        "reward_system_objects": rwdObjs_dicts,
        "distribution_objects": dstObjs_dicts,
    }

    ANALYSIS_NOTEBOOK_FOLDER = "./reports/"

    if not os.path.isdir(ANALYSIS_NOTEBOOK_FOLDER):
        print(f"No analysis notebook path not provided, skip analysis.")
    else:
        # run all notebooks in the analysis folder
        sorted_contents = natsorted(os.listdir(ANALYSIS_NOTEBOOK_FOLDER))

        for notebook in sorted_contents:

            # make sure we only use .ipynb files
            if not (notebook.endswith(".ipynb")):
                continue

            nb_input_path = ANALYSIS_NOTEBOOK_FOLDER + notebook
            nb_destination_path = NOTEBOOK_OUTPUT_PATH + "output_" + notebook
            print(f"\n|---{notebook} :")

            pm.execute_notebook(
                nb_input_path, nb_destination_path, parameters=analysis_params
            )

            # # copy generated csv files to results folder
            # for output_csv in os.listdir():
            #     if not (output_csv.endswith(".csv")):
            #         continue
            #     csv_destination = DISTRIBUTION_OUTPUT_PATH + output_csv
            #     os.rename(output_csv, csv_destination)

            # generate HTML report
            return_buf = subprocess.run(
                "jupyter nbconvert --log-level=0 --to html --TemplateExporter.exclude_input=True %s"
                % nb_destination_path,
                shell=True,
            )

            # move it to right folder
            html_report_origin = nb_destination_path[:-6] + ".html"
            html_report_destination = (
                REPORT_OUTPUT_PATH + notebook[2:-6] + "-report.html"
            )
            os.rename(html_report_origin, html_report_destination)

    # /// END COPIED FROM RAD CLASSIC

    # TODO Future feature: specify the list of reports to run in params.json

    print("========= DONE ==========")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="RAD main script")
    parser.add_argument(
        "-p",
        "--path",
        type=str,
        required=True,
        help="Path to the folder in which we'll perform the analysis",
    )
    args = parser.parse_args()

    input_path = args.path
    # quick conveniency check
    input_path = input_path if input_path[-1] == "/" else (input_path + "/")

    run_rad(input_path)


# =============== OLD RUN_RAD FUNCTION ==============
# def run_rad(_inputPath):

#     _inputParameters = _inputPath + "/parameters.json"

#     params = {}
#     with open(_inputParameters, "r") as read_file:
#         params = json.load(read_file)

#     # change to "sources"
#     rewardsystem_objects = {}
#     for reward_system in params["sources"]:
#         # make sure the notebook finds the path to the files
#         for file in params["sources"][reward_system]["input_files"]:
#             params["sources"][reward_system]["input_files"][file] = os.path.abspath(
#                 os.path.join(
#                     input_path, params["sources"][reward_system]["input_files"][file]
#                 )
#             )

#         # create rewards Object
#         rewardsystem_objects[reward_system] = objBuilder.build_reward_object(
#             reward_system,
#             params["sources"][reward_system]["type"],
#             params["sources"][reward_system],
#         )
#         # print(rewardsystem_objects[reward_system].get_distribution_results())

#     # Create the distributions here:
#     # distribtuion_objects = {}
#     # for distribution in params["distributions"]
#     # generate each distribution using rewardsystem_objects

#     distribution_objects = {}
#     for distribution in params["distributions"]:
#         dist_sources = {}
#         for source in params["distributions"][distribution]["sources"]:
#             dist_sources[source] = rewardsystem_objects[source]

#         distribution_objects[distribution] = distBuilder.build_distribution_object(
#             distribution,
#             params["distributions"][distribution]["type"],
#             params["distributions"][distribution],
#             dist_sources,
#         )

#     print(distribution_objects)

#     # change to distribution_objects
#     for template_name in params["reports"]:
#         # add all relevant praise objects to the input and build the notebook
#         _data = {}
#         template_type = params["reports"][template_name]["type"]
#         for source_system in params["reports"][template_name]["sources"]:
#             _data[source_system] = distribution_objects[source_system]
#         nbBuilder.build_and_run(template_name, template_type, _data)

#     for export in params["exports"]:
#         _data = {}
#         for source_system in params["exports"][export]["sources"]:
#             _data[source_system] = distribution_objects[source_system]
#         exportBuilder.run_export(export, params["exports"][export], _data)

#     # [TODO] Save the different kinds of exports at different places, handle in a way that all exports are moved and you dont have to whitelist stuff

#     for output_file in os.listdir():
#         if output_file.endswith(".csv") or output_file.endswith(".md"):
#             if output_file == "README.md":
#                 pass
#             else:
#                 file_destination = _inputPath + "/my_reports/" + output_file
#                 shutil.copy(output_file, file_destination)
#                 os.remove(output_file)

#         if output_file.endswith(".html"):
#             file_destination = _inputPath + "/my_reports/" + output_file
#             shutil.copy(output_file, file_destination)
#             os.remove(output_file)

#         if output_file.endswith(".ipynb"):
#             file_destination = _inputPath + "/my_reports/" + output_file
#             shutil.copy(output_file, file_destination)
#             os.remove(output_file)

#     print("========= DONE ==========")
