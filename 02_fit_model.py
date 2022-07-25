import pyddm

import models
import loss_functions
import pandas as pd
import helper
import os


def fit_model_by_condition(subj_idx=0, loss="vincent"):
    '''
    NB: This script can (and should) be run in parallel in several different python consoles, one subject per console
    model_idx: 1 for the full model described in the paper; 2 for the model with fixed bounds; 3 for "vanilla" DDM
    subj_idx: 0 to 15 to obtain individual fits, or "all" to fit to group-averaged data
    n: number of repeated fits per condition (n>1 can be used to quickly check robustness of model fitting)
    n_training_conditions: defines how many conditions will be included in the training set (4, 8, or 9)
                            For `4`, training data for each condition (TTA, d) will be the decisions where both TTA and d
                            are different from those of the current condition. For `8`, all other conditions will be included.
    test_conditions: "all" to cross-validate model on all nine conditions, or a list of dicts with conditions for which to fit the model
    '''
    # print("Model %i, subj idx %s" % (model_no, str(subj_idx)))

    model = models.ModelDynamicDriftCollapsingBounds()

    exp_data = pd.read_csv("measures.csv")
    exp_data = exp_data[exp_data.RT<4.5]
    subjects = exp_data.subj_id.unique()

    if subj_idx == "all":
        subj_id = "all"
        subj_data = exp_data
        loss = loss_functions.LossWLSVincent if loss=="vincent" else pyddm.LossRobustBIC
    else:
        subj_id = subjects[subj_idx]
        subj_data = exp_data[(exp_data.subj_id == subj_id)]
        loss = loss_functions.LossWLS

    output_directory = "model_fit_results"

    file_name = "subj_%s_parameters_fitted.csv" % (str(subj_id))
    if not os.path.isfile(os.path.join(output_directory, file_name)):
        helper.write_to_csv(output_directory, file_name, ["subj_id", "loss"] + model.param_names, write_mode="w")

    print(subj_id)

    training_data = subj_data
    print("len(training_data): " + str(len(training_data)))

    fitted_model = helper.fit_model(model.model, training_data, loss)
    helper.write_to_csv(output_directory, file_name,
                        [subj_id, fitted_model.get_fit_result().value()]
                        + [float(param) for param in fitted_model.get_model_parameters()])

    return fitted_model


fitted_model = fit_model_by_condition(subj_idx="all", loss="robustBIC")


