import numpy as np
import random
from tqdm import tqdm
from display_codes import display, display_precomputed_error
from get_dataset import get_data
from similarities import sigmoid, tps
import pickle

def sample_eig(data, s, similarity_measure, scale=False, rankcheck=0):
    """
    input: original matrix
    output: sample eigenvalue
    """
    n = len(data)
    list_of_available_indices = range(n)
    sample_indices = np.sort(random.sample(list_of_available_indices, s))
    subsample_matrix = similarity_measure(data[sample_indices,:], data[sample_indices,:])
    all_eig_val_estimates = np.real(np.linalg.eigvals(subsample_matrix))
    all_eig_val_estimates.sort()
  
    min_eig = np.array(all_eig_val_estimates)[rankcheck]

    if scale == False:
        return min_eig
    else:
        return n*min_eig/float(s)

###########################################PARAMETERS############################################
# parameters
trials = 100
similarity_measure = "tps"
search_rank = [0,1,2,3,-4,-3,-2,-1]
max_samples = 1000
dataset_name = "kong"
# uncomment for run saved instance
# dataset_size = 5000
#################################################################################################

############################################# GRAB THE MATRICES #################################
xy, dataset_size = get_data(dataset_name)
if similarity_measure == "sigmoid":
    similarity = sigmoid
if similarity_measure == "tps":
    similarity = tps

true_mat = similarity(xy, xy)
true_spectrum = np.real(np.linalg.eigvals(true_mat))
print("loaded dataset")
print("||A||_infty:", np.max(true_mat))
#################################################################################################

################################### COMPUTE ERRORS AND EIGS #####################################
sample_eigenvalues_scaled = []
sample_eigenvalues_scaled_std = []
tracked_errors = []
tracked_errors_std = []
true_spectrum.sort()
chosen_eig = true_spectrum[search_rank]

for i in tqdm(range(10, max_samples, 10)):
    eig_vals = []
    error_vals = []
    for j in range(trials):
        # get eigenvalue
        min_eig_single_round = sample_eig(xy, i, similarity, True, \
                                      rankcheck=search_rank)
        # get error this round
        # error_single_round = np.log((min_eig_single_round - chosen_eig)**2)
        # uncomment following line for relative error
        error_single_round = np.log(np.abs(min_eig_single_round - chosen_eig) / np.abs(chosen_eig))
        # add to the local list
        eig_vals.append(min_eig_single_round)
        error_vals.append(error_single_round)
        

    # compute statistics from the local lists
    mean_min_eig = np.mean(eig_vals, 0)
    std_min_eig = np.std(eig_vals, 0)
    mean_error = np.mean(error_vals, 0)
    std_error = np.std(error_vals, 0)

    # add statistics to the global list
    sample_eigenvalues_scaled.append(mean_min_eig)
    sample_eigenvalues_scaled_std.append(std_min_eig)
    tracked_errors.append(mean_error)
    tracked_errors_std.append(std_error)

# convert to arrays
sample_eigenvalues_scaled = np.array(sample_eigenvalues_scaled)
sample_eigenvalues_scaled_std = np.array(sample_eigenvalues_scaled_std)
tracked_errors = np.array(tracked_errors)
tracked_errors_std = np.array(tracked_errors_std)

with open("pickle_files/"+dataset_name+"_"+similarity_measure+".pkl", "wb") as pickle_file:
    pickle.dump([sample_eigenvalues_scaled, sample_eigenvalues_scaled_std, \
                  tracked_errors, tracked_errors_std], pickle_file)

# # uncomment to load from pickle file only
# with open("pickle_files/"+dataset_name+"_"+similarity_measure+".pkl", "rb") as pickle_file:
#     A = pickle.load (pickle_file)
# [sample_eigenvalues_scaled, sample_eigenvalues_scaled_std, \
#                   tracked_errors, tracked_errors_std] = A

################################################################################################

for i in range(len(search_rank)):
    display(dataset_name, similarity_measure, true_spectrum, dataset_size, search_rank[i], \
        sample_eigenvalues_scaled[:,i], sample_eigenvalues_scaled_std[:,i], max_samples)
    display_precomputed_error(dataset_name, similarity_measure, tracked_errors[:,i], tracked_errors_std[:,i], \
        dataset_size, search_rank[i], max_samples)